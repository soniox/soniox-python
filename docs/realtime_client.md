---
title: "Realtime Client"
description: "Soniox Python SDK - Realtime Client Reference"
keywords: "RealtimeAPI, AsyncRealtimeAPI, RealtimeSTTClient, AsyncRealtimeSTTClient, RealtimeSTTSession, AsyncRealtimeSTTSession, RealtimeTTSClient, AsyncRealtimeTTSClient, RealtimeTTSConnection, AsyncRealtimeTTSConnection, RealtimeTTSMultiplexedConnection, AsyncRealtimeTTSMultiplexedConnection, RealtimeTTSStream, AsyncRealtimeTTSStream"
---

---

## RealtimeAPI

Entrypoint for realtime helpers on SonioxClient.

<a id="realtimeapi-constructor"></a>

### Constructor

```python
RealtimeAPI(client: SonioxClient)
```

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `client` | `SonioxClient` | Soniox client instance. |

**Returns**

`None`

<a id="realtimeapi-properties"></a>

### Properties

| Property | Type | Description |
| ------ | ------ | ------ |
| `stt` | `RealtimeSTTClient` | Speech-to-text API namespace. |
| `tts` | `RealtimeTTSClient` | Text-to-Speech API namespace |

---

## AsyncRealtimeAPI

Entrypoint for async realtime helpers on AsyncSonioxClient.

<a id="asyncrealtimeapi-constructor"></a>

### Constructor

```python
AsyncRealtimeAPI(client: AsyncSonioxClient)
```

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `client` | `AsyncSonioxClient` | Soniox client instance. |

**Returns**

`None`

<a id="asyncrealtimeapi-properties"></a>

### Properties

| Property | Type | Description |
| ------ | ------ | ------ |
| `stt` | `AsyncRealtimeSTTClient` | Speech-to-text API namespace. |
| `tts` | `AsyncRealtimeTTSClient` | Text-to-Speech API namespace |

---

## RealtimeSTTClient

Factory for creating synchronous realtime speech-to-text sessions.

This class validates credentials and prepares session configuration,
but does not itself manage WebSocket connections.

<a id="realtimesttclient-constructor"></a>

### Constructor

```python
RealtimeSTTClient(client: SonioxClient)
```

Create a realtime STT client bound to an existing API client.

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `client` | `SonioxClient` | Parent Soniox client providing configuration and credentials. |

**Returns**

`None`

<a id="realtimesttclient-connect"></a>

### connect()

```python
connect(*, config: RealtimeSTTConfig, api_key: str | None = None, connect_timeout_sec: float = DEFAULT_CONNECT_TIMEOUT_SEC) -> RealtimeSTTSession
```

Create a new realtime STT session.

The returned session is not connected until entered as a
context manager.

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `config` | `RealtimeSTTConfig` | Realtime transcription configuration. |
| `api_key` | `str \| None` | Optional API key override. If not provided, the client's default API key is used. |
| `connect_timeout_sec` | `float` | Maximum seconds to wait for the WebSocket handshake. Defaults to 10 seconds. |

**Returns**

`RealtimeSTTSession`

A new RealtimeSTTSession instance.

**Raises**

- `SonioxValidationError` If no API key is available.

---

## AsyncRealtimeSTTClient

Factory for creating asynchronous realtime speech-to-text sessions.

This class validates credentials and prepares session configuration,
but does not itself manage WebSocket connections.

<a id="asyncrealtimesttclient-constructor"></a>

### Constructor

```python
AsyncRealtimeSTTClient(client: AsyncSonioxClient)
```

Create a realtime STT client bound to an existing API client.

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `client` | `AsyncSonioxClient` | Parent Soniox client providing configuration and credentials. |

**Returns**

`None`

<a id="asyncrealtimesttclient-connect"></a>

### connect()

```python
connect(*, config: RealtimeSTTConfig, api_key: str | None = None, connect_timeout_sec: float = DEFAULT_CONNECT_TIMEOUT_SEC) -> AsyncRealtimeSTTSession
```

Create a new realtime STT session.

The returned session is not connected until entered as an async
context manager.

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `config` | `RealtimeSTTConfig` | Realtime transcription configuration. |
| `api_key` | `str \| None` | Optional API key override. If not provided, the client's default API key is used. |
| `connect_timeout_sec` | `float` | Maximum seconds to wait for the WebSocket handshake. Defaults to 10 seconds. |

**Returns**

`AsyncRealtimeSTTSession`

A new AsyncRealtimeSTTSession instance.

**Raises**

- `SonioxValidationError` If no API key is available.

---

## RealtimeSTTSession

Synchronous WebSocket session for a single real-time speech-to-text stream.

This class manages the full lifecycle of a real-time transcription session:
connecting to the WebSocket endpoint, streaming audio data, receiving events,
and gracefully closing the stream. A session is stateful and represents
exactly one streaming interaction with the Soniox realtime API.

Instances are designed to be used as context managers.

<a id="realtimesttsession-constructor"></a>

### Constructor

