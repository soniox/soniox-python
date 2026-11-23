from __future__ import annotations

import json
import random
import threading
import time
from collections.abc import Callable, Iterator
from types import TracebackType
from typing import TYPE_CHECKING

from websockets.exceptions import (
    ConnectionClosed,
    InvalidStatus,
    WebSocketException,
)
from websockets.sync.client import connect as sync_ws_connect

from ..errors import SonioxRealtimeError, SonioxValidationError
from ..types.realtime import RealtimeControlType, RealtimeEvent, RealtimeSTTConfig
from ._reconnect import (
    CLOSE_DIAL_TIMEOUT_SEC,
    MAX_RESUMES_WITHOUT_A_FRAME,
    PING_INTERVAL_SEC,
    RECONNECT_REPLY_TIMEOUT_SEC,
    Ending,
    Reconnect,
)
from ._utils import (
    DEFAULT_CONNECT_TIMEOUT_SEC,
    DEFAULT_IDLE_TIMEOUT_MS,
    KEEP_ALIVE_INTERVAL_SEC,
    KeepaliveThread,
    auth_headers,
    validate_connect_timeout_sec,
)

if TYPE_CHECKING:
    from ..client import SonioxClient


class RealtimeSTTSession:
    """
    Synchronous WebSocket session for a single real-time speech-to-text stream.

    This class manages the full lifecycle of a real-time transcription session:
    connecting to the WebSocket endpoint, streaming audio data, receiving events,
    and gracefully closing the stream. A session is stateful and represents
    exactly one streaming interaction with the Soniox realtime API.

    Instances are designed to be used as context managers.
    """

    def __init__(
        self,
        url: str,
        config: RealtimeSTTConfig,
        api_key: str,
        *,
        connect_timeout_sec: float = DEFAULT_CONNECT_TIMEOUT_SEC,
    ) -> None:
        """
        Create a new realtime STT session.

        This does not open a network connection. The WebSocket connection
        is established when entering the context manager.

        Args:
            url:
                WebSocket URL for the realtime transcription endpoint.
            config:
                Configuration describing the audio format and transcription
                behavior for this session.
            api_key:
                API key sent on the WebSocket handshake.
            connect_timeout_sec:
                Maximum seconds to wait for the WebSocket handshake to
                complete. Defaults to 10 seconds.
        """
        self._url = url
        self._config = config
        self._api_key = api_key
        self._connect_timeout_sec = connect_timeout_sec
        self._ws = None
        self._last_message: RealtimeEvent | None = None
        self._paused = False
        self._keepalive: KeepaliveThread | None = None
        # Whether the end-of-audio message has gone out.
        self._audio_ended = False
        self._over: Ending | None = None
        # Private so a caller on a strange network can set it before entering.
        self._idle_timeout_sec = (config.idle_timeout_ms or DEFAULT_IDLE_TIMEOUT_MS) / 1000
        self._ping_interval_sec = min(self._idle_timeout_sec / 4, PING_INTERVAL_SEC)
        self._reconnect = Reconnect() if config.enable_reconnect else None
        self._ping: KeepaliveThread | None = None
        # Held while sending and while continuing the stream, so no message reaches
        # connection without being recorded for the resend.
        self._lock = threading.Lock()

    @property
    def config(self) -> RealtimeSTTConfig:
        """
        Return the configuration used to initialize this session.
        """
        return self._config

    @property
    def paused(self) -> bool:
        """Return True if the session is currently paused."""
        return self._paused

    def __enter__(self) -> RealtimeSTTSession:
        """
        Open the WebSocket connection and start the realtime session.

        The session configuration is sent immediately after connecting.
        If any step fails, the connection is closed and a
        SonioxRealtimeError is raised.

        Returns:
            The active realtime session instance.

        Raises:
            SonioxRealtimeError:
                If the WebSocket connection or session initialization fails.
        """
        try:
            self._ws = sync_ws_connect(
                self._url,
                open_timeout=self._connect_timeout_sec,
                additional_headers=auth_headers(self._api_key),
            )
        except TimeoutError as exc:
            raise SonioxRealtimeError("Connection timed out") from exc
        except Exception as exc:
            raise SonioxRealtimeError("Failed to start realtime session") from exc

        try:
            self._ws.send(json.dumps(self._config.model_dump(exclude_none=True)))
            if self._reconnect is not None:
                # Reconnect needs pings: they notice a drop in seconds, and their
                # pongs are what lets the resend log be dropped as it is confirmed.
                self._ping = KeepaliveThread(self._send_ping, self._ping_interval_sec)
                self._ping.start()
            return self
        except Exception as exc:
            if self._ws:
                try:
                    self._ws.close()
                except Exception:
                    pass
                self._ws = None
            raise SonioxRealtimeError("Failed to start realtime session") from exc

    def __exit__(
        self,
        _exc_type: type[BaseException] | None,
        _exc_value: BaseException | None,
        _traceback: TracebackType | None,
    ) -> None:
        """
        Close the realtime session and release network resources.

        This method is called automatically when exiting the
        context manager.
        """
        _ = (_exc_type, _exc_value, _traceback)  # To make linter happy.
        self.close()

    def close(self) -> None:
        """
        Close the realtime session and release the WebSocket.

        Signals end-of-audio to the server and clears the underlying
        connection. Subsequent calls are no-ops.

        Called automatically when exiting the context manager.
        """
        if self._over is None:
            self._over = Ending.CLOSING
        if self._ping is not None:
            self._ping.stop()
            self._ping = None
        if self._keepalive is not None:
            self._keepalive.stop()
            self._keepalive = None
        self._paused = False
        if not self._ws:
            self._end_a_stream_with_no_socket()
            return
        if self._over is Ending.TAKEN:
            # A close frame here could reach the server as the end of a stream
            # the newer connection is still using.
            self._drop_socket()
            return
        try:
            if not self._audio_ended:
                # `finish()` already said so; saying it twice is a second
                # message the server counts and would be resent on a reconnect.
                self._end_audio()
                self._ws.send("")
        except Exception:
            pass
        finally:
            ws, self._ws = self._ws, None
        # The 1000 is what tells the server the stream is over. Without it the
        # stream waits out its idle timeout, billed, holding a slot.
        try:
            ws.close()
        except Exception:
            pass
        self._over = Ending.ENDED

    def send_byte_chunk(self, chunk: bytes) -> None:
        """
        Send a single chunk of raw audio bytes to the realtime stream.

        The audio data must match the format declared in the session
        configuration (sample rate, channels, encoding).

        Args:
            chunk:
                Raw audio bytes to send.

        Raises:
            SonioxRealtimeError:
                If the session is not connected or the send operation fails.
        """
        self._require_stream()
        if self._paused:
            return
        try:
            self._send(chunk)
        except Exception as exc:
            raise SonioxRealtimeError("Failed to send audio chunk") from exc

    def send_bytes(self, chunks: bytes | Iterator[bytes], *, finish: bool = True) -> None:
        """
        Send audio data to the realtime stream.

        Accepts either a single bytes object or an iterator yielding byte
        chunks (e.g. from `throttle_audio`). If `finish=True` (the default),
        an end-of-audio signal is sent after the last chunk; pass
        `finish=False` when you intend to send more audio later in the
        same session.

        Args:
            chunks: Raw bytes or an iterator of byte chunks.
            finish: If True (default), signal end-of-audio after the last chunk.
        """
        if isinstance(chunks, bytes):
            self.send_byte_chunk(chunks)
            return

        for chunk in chunks:
            self.send_byte_chunk(chunk)

        if finish:
            self.finish()

    def send_control_message(self, control_type: RealtimeControlType) -> None:
        """
        Send a control message to the realtime session.

        Control messages modify the state of the stream, such as signaling
        end-of-audio or requesting finalization.

        Args:
            control_type:
                The type of control message to send.

        Raises:
            SonioxRealtimeError:
                If the session is not connected or the message cannot be sent.
        """
        self._require_stream()
        try:
            if control_type == RealtimeControlType.FINISH:
                if self._audio_ended:
                    # The server counts the empty frame, so a second one is a
                    # second message - resent as well, on a reconnect.
                    return
                self._end_audio()
                self._send("")
            elif control_type == RealtimeControlType.KEEP_ALIVE:
                self._send(json.dumps({"type": "keepalive"}))
            elif control_type == RealtimeControlType.FINALIZE:
                self._send(json.dumps({"type": "finalize"}))
        except Exception as exc:
            raise SonioxRealtimeError("Failed to send control message") from exc

    def finish(self) -> None:
        """
        Signal end-of-audio.

        The server finalizes any pending tokens and closes the
        connection. Continue iterating `receive_events()` to consume
        the remaining tokens.
        """
        self.send_control_message(RealtimeControlType.FINISH)

    def keep_alive(self) -> None:
        """
        Send a keep-alive message to prevent the session from timing out.
        """
        self.send_control_message(RealtimeControlType.KEEP_ALIVE)

    def finalize(self) -> None:
        """
        Finalize all outstanding non-final tokens while keeping the session open.

        Subsequent tokens will be delivered with `is_final=True`.
        """
        self.send_control_message(RealtimeControlType.FINALIZE)

    def send_agent_text(self, text: str, *, end_of_segment: bool = False) -> None:
        """
        Send text your agent is speaking, so Soniox recognizes those words when
        the user says them back.

        Soniox places the text by its position among the audio frames, so send
        each piece a little before the caller hears it - 500ms to 1s ahead of
        playback - paced by how much of the reply has actually been played, not
        by how fast the model or the Text-to-Speech produced it.

        A segment is one agent turn. Close every turn with
        `end_of_segment=True`, either on the last piece of text or on its own.
        Do the same when the caller interrupts: send whatever was already
        played, close the segment, and drop the rest of the reply.

        Args:
            text: The next piece of what the agent is saying, spaces included -
                Soniox joins the pieces exactly as sent. May be empty.
            end_of_segment: Whether the agent's turn ends here.

        Raises:
            SonioxValidationError:
                If the session config left `enable_agent_text_input` unset.
            SonioxRealtimeError:
                If the session is not connected or the message cannot be sent.
        """
        if not self._config.enable_agent_text_input:
            raise SonioxValidationError(
                "Set enable_agent_text_input on the session config to send agent text"
            )
        self._require_stream()
        try:
            self._send(
                json.dumps({"type": "agent_text", "text": text, "end_of_segment": end_of_segment})
            )
        except Exception as exc:
            raise SonioxRealtimeError("Failed to send agent text") from exc

    def recv_bytes(self) -> bytes:
        """
        Receive a raw message from the WebSocket connection.

        Reconnect belongs to `receive_event`, which records the token the
        server sends: a session driven through it replaces a lost connection
        here, so this only returns empty once the stream itself is over, and a
        continued stream returns the server's `reconnected` message. Called alone
        this is the plain socket and a drop ends the stream, because nothing
        recorded the token. The token message and the pongs come through as
        they are; `receive_event` is what keeps those to itself.

        Returns:
            The received message as bytes. An empty bytes object indicates
            that the connection has been closed.

        Raises:
            SonioxRealtimeError:
                If the session is not connected, or if the connection dropped
                and the stream could not be continued.
        """
        socket = self._ws
        if socket is None:
            raise SonioxRealtimeError("Realtime session is not connected")
        state = self._reconnect
        if state is None:
            try:
                message = socket.recv()
            except ConnectionClosed:
                return b""
            return message.encode("utf-8") if isinstance(message, str) else message

        while True:
            ws = self._ws
            if ws is None:
                # `close()` took the socket while this read was waiting.
                return b""
            try:
                # The wait is bounded so a silent drop, which arrives as nothing
                # at all, is noticed by the ping that went unanswered.
                message = ws.recv(timeout=self._ping_interval_sec)
            except TimeoutError:
                with self._lock:
                    # The ping thread is writing the log this reads.
                    overdue = state.pong_overdue(self._ping_interval_sec)
                if not overdue:
                    continue
                if self._over is None and not self._can_resume():
                    # A ping of a live stream went unanswered and there is no
                    # taking this one over. Ending the caller's loop here would
                    # read as a stream that finished, which it has not.
                    self._over = Ending.ENDED
                    raise SonioxRealtimeError(
                        "The connection was lost: a ping went unanswered"
                    ) from None
                return self._continue_stream() or b""
            except ConnectionClosed:
                # Including a close the library calls OK: a server going
                # away closes with 1001 and the stream is still there. Only
                # a terminal frame ends it, and then there is nothing to take
                # over and `_continue_stream` says so.
                return self._continue_stream() or b""
            # A frame is the proof of life the window is counted from.
            state.heard_from_server()
            return message.encode("utf-8") if isinstance(message, str) else message

    def parse_event(self, raw: str | bytes) -> RealtimeEvent:
        """
        Parse a raw WebSocket message into a structured realtime event.

        Args:
            raw:
                Raw message payload received from the server.

        Returns:
            A validated RealtimeEvent instance.
        """
        return RealtimeEvent.validate_event(raw)

    @property
    def last_message(self) -> RealtimeEvent | None:
        """
        Return the most recently received realtime event, if any.
        """
        return self._last_message

    def receive_event(self) -> RealtimeEvent | None:
        """
        Receive and parse the next realtime event from the server.

        Returns:
            The next RealtimeEvent, or None if the connection has closed.

        Raises:
            SonioxRealtimeError:
                If the session was never connected.
        """
        if self._ws is None:
            if self._over is not None:
                return None
            raise SonioxRealtimeError("Realtime session is not connected")
        while True:
            raw = self.recv_bytes()
            if not raw:
                return None
            event = self.parse_event(raw)
            if self._reconnect is not None and not self._for_caller(event):
                continue
            self._last_message = event
            return event

    def receive_events(self) -> Iterator[RealtimeEvent]:
        """
        Yield realtime events as they are received from the server.

        Iteration stops automatically when the connection is closed.
        """
        while True:
            event = self.receive_event()
            if event is None:
                break
            yield event

    def handle_events(self, handler: Callable[[RealtimeEvent], None]) -> None:
        """
        Receive realtime events and dispatch them to a handler callback.

        Args:
            handler:
                Callable invoked for each received RealtimeEvent.
        """
        for event in self.receive_events():
            handler(event)

    def _end_a_stream_with_no_socket(self) -> None:
        """
        End a stream that has no connection left to end it on.

        Closing while the stream is being continued leaves nothing to say it is
        over on, and a stream nobody ends waits out its idle timeout - billed on
        wall clock, and holding a concurrent request slot the whole time. So it
        is continued once more, briefly, to be closed properly. Best effort:
        the stream times out on its own if this does not get through.
        """
        state = self._reconnect
        # Not `_can_resume`: closing is itself an ending, and this is the one
        # ending that leaves a stream out there worth reaching to end.
        if state is None or state.url is None or self._over is not Ending.CLOSING:
            return
        url = state.url
        assert url is not None
        try:
            ws = sync_ws_connect(
                url,
                open_timeout=CLOSE_DIAL_TIMEOUT_SEC,
                additional_headers=auth_headers(self._api_key),
            )
        except Exception:
            return
        try:
            ws.send(
                json.dumps(
                    {
                        "type": "reconnect",
                        "reconnect_token": state.token,
                        "last_seq": state.last_seq,
                    }
                )
            )
            ws.recv(timeout=CLOSE_DIAL_TIMEOUT_SEC)
        except Exception:
            pass
        try:
            ws.close()
        except Exception:
            pass
        self._over = Ending.ENDED

    def _can_resume(self) -> bool:
        """Whether a dropped stream may be continued on a new connection."""
        state = self._reconnect
        return state is not None and state.url is not None and self._over is None

    def _end_audio(self) -> None:
        """Remember the end of audio has gone out, so it is not sent twice."""
        # The stream is not over yet: the server runs on to its final results,
        # and a connection lost in that window can still be continued. Only a
        # `finished` or an error frame ends it, which `_for_caller` records.
        self._audio_ended = True

    def _require_stream(self) -> None:
        """
        Refuse work on a session with nowhere for its messages to go.

        A session taking the stream over has no socket for a moment, but its
        messages are kept and sent again once it has one, so it is not
        disconnected.
        """
        if self._over in (Ending.ENDED, Ending.TAKEN):
            # Without this the send is recorded for a resend that never comes.
            raise SonioxRealtimeError("The realtime stream has ended")
        if self._over is not None or (self._ws is None and not self._can_resume()):
            raise SonioxRealtimeError("Realtime session is not connected")

    def _send(self, payload: str | bytes) -> None:
        """
        Send a message the server counts, keeping it until a pong confirms it.

        A dropped connection is not an error here: the message stays in the
        resend log and goes out again once the stream is continued.
        """
        if self._reconnect is None:
            if self._ws is None:
                raise SonioxRealtimeError("Realtime session is not connected")
            self._ws.send(payload)
            return
        with self._lock:
            self._reconnect.record(payload)
            if self._ws is None:
                return
            try:
                self._ws.send(payload)
            except ConnectionClosed:
                pass

    def _send_ping(self) -> None:
        """Ping, so a lost connection is noticed and the resend log stays short."""
        state = self._reconnect
        if state is None:
            return
        with self._lock:
            payload = state.ping()
            ws = self._ws
        if ws is None:
            return
        try:
            ws.send(payload)
        except Exception:
            # Nothing to do about it here; the missing pong is the signal.
            pass

    def _continue_stream(self) -> bytes | None:
        """
        Continue the stream on a new connection.

        Returns:
            The server's `reconnected` message, which goes on to the caller so
            it knows the stream dropped, or None if the stream ended rather
            than dropped, which is the caller's end of the events.

        Raises:
            SonioxRealtimeError:
                If the stream was still there to continue but could not be.
        """
        state = self._reconnect
        if state is None or not self._can_resume():
            return None
        url = state.url
        assert url is not None
        self._drop_socket()

        # The server's window already runs from the last message it got, which
        # on a silent drop is a ping and a pong before we noticed.
        deadline = state.acked_at + self._idle_timeout_sec
        delay = 0.25
        while time.monotonic() < deadline:
            if self._over is not None:
                return None  # Nothing left to continue for.
            if state.resumes_without_a_frame >= MAX_RESUMES_WITHOUT_A_FRAME:
                # Every success hands back a new token and a new window, so
                # nothing in the protocol would ever stop this.
                self._over = Ending.ENDED
                raise SonioxRealtimeError(
                    "The stream could not be continued: it was continued "
                    f"{MAX_RESUMES_WITHOUT_A_FRAME} times with no response from the server"
                )
            # An attempt gets half of what is left, so one that hangs on a
            # unanswered dial cannot eat the whole window and leave no
            # second try.
            attempt_ends = min(
                time.monotonic() + max((deadline - time.monotonic()) / 2, 1.0), deadline
            )
            continued = self._dial_once(url, state, attempt_ends)
            if continued is not None:
                return continued
            if self._over is not None:
                return None  # Closed, or taken over, while that attempt ran.
            # Equal jitter, so clients dropped at the same moment do not
            # all dial again together.
            time.sleep(
                min(
                    delay / 2 + random.random() * delay / 2,
                    max(deadline - time.monotonic(), 0.0),
                )
            )
            delay = min(delay * 2, 2.0)

        self._over = Ending.ENDED
        raise SonioxRealtimeError("The stream was not continued before its window closed")

    def _dial_once(self, url: str, state: Reconnect, attempt_ends: float) -> bytes | None:
        """
        Present the token on one new connection, and adopt it if it is accepted.

        Args:
            url:
                Where to continue the stream, as the server gave it.
            state:
                The stream's bookkeeping. Its token goes out and its resend log
                goes out behind it.
            attempt_ends:
                When this attempt's share of the reconnect window runs out.

        Returns:
            The server's `reconnected` message, which goes on to the caller so
            it knows the stream dropped, or None to say the stream is still
            there and worth another attempt. None with an ending recorded means
            stop: the session was closed, or a newer connection has the stream.

        Raises:
            SonioxRealtimeError:
                If the stream cannot be continued at all.
        """
        ws = None
        try:
            ws = sync_ws_connect(
                url,
                open_timeout=min(
                    self._connect_timeout_sec,
                    max(attempt_ends - time.monotonic(), 0.1),
                ),
                additional_headers=auth_headers(self._api_key),
            )
            ws.send(
                json.dumps(
                    {
                        "type": "reconnect",
                        "reconnect_token": state.token,
                        "last_seq": state.last_seq,
                    }
                )
            )
            raw = ws.recv(
                timeout=min(
                    RECONNECT_REPLY_TIMEOUT_SEC,
                    max(attempt_ends - time.monotonic(), 0.1),
                )
            )
        except (OSError, TimeoutError, WebSocketException) as exc:
            if isinstance(exc, InvalidStatus) and exc.response.status_code < 500:
                # A 5xx is the way in being down, not a refusal, so that one
                # is tried again. `InvalidStatus` subclasses `InvalidHandshake`.
                self._over = Ending.ENDED
                raise SonioxRealtimeError(f"The stream could not be continued: {exc}") from exc
            if ws is not None:
                # The connection is open and will stay open: nothing else holds
                # it, and the server counts it against our limit.
                ws.close_socket()
            return None

        try:
            reply = self.parse_event(raw)
        except Exception:
            # Something in the way answering with a page, not the server:
            # the same as a 5xx, and worth another dial.
            ws.close_socket()
            return None

        if reply.error_type == "connection_replaced":
            # The stream is not over, so this socket is dropped rather than
            # closed, and nothing dials again.
            ws.close_socket()
            self._over = Ending.TAKEN
            return raw.encode("utf-8") if isinstance(raw, str) else raw

        if reply.type != "reconnected" or not reply.reconnect_token or reply.last_request is None:
            # No count means no telling what the server has, and it
            # transcribes resent audio again rather than noticing.
            ws.close_socket()
            self._over = Ending.ENDED
            raise SonioxRealtimeError(reply.error_message or "The stream could not be continued")

        with self._lock:
            if self._over is not None:
                # This connection has the stream, so closing it ends it.
                ws.close()
                return None
            resend = state.resend_after(reply.last_request, reply.reconnect_token)
            self._ws = ws
            try:
                for message in resend:
                    ws.send(message)
            except (OSError, WebSocketException):
                # The log is untouched, so the next read continues again.
                pass
        return raw.encode("utf-8") if isinstance(raw, str) else raw

    def _drop_socket(self) -> None:
        """
        Abandon the connection without a close frame.

        A normal close ends the stream; the server closes this connection itself
        once the new one has continued the stream.
        """
        with self._lock:
            ws, self._ws = self._ws, None
        if ws is not None:
            try:
                ws.close_socket()
            except Exception:
                pass

    def _for_caller(self, event: RealtimeEvent) -> bool:
        """
        Take what the reconnect protocol needs from an event, and say whether
        anything is left for the caller.

        Returns:
            False for the messages the protocol answers itself - the token it
            is given, and the pongs - which the caller never sees.
        """
        state = self._reconnect
        assert state is not None
        if event.type == "reconnect":
            state.token, state.url = event.reconnect_token, event.reconnect_url
            # A ping sent before the stream started is answered once it does,
            # so the wait for a pong starts here, not at the start request.
            with self._lock:
                state.clear_pings()
            return False
        if event.type == "pong":
            with self._lock:
                state.pong(event.id)
            return False
        if event.type == "reconnected":
            # The token is ours to present, not the caller's to hold.
            event.reconnect_token = None
            return True
        if event.error_type == "connection_replaced":
            self._over = Ending.TAKEN
            return True
        if (
            (event.error_code is not None and event.error_code != 0)
            or event.error_message is not None
            or event.finished
        ):
            # A message with no code is an error all the same, and dialling
            # for a stream that has ended only wastes the window.
            self._over = Ending.ENDED
            return True
        if event.seq is not None:
            if event.seq <= state.last_seq:
                return False  # Sent again after a reconnect, already delivered.
            state.last_seq = event.seq
        return True

    def pause(self, *, finalize: bool = True) -> None:
        """
        Pause the session, suppressing outgoing audio and starting a
        background keepalive thread.

        While paused, calls to `send_byte_chunk` are silently dropped.
        A background thread sends a keepalive message every
        ``KEEP_ALIVE_INTERVAL_SEC`` seconds to prevent the server from
        timing out the session.

        Calling `pause` on an already-paused session is a no-op.

        Args:
            finalize: If True (default), call `finalize()` before pausing.

        Raises:
            SonioxRealtimeError: If the session is not connected.
        """
        self._require_stream()
        if self._paused:
            return
        if finalize:
            self.finalize()
        self._paused = True
        if self._ping is None:
            # A ping already holds the stream open, so a session that pings
            # needs no keepalive beside it.
            self._keepalive = KeepaliveThread(self.keep_alive, KEEP_ALIVE_INTERVAL_SEC)
            self._keepalive.start()

    def resume(self) -> None:
        """
        Resume a paused session, stopping the keepalive thread and
        allowing audio to be sent again.

        Calling `resume` on a session that is not paused is a no-op.

        Raises:
            SonioxRealtimeError: If the session is not connected.
        """
        self._require_stream()
        if not self._paused:
            return
        if self._keepalive is not None:
            self._keepalive.stop()
            self._keepalive = None
        self._paused = False

    enter = __enter__