```python
RealtimeSTTSession(url: str, config: RealtimeSTTConfig, *, connect_timeout_sec: float = DEFAULT_CONNECT_TIMEOUT_SEC)
```

Create a new realtime STT session.

This does not open a network connection. The WebSocket connection
is established when entering the context manager.

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `url` | `str` | WebSocket URL for the realtime transcription endpoint. |
| `config` | `RealtimeSTTConfig` | Configuration describing the audio format and transcription behavior for this session. |
| `connect_timeout_sec` | `float` | Maximum seconds to wait for the WebSocket handshake to complete. Defaults to 10 seconds. |

**Returns**

`None`

<a id="realtimesttsession-properties"></a>

### Properties

| Property | Type | Description |
| ------ | ------ | ------ |
| `config` | `RealtimeSTTConfig` | Return the configuration used to initialize this session. |
| `paused` | `bool` | Return True if the session is currently paused. |
| `last_message` | `RealtimeEvent \| None` | Return the most recently received realtime event, if any. |

<a id="realtimesttsession-close"></a>

### close()

```python
close() -> None
```

Close the realtime session and release the WebSocket.

Signals end-of-audio to the server and clears the underlying
connection. Subsequent calls are no-ops.

Called automatically when exiting the context manager.

**Returns**

`None`

***

<a id="realtimesttsession-send_byte_chunk"></a>

### send_byte_chunk()

```python
send_byte_chunk(chunk: bytes) -> None
```

Send a single chunk of raw audio bytes to the realtime stream.

The audio data must match the format declared in the session
configuration (sample rate, channels, encoding).

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `chunk` | `bytes` | Raw audio bytes to send. |

**Returns**

`None`

**Raises**

- `SonioxRealtimeError` If the session is not connected or the send operation fails.

***

<a id="realtimesttsession-send_bytes"></a>

### send_bytes()

```python
send_bytes(chunks: bytes | Iterator[bytes], *, finish: bool = True) -> None
```

Send audio data to the realtime stream.

Accepts either a single bytes object or an iterator yielding byte
chunks (e.g. from `throttle_audio`). If `finish=True` (the default),
an end-of-audio signal is sent after the last chunk; pass
`finish=False` when you intend to send more audio later in the
same session.

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `chunks` | `bytes \| Iterator[bytes]` | Raw bytes or an iterator of byte chunks. |
| `finish` | `bool` | If True (default), signal end-of-audio after the last chunk. |

**Returns**

`None`

***

<a id="realtimesttsession-send_control_message"></a>

### send_control_message()

```python
send_control_message(control_type: RealtimeControlType) -> None
```

Send a control message to the realtime session.

Control messages modify the state of the stream, such as signaling
end-of-audio or requesting finalization.

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `control_type` | `RealtimeControlType` | The type of control message to send. |

**Returns**

`None`

**Raises**

- `SonioxRealtimeError` If the session is not connected or the message cannot be sent.

***

<a id="realtimesttsession-finish"></a>

### finish()

```python
finish() -> None
```

Signal end-of-audio.

The server finalizes any pending tokens and closes the
connection. Continue iterating `receive_events()` to consume
the remaining tokens.

**Returns**

`None`

***

<a id="realtimesttsession-keep_alive"></a>

### keep_alive()

```python
keep_alive() -> None
```

Send a keep-alive message to prevent the session from timing out.

**Returns**

`None`

***

<a id="realtimesttsession-finalize"></a>

### finalize()

```python
finalize() -> None
```

Finalize all outstanding non-final tokens while keeping the session open.

Subsequent tokens will be delivered with `is_final=True`.

**Returns**

`None`

***

<a id="realtimesttsession-recv_bytes"></a>

### recv_bytes()

```python
recv_bytes() -> bytes
```

Receive a raw message from the WebSocket connection.

**Returns**

`bytes`

The received message as bytes. An empty bytes object indicates
that the connection has been closed.

***

<a id="realtimesttsession-parse_event"></a>

### parse_event()

```python
parse_event(raw: str | bytes) -> RealtimeEvent
```

Parse a raw WebSocket message into a structured realtime event.

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `raw` | `str \| bytes` | Raw message payload received from the server. |

**Returns**

`RealtimeEvent`

A validated RealtimeEvent instance.

***

<a id="realtimesttsession-receive_event"></a>

### receive_event()

```python
receive_event() -> RealtimeEvent | None
```

Receive and parse the next realtime event from the server.

**Returns**

`RealtimeEvent | None`

The next RealtimeEvent, or None if the connection has closed.

**Raises**

- `SonioxRealtimeError` If the session is not connected.

***

<a id="realtimesttsession-receive_events"></a>

### receive_events()

```python
receive_events() -> Iterator[RealtimeEvent]
```

Yield realtime events as they are received from the server.

Iteration stops automatically when the connection is closed.

**Returns**

`Iterator[RealtimeEvent]`

***

<a id="realtimesttsession-handle_events"></a>

### handle_events()

```python
handle_events(handler: Callable[[RealtimeEvent], None]) -> None
```

Receive realtime events and dispatch them to a handler callback.

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `handler` | `Callable[[RealtimeEvent], None]` | Callable invoked for each received RealtimeEvent. |