class RealtimeSTTClient:
    """
    Factory for creating synchronous realtime speech-to-text sessions.

    This class validates credentials and prepares session configuration,
    but does not itself manage WebSocket connections.
    """

    def __init__(self, client: SonioxClient) -> None:
        """
        Create a realtime STT client bound to an existing API client.

        Args:
            client:
                Parent Soniox client providing configuration and credentials.
        """
        self._client = client

    def connect(
        self,
        *,
        config: RealtimeSTTConfig,
        api_key: str | None = None,
        connect_timeout_sec: float = DEFAULT_CONNECT_TIMEOUT_SEC,
    ) -> RealtimeSTTSession:
        """
        Create a new realtime STT session.

        The returned session is not connected until entered as a
        context manager.

        Args:
            config:
                Realtime transcription configuration.
            api_key:
                Optional API key override. If not provided, the client's
                default API key is used.
            connect_timeout_sec:
                Maximum seconds to wait for the WebSocket handshake.
                Defaults to 10 seconds.

        Returns:
            A new RealtimeSTTSession instance.

        Raises:
            SonioxValidationError:
                If no API key is available.
        """
        key = api_key or self._client.api_key
        if not key:
            raise SonioxValidationError("API key is required to start a realtime session")

        timeout_sec = validate_connect_timeout_sec(connect_timeout_sec)

        return RealtimeSTTSession(
            self._client.websocket_base_url,
            config,
            key,
            connect_timeout_sec=timeout_sec,
        )