**Returns**

`None`

***

<a id="realtimesttsession-pause"></a>

### pause()

```python
pause(*, finalize: bool = True) -> None
```

Pause the session, suppressing outgoing audio and starting a
background keepalive thread.

While paused, calls to `send_byte_chunk` are silently dropped.
A background thread sends a keepalive message every
``KEEP_ALIVE_INTERVAL_SEC`` seconds to prevent the server from
timing out the session.

Calling `pause` on an already-paused session is a no-op.

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `finalize` | `bool` | If True (default), call `finalize()` before pausing. |

**Returns**

`None`

**Raises**

- `SonioxRealtimeError` If the session is not connected.

***

<a id="realtimesttsession-resume"></a>

### resume()

```python
resume() -> None
```

Resume a paused session, stopping the keepalive thread and
allowing audio to be sent again.

Calling `resume` on a session that is not paused is a no-op.

**Returns**

`None`

**Raises**

- `SonioxRealtimeError` If the session is not connected.

---

## AsyncRealtimeSTTSession

Asynchronous WebSocket session for a single real-time speech-to-text stream.

This class manages the full lifecycle of a real-time transcription session:
connecting to the WebSocket endpoint, streaming audio data, receiving events,
and gracefully closing the stream. A session is stateful and represents
exactly one streaming interaction with the Soniox realtime API.

Instances are designed to be used as async context managers.

<a id="asyncrealtimesttsession-constructor"></a>

### Constructor

```python
AsyncRealtimeSTTSession(url: str, config: RealtimeSTTConfig, *, connect_timeout_sec: float = DEFAULT_CONNECT_TIMEOUT_SEC)
```

Create a new realtime STT session.

This does not open a network connection. The WebSocket connection
is established when entering the async context manager.

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `url` | `str` | WebSocket URL for the realtime transcription endpoint. |
| `config` | `RealtimeSTTConfig` | Configuration describing the audio format and transcription behavior for this session. |
| `connect_timeout_sec` | `float` | Maximum seconds to wait for the WebSocket handshake to complete. Defaults to 10 seconds. |

**Returns**

`None`

<a id="asyncrealtimesttsession-properties"></a>

### Properties

| Property | Type | Description |
| ------ | ------ | ------ |
| `config` | `RealtimeSTTConfig` | Return the configuration used to initialize this session. |
| `paused` | `bool` | Return True if the session is currently paused. |
| `last_message` | `RealtimeEvent \| None` | Return the most recently received realtime event, if any. |

<a id="asyncrealtimesttsession-close"></a>

### close()

```python
close() -> None
```

Close the realtime session and release the WebSocket.

Signals end-of-audio to the server and clears the underlying
connection. Subsequent calls are no-ops.

Called automatically when exiting the async context manager.

**Returns**

`None`

***

<a id="asyncrealtimesttsession-send_byte_chunk"></a>

### send_byte_chunk()

```python
send_byte_chunk(chunk: bytes) -> None
```

Send a single chunk of raw audio bytes to the realtime stream.

The audio data must match the format declared in the session
configuration (sample rate, channels, encoding).

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `chunk` | `bytes` | Raw audio bytes to send. |

**Returns**

`None`

**Raises**

- `SonioxRealtimeError` If the session is not connected or the send operation fails.

***

<a id="asyncrealtimesttsession-send_bytes"></a>

### send_bytes()

```python
send_bytes(chunks: bytes | AsyncIterator[bytes], *, finish: bool = True) -> None
```

Send audio data to the realtime stream.

Accepts either a single bytes object or an async iterator yielding
byte chunks (e.g. from `throttle_audio_async`). If `finish=True`
(the default), an end-of-audio signal is sent after the last chunk;
pass `finish=False` when you intend to send more audio later in the
same session.

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `chunks` | `bytes \| AsyncIterator[bytes]` | Raw bytes or an async iterator of byte chunks. |
| `finish` | `bool` | If True (default), signal end-of-audio after the last chunk. |

**Returns**

`None`

***

<a id="asyncrealtimesttsession-send_control_message"></a>

### send_control_message()

```python
send_control_message(control_type: RealtimeControlType) -> None
```

Send a control message to the realtime session.

Control messages modify the state of the stream, such as signaling
end-of-audio or requesting finalization.

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `control_type` | `RealtimeControlType` | The type of control message to send. |

**Returns**

`None`

**Raises**

- `SonioxRealtimeError` If the session is not connected or the message cannot be sent.

***

<a id="asyncrealtimesttsession-finish"></a>

### finish()

```python
finish() -> None
```

Signal end-of-audio.

The server finalizes any pending tokens and closes the
connection. Continue iterating `receive_events()` to consume
the remaining tokens.

**Returns**

`None`

***

<a id="asyncrealtimesttsession-keep_alive"></a>

### keep_alive()

```python
keep_alive() -> None
```

Send a keep-alive message to prevent the session from timing out.

**Returns**

`None`

***

<a id="asyncrealtimesttsession-finalize"></a>

### finalize()

```python
finalize() -> None
```

Finalize all outstanding non-final tokens while keeping the session open.

Subsequent tokens will be delivered with `is_final=True`.

**Returns**

`None`

***

<a id="asyncrealtimesttsession-recv_bytes"></a>

### recv_bytes()

```python
recv_bytes() -> bytes
```

Receive a raw message from the WebSocket connection.

**Returns**

`bytes`

The received message as bytes. An empty bytes object indicates
that the connection has been closed.

***

<a id="asyncrealtimesttsession-parse_event"></a>

### parse_event()

```python
parse_event(raw: str | bytes) -> RealtimeEvent
```

Parse a raw WebSocket message into a structured realtime event.

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `raw` | `str \| bytes` | Raw message payload received from the server. |

**Returns**

`RealtimeEvent`

A validated RealtimeEvent instance.

***

<a id="asyncrealtimesttsession-receive_event"></a>

### receive_event()

```python
receive_event() -> RealtimeEvent | None
```

Receive and parse the next realtime event from the server.

**Returns**

`RealtimeEvent | None`

The next RealtimeEvent, or None if the connection has closed.

**Raises**

- `SonioxRealtimeError` If the session is not connected.

***

<a id="asyncrealtimesttsession-receive_events"></a>

### receive_events()

```python
receive_events() -> AsyncIterator[RealtimeEvent]
```

Yield realtime events as they are received from the server.

Iteration stops automatically when the connection is closed.

**Returns**

`AsyncIterator[RealtimeEvent]`

***

<a id="asyncrealtimesttsession-handle_events"></a>

### handle_events()

```python
handle_events(handler: Callable[[RealtimeEvent], Awaitable[None]]) -> None
```

Receive realtime events and dispatch them to a handler callback.

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `handler` | `Callable[[RealtimeEvent], Awaitable[None]]` | Callable invoked for each received RealtimeEvent. |

**Returns**

`None`

***

<a id="asyncrealtimesttsession-pause"></a>

### pause()

```python
pause(*, finalize: bool = True) -> None
```

Pause the session, suppressing outgoing audio and starting a
background keepalive task.

While paused, calls to `send_byte_chunk` are silently dropped.
A background task sends a keepalive message every
``KEEP_ALIVE_INTERVAL_SEC`` seconds to prevent the server from
timing out the session.

Calling `pause` on an already-paused session is a no-op.

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `finalize` | `bool` | If True (default), call `finalize()` before pausing. |

**Returns**

`None`

**Raises**

- `SonioxRealtimeError` If the session is not connected.

***

<a id="asyncrealtimesttsession-resume"></a>

### resume()

```python
resume() -> None
```

Resume a paused session, stopping the keepalive task and
allowing audio to be sent again.

Calling `resume` on a session that is not paused is a no-op.

**Returns**

`None`

**Raises**

- `SonioxRealtimeError` If the session is not connected.

---

## RealtimeTTSClient

Factory for synchronous realtime Text-to-Speech connections and streams.

<a id="realtimettsclient-constructor"></a>

### Constructor

```python
RealtimeTTSClient(client: SonioxClient)
```

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `client` | `SonioxClient` | Soniox client instance. |

**Returns**

`None`

<a id="realtimettsclient-connect"></a>

### connect()

```python
connect(*, config: RealtimeTTSConfig, api_key: str | None = None, connect_timeout_sec: float = DEFAULT_CONNECT_TIMEOUT_SEC) -> RealtimeTTSConnection
```

Create a single-stream realtime Text-to-Speech connection.

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `config` | `RealtimeTTSConfig` | Configuration options for this operation. |
| `api_key` | `str \| None` | API key used for authentication. |
| `connect_timeout_sec` | `float` | - |

**Returns**

`RealtimeTTSConnection`

***

<a id="realtimettsclient-connect_multi_stream"></a>

### connect_multi_stream()

```python
connect_multi_stream(*, connect_timeout_sec: float = DEFAULT_CONNECT_TIMEOUT_SEC) -> RealtimeTTSMultiplexedConnection
```

Create a multiplexed realtime Text-to-Speech connection.

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `connect_timeout_sec` | `float` | - |

**Returns**

`RealtimeTTSMultiplexedConnection`

---

## AsyncRealtimeTTSClient

Factory for asynchronous realtime Text-to-Speech connections and streams.

<a id="asyncrealtimettsclient-constructor"></a>

### Constructor

```python
AsyncRealtimeTTSClient(client: AsyncSonioxClient)
```

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `client` | `AsyncSonioxClient` | Soniox client instance. |

**Returns**

`None`

<a id="asyncrealtimettsclient-connect"></a>

### connect()

```python
connect(*, config: RealtimeTTSConfig, api_key: str | None = None, connect_timeout_sec: float = DEFAULT_CONNECT_TIMEOUT_SEC) -> AsyncRealtimeTTSConnection
```

Create a single-stream realtime Text-to-Speech connection.

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `config` | `RealtimeTTSConfig` | Configuration options for this operation. |
| `api_key` | `str \| None` | API key used for authentication. |
| `connect_timeout_sec` | `float` | - |

**Returns**

`AsyncRealtimeTTSConnection`

***

<a id="asyncrealtimettsclient-connect_multi_stream"></a>

### connect_multi_stream()

```python
connect_multi_stream(*, connect_timeout_sec: float = DEFAULT_CONNECT_TIMEOUT_SEC) -> AsyncRealtimeTTSMultiplexedConnection
```

Create a multiplexed realtime Text-to-Speech connection.

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `connect_timeout_sec` | `float` | - |

**Returns**

`AsyncRealtimeTTSMultiplexedConnection`

---

## RealtimeTTSConnection

Synchronous WebSocket connection for one realtime Text-to-Speech stream.

<a id="realtimettsconnection-constructor"></a>

### Constructor

```python
RealtimeTTSConnection(url: str, config: RealtimeTTSConfig, *, connect_timeout_sec: float = DEFAULT_CONNECT_TIMEOUT_SEC)
```

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `url` | `str` | WebSocket URL for realtime transcription. |
| `config` | `RealtimeTTSConfig` | Configuration options for this operation. |
| `connect_timeout_sec` | `float` | - |

**Returns**

`None`

<a id="realtimettsconnection-properties"></a>

### Properties

| Property | Type | Description |
| ------ | ------ | ------ |
| `config` | `RealtimeTTSConfig` | Configuration used to initialize this connection. |
| `paused` | `bool` | Return True if the connection is currently paused. |
| `last_message` | `RealtimeTTSEvent \| None` | Most recently received realtime event, if any. |

<a id="realtimettsconnection-close"></a>

### close()

```python
close() -> None
```

Close the realtime Text-to-Speech connection.

**Returns**

`None`

***

<a id="realtimettsconnection-send_text_chunk"></a>

### send_text_chunk()

```python
send_text_chunk(text: str, *, text_end: bool = False) -> None
```

Send one text chunk to the realtime stream.

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `text` | `str` | Text chunk to generate into speech. |
| `text_end` | `bool` | Whether this message marks the final text chunk for the stream. |

**Returns**

`None`

***

<a id="realtimettsconnection-send_text_chunks"></a>

### send_text_chunks()

```python
send_text_chunks(chunks: str | Iterator[str], *, text_end: bool = True) -> None
```

Send text data to the realtime stream.

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `chunks` | `str \| Iterator[str]` | Audio chunks to stream to realtime transcription. |
| `text_end` | `bool` | Whether this message marks the final text chunk for the stream. |

**Returns**

`None`

***

<a id="realtimettsconnection-finish"></a>

### finish()

```python
finish() -> None
```

Signal that no more text will be sent for this stream.

**Returns**

`None`

***

<a id="realtimettsconnection-cancel"></a>

### cancel()

```python
cancel() -> None
```

Cancel the realtime Text-to-Speech stream.

**Returns**

`None`

***

<a id="realtimettsconnection-keep_alive"></a>

### keep_alive()

```python
keep_alive() -> None
```

Send a keep-alive message to prevent the session from timing out.

**Returns**

`None`

***

<a id="realtimettsconnection-pause"></a>

### pause()

```python
pause() -> None
```

Pause outgoing text and start periodic keep-alive messages.

**Returns**

`None`

***

<a id="realtimettsconnection-resume"></a>

### resume()

```python
resume() -> None
```

Resume outgoing text and stop periodic keep-alive messages.

**Returns**

`None`

***

<a id="realtimettsconnection-recv_bytes"></a>

### recv_bytes()

```python
recv_bytes() -> bytes
```

Receive one raw websocket message payload as bytes.

**Returns**

`bytes`

***

<a id="realtimettsconnection-parse_event"></a>

### parse_event()

```python
parse_event(raw: str | bytes) -> RealtimeTTSEvent
```

Parse a raw websocket message into a realtime event.

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `raw` | `str \| bytes` | Raw event payload from the realtime API. |

**Returns**

`RealtimeTTSEvent`

***

<a id="realtimettsconnection-receive_event"></a>

### receive_event()

```python
receive_event() -> RealtimeTTSEvent | None
```

Receive and parse the next realtime event.

**Returns**

`RealtimeTTSEvent | None`

***

<a id="realtimettsconnection-receive_events"></a>

### receive_events()

```python
receive_events() -> Iterator[RealtimeTTSEvent]
```

Yield realtime events until the stream ends or closes.

**Returns**

`Iterator[RealtimeTTSEvent]`

***

<a id="realtimettsconnection-receive_audio_chunks"></a>

### receive_audio_chunks()

```python
receive_audio_chunks() -> Iterator[bytes]
```

Yield decoded audio chunks from incoming realtime events.

**Returns**

`Iterator[bytes]`

---

## AsyncRealtimeTTSConnection

Asynchronous WebSocket connection for one realtime Text-to-Speech stream.

<a id="asyncrealtimettsconnection-constructor"></a>

### Constructor

```python
AsyncRealtimeTTSConnection(url: str, config: RealtimeTTSConfig, *, connect_timeout_sec: float = DEFAULT_CONNECT_TIMEOUT_SEC)
```

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `url` | `str` | WebSocket URL for realtime transcription. |
| `config` | `RealtimeTTSConfig` | Configuration options for this operation. |
| `connect_timeout_sec` | `float` | - |

**Returns**

`None`

<a id="asyncrealtimettsconnection-properties"></a>

### Properties

| Property | Type | Description |
| ------ | ------ | ------ |
| `config` | `RealtimeTTSConfig` | Configuration used to initialize this connection. |
| `paused` | `bool` | Return True if the connection is currently paused. |
| `last_message` | `RealtimeTTSEvent \| None` | Most recently received realtime event, if any. |

<a id="asyncrealtimettsconnection-close"></a>

### close()

```python
close() -> None
```

Close the realtime Text-to-Speech connection.

**Returns**

`None`

***

<a id="asyncrealtimettsconnection-send_text_chunk"></a>

### send_text_chunk()

```python
send_text_chunk(text: str, *, text_end: bool = False) -> None
```

Send one text chunk to the realtime stream.

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `text` | `str` | Text chunk to generate into speech. |
| `text_end` | `bool` | Whether this message marks the final text chunk for the stream. |

**Returns**

`None`

***

<a id="asyncrealtimettsconnection-send_text_chunks"></a>

### send_text_chunks()

```python
send_text_chunks(chunks: str | AsyncIterator[str], *, text_end: bool = True) -> None
```

Send text data to the realtime stream.

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `chunks` | `str \| AsyncIterator[str]` | Audio chunks to stream to realtime transcription. |
| `text_end` | `bool` | Whether this message marks the final text chunk for the stream. |

**Returns**

`None`

***

<a id="asyncrealtimettsconnection-finish"></a>

### finish()

```python
finish() -> None
```

Signal that no more text will be sent for this stream.

**Returns**

`None`

***

<a id="asyncrealtimettsconnection-cancel"></a>

### cancel()

```python
cancel() -> None
```

Cancel the realtime Text-to-Speech stream.

**Returns**

`None`

***

<a id="asyncrealtimettsconnection-keep_alive"></a>

### keep_alive()

```python
keep_alive() -> None
```

Send a keep-alive message to prevent the session from timing out.

**Returns**

`None`

***

<a id="asyncrealtimettsconnection-pause"></a>

### pause()

```python
pause() -> None
```

Pause outgoing text and start periodic keep-alive messages.

**Returns**

`None`

***

<a id="asyncrealtimettsconnection-resume"></a>

### resume()

```python
resume() -> None
```

Resume outgoing text and stop periodic keep-alive messages.

**Returns**

`None`

***

<a id="asyncrealtimettsconnection-recv_bytes"></a>

### recv_bytes()

```python
recv_bytes() -> bytes
```

Receive one raw websocket message payload as bytes.

**Returns**

`bytes`

***

<a id="asyncrealtimettsconnection-parse_event"></a>

### parse_event()

```python
parse_event(raw: str | bytes) -> RealtimeTTSEvent
```

Parse a raw websocket message into a realtime event.

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `raw` | `str \| bytes` | Raw event payload from the realtime API. |

**Returns**

`RealtimeTTSEvent`

***

<a id="asyncrealtimettsconnection-receive_event"></a>

### receive_event()

```python
receive_event() -> RealtimeTTSEvent | None
```

Receive and parse the next realtime event.

**Returns**

`RealtimeTTSEvent | None`

***

<a id="asyncrealtimettsconnection-receive_events"></a>

### receive_events()

```python
receive_events() -> AsyncIterator[RealtimeTTSEvent]
```

Yield realtime events until the stream ends or closes.

**Returns**

`AsyncIterator[RealtimeTTSEvent]`

***

<a id="asyncrealtimettsconnection-receive_audio_chunks"></a>

### receive_audio_chunks()

```python
receive_audio_chunks() -> AsyncIterator[bytes]
```

Yield decoded audio chunks from incoming realtime events.

**Returns**

`AsyncIterator[bytes]`

***

<a id="asyncrealtimettsconnection-handle_events"></a>

### handle_events()

```python
handle_events(handler: Callable[[RealtimeTTSEvent], Awaitable[None]]) -> None
```

Receive events and pass each one to ``handler``.

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `handler` | `Callable[[RealtimeTTSEvent], Awaitable[None]]` | Event payload received from the realtime Text-to-Speech websocket. |

**Returns**

`None`

---

## RealtimeTTSMultiplexedConnection

Synchronous websocket connection that can host multiple Text-to-Speech streams.

<a id="realtimettsmultiplexedconnection-constructor"></a>

### Constructor

```python
RealtimeTTSMultiplexedConnection(url: str, api_key: str, *, connect_timeout_sec: float = DEFAULT_CONNECT_TIMEOUT_SEC)
```

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `url` | `str` | WebSocket URL for realtime transcription. |
| `api_key` | `str` | API key used for authentication. |
| `connect_timeout_sec` | `float` | - |

**Returns**

`None`

<a id="realtimettsmultiplexedconnection-properties"></a>

### Properties

| Property | Type | Description |
| ------ | ------ | ------ |
| `last_message` | `RealtimeTTSEvent \| None` | Most recently received realtime event, if any. |
| `paused` | `bool` | Return True if the connection is currently paused. |

<a id="realtimettsmultiplexedconnection-close"></a>

### close()

```python
close() -> None
```

Close the websocket and clear the stream state.

**Returns**

`None`

***

<a id="realtimettsmultiplexedconnection-keep_alive"></a>

### keep_alive()

```python
keep_alive() -> None
```

Send a keep-alive message to prevent the session from timing out.

**Returns**

`None`

***

<a id="realtimettsmultiplexedconnection-pause"></a>

### pause()

```python
pause() -> None
```

Pause outgoing text and start periodic keep-alive messages.

**Returns**

`None`

***

<a id="realtimettsmultiplexedconnection-resume"></a>

### resume()

```python
resume() -> None
```

Resume outgoing text and stop periodic keep-alive messages.

**Returns**

`None`

***

<a id="realtimettsmultiplexedconnection-open_stream"></a>

### open_stream()

```python
open_stream(*, config: RealtimeTTSConfig) -> RealtimeTTSStream
```

Register and start a new stream on the shared websocket.

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `config` | `RealtimeTTSConfig` | Configuration options for this operation. |

**Returns**

`RealtimeTTSStream`

---

## AsyncRealtimeTTSMultiplexedConnection

Asynchronous websocket connection that can host multiple TTS streams.

<a id="asyncrealtimettsmultiplexedconnection-constructor"></a>

### Constructor

```python
AsyncRealtimeTTSMultiplexedConnection(url: str, api_key: str, *, connect_timeout_sec: float = DEFAULT_CONNECT_TIMEOUT_SEC)
```

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `url` | `str` | WebSocket URL for realtime transcription. |
| `api_key` | `str` | API key used for authentication. |
| `connect_timeout_sec` | `float` | - |

**Returns**

`None`

<a id="asyncrealtimettsmultiplexedconnection-properties"></a>

### Properties

| Property | Type | Description |
| ------ | ------ | ------ |
| `last_message` | `RealtimeTTSEvent \| None` | Most recently received realtime event, if any. |
| `paused` | `bool` | Return True if the connection is currently paused. |

<a id="asyncrealtimettsmultiplexedconnection-close"></a>

### close()

```python
close() -> None
```

Close the websocket and clear the stream state.

**Returns**

`None`

***

<a id="asyncrealtimettsmultiplexedconnection-keep_alive"></a>

### keep_alive()

```python
keep_alive() -> None
```

Send a keep-alive message to prevent the session from timing out.

**Returns**

`None`

***

<a id="asyncrealtimettsmultiplexedconnection-pause"></a>

### pause()

```python
pause() -> None
```

Pause outgoing text and start periodic keep-alive messages.

**Returns**

`None`

***

<a id="asyncrealtimettsmultiplexedconnection-resume"></a>

### resume()

```python
resume() -> None
```

Resume outgoing text and stop periodic keep-alive messages.

**Returns**

`None`

***

<a id="asyncrealtimettsmultiplexedconnection-open_stream"></a>

### open_stream()

```python
open_stream(*, config: RealtimeTTSConfig) -> AsyncRealtimeTTSStream
```

Register and start a new stream on the shared websocket.

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `config` | `RealtimeTTSConfig` | Configuration options for this operation. |

**Returns**

`AsyncRealtimeTTSStream`

---

## RealtimeTTSStream

Handle for one stream on a multiplexed realtime TTS connection.

<a id="realtimettsstream-constructor"></a>

### Constructor

```python
RealtimeTTSStream(connection: RealtimeTTSMultiplexedConnection, config: RealtimeTTSConfig)
```

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `connection` | `RealtimeTTSMultiplexedConnection` | Synchronous websocket connection that can host multiple Text-to-Speech streams. |
| `config` | `RealtimeTTSConfig` | Configuration options for this operation. |

**Returns**

`None`

<a id="realtimettsstream-properties"></a>

### Properties

| Property | Type | Description |
| ------ | ------ | ------ |
| `config` | `RealtimeTTSConfig` | Stream configuration. |
| `stream_id` | `str` | Stream identifier. |
| `last_message` | `RealtimeTTSEvent \| None` | Most recently received event for this stream, if any. |

<a id="realtimettsstream-send_text_chunk"></a>

### send_text_chunk()

```python
send_text_chunk(text: str, *, text_end: bool = False) -> None
```

Send one text chunk for this stream.

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `text` | `str` | Text chunk to generate into speech. |
| `text_end` | `bool` | Whether this message marks the final text chunk for the stream. |

**Returns**

`None`

***

<a id="realtimettsstream-send_text_chunks"></a>

### send_text_chunks()

```python
send_text_chunks(chunks: str | Iterator[str], *, text_end: bool = True) -> None
```

Send text chunks for this stream.

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `chunks` | `str \| Iterator[str]` | Audio chunks to stream to realtime transcription. |
| `text_end` | `bool` | Whether this message marks the final text chunk for the stream. |

**Returns**

`None`

***

<a id="realtimettsstream-finish"></a>

### finish()

```python
finish() -> None
```

Signal that no more text will be sent for this stream.

**Returns**

`None`

***

<a id="realtimettsstream-cancel"></a>

### cancel()

```python
cancel() -> None
```

Cancel this stream.

**Returns**

`None`

***

<a id="realtimettsstream-keep_alive"></a>

### keep_alive()

```python
keep_alive() -> None
```

Send a keepalive message on the underlying shared connection.

**Returns**

`None`

***

<a id="realtimettsstream-pause"></a>

### pause()

```python
pause() -> None
```

Pause the underlying shared connection and start keepalive.

**Returns**

`None`

***

<a id="realtimettsstream-resume"></a>

### resume()

```python
resume() -> None
```

Resume the underlying shared connection and stop keepalive.

**Returns**

`None`

***

<a id="realtimettsstream-receive_event"></a>

### receive_event()

```python
receive_event() -> RealtimeTTSEvent | None
```

Receive the next event for this stream.

**Returns**

`RealtimeTTSEvent | None`

***

<a id="realtimettsstream-receive_events"></a>

### receive_events()

```python
receive_events() -> Iterator[RealtimeTTSEvent]
```

Yield events for this stream until it ends.

**Returns**

`Iterator[RealtimeTTSEvent]`

***

<a id="realtimettsstream-receive_audio_chunks"></a>

### receive_audio_chunks()

```python
receive_audio_chunks() -> Iterator[bytes]
```

Yield decoded audio chunks for this stream.

**Returns**

`Iterator[bytes]`

---

## AsyncRealtimeTTSStream

Handle for one stream on a multiplexed realtime TTS connection.

<a id="asyncrealtimettsstream-constructor"></a>

### Constructor

```python
AsyncRealtimeTTSStream(connection: AsyncRealtimeTTSMultiplexedConnection, config: RealtimeTTSConfig)
```

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `connection` | `AsyncRealtimeTTSMultiplexedConnection` | Asynchronous websocket connection that can host multiple TTS streams. |
| `config` | `RealtimeTTSConfig` | Configuration options for this operation. |

**Returns**

`None`

<a id="asyncrealtimettsstream-properties"></a>

### Properties

| Property | Type | Description |
| ------ | ------ | ------ |
| `config` | `RealtimeTTSConfig` | Stream configuration. |
| `stream_id` | `str` | Stream identifier. |
| `last_message` | `RealtimeTTSEvent \| None` | Most recently received event for this stream, if any. |

<a id="asyncrealtimettsstream-send_text_chunk"></a>

### send_text_chunk()

```python
send_text_chunk(text: str, *, text_end: bool = False) -> None
```

Send one text chunk for this stream.

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `text` | `str` | Text chunk to generate into speech. |
| `text_end` | `bool` | Whether this message marks the final text chunk for the stream. |

**Returns**

`None`

***

<a id="asyncrealtimettsstream-send_text_chunks"></a>

### send_text_chunks()

```python
send_text_chunks(chunks: str | AsyncIterator[str], *, text_end: bool = True) -> None
```

Send text chunks for this stream.

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `chunks` | `str \| AsyncIterator[str]` | Audio chunks to stream to realtime transcription. |
| `text_end` | `bool` | Whether this message marks the final text chunk for the stream. |

**Returns**

`None`

***

<a id="asyncrealtimettsstream-finish"></a>

### finish()

```python
finish() -> None
```

Signal that no more text will be sent for this stream.

**Returns**

`None`

***

<a id="asyncrealtimettsstream-cancel"></a>

### cancel()

```python
cancel() -> None
```

Cancel this stream.

**Returns**

`None`

***

<a id="asyncrealtimettsstream-keep_alive"></a>

### keep_alive()

```python
keep_alive() -> None
```

Send a keepalive message on the underlying shared connection.

**Returns**

`None`

***

<a id="asyncrealtimettsstream-pause"></a>

### pause()

```python
pause() -> None
```

Pause the underlying shared connection and start keepalive.

**Returns**

`None`

***

<a id="asyncrealtimettsstream-resume"></a>

### resume()

```python
resume() -> None
```

Resume the underlying shared connection and stop keepalive.

**Returns**

`None`

***

<a id="asyncrealtimettsstream-receive_event"></a>

### receive_event()

```python
receive_event() -> RealtimeTTSEvent | None
```

Receive the next event for this stream.

**Returns**

`RealtimeTTSEvent | None`

***

<a id="asyncrealtimettsstream-receive_events"></a>

### receive_events()

```python
receive_events() -> AsyncIterator[RealtimeTTSEvent]
```

Yield events for this stream until it ends.

**Returns**

`AsyncIterator[RealtimeTTSEvent]`

***

<a id="asyncrealtimettsstream-receive_audio_chunks"></a>

### receive_audio_chunks()

```python
receive_audio_chunks() -> AsyncIterator[bytes]
```

Yield decoded audio chunks for this stream.

**Returns**

`AsyncIterator[bytes]`