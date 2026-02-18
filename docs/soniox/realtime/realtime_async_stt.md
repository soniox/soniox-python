---
title: soniox.realtime.async_stt
description: Description for async_stt
keywords: annotations, json, AsyncIterator, Awaitable, Callable, TracebackType, TYPE_CHECKING, async_ws_connect, ConnectionClosed, SonioxRealtimeError, SonioxValidationError, RealtimeControlType, RealtimeEvent, RealtimeSTTConfig, KEEP_ALIVE_INTERVAL_SEC, KeepaliveTask, AsyncSonioxClient, AsyncRealtimeSTTSession, AsyncRealtimeSTTClient
---


---

## Class `AsyncRealtimeSTTSession`

Asynchronous WebSocket session for a single real-time speech-to-text stream.

This class manages the full lifecycle of a real-time transcription session:
connecting to the WebSocket endpoint, streaming audio data, receiving events,
and gracefully closing the stream. A session is stateful and represents
exactly one streaming interaction with the Soniox realtime API.

Instances are designed to be used as async context managers.

### Attributes

- **_url**: 

- **_config**: 

- **_ws**: 

- **_last_message**: 

- **_paused**: 

- **_keepalive**: 

- **config**: Return the configuration used to initialize this session.

- **paused**: Return True if the session is currently paused.

- **last_message**: Return the most recently received realtime event, if any.

- **enter**: 

- **aenter**: 

### `__init__`

Create a new realtime STT session.

This does not open a network connection. The WebSocket connection
is established when entering the async context manager.

Args:
    url:
        WebSocket URL for the realtime transcription endpoint.
    config:
        Configuration describing the audio format and transcription
        behavior for this session.

#### Signature

```python
__init__(url: str, config: RealtimeSTTConfig) -> None
```

#### Parameters

- **self** (None): 

- **url** (str): 

- **config** (RealtimeSTTConfig): 

#### Returns

None

### `__aenter__`

Open the WebSocket connection and start the realtime session.

The session configuration is sent immediately after connecting.
If any step fails, the connection is closed and a
SonioxRealtimeError is raised.

Returns:
    The active realtime session instance.

Raises:
    SonioxRealtimeError:
        If the WebSocket connection or session initialization fails.

#### Signature

```python
__aenter__() -> AsyncRealtimeSTTSession
```

#### Parameters

- **self** (None): 

#### Returns

AsyncRealtimeSTTSession

### `__aexit__`

Close the realtime session and release network resources.

This method is called automatically when exiting the async
context manager.

#### Signature

```python
__aexit__(_exc_type: type[BaseException] | None, _exc_value: BaseException | None, _traceback: TracebackType | None) -> None
```

#### Parameters

- **self** (None): 

- **_exc_type** (type[BaseException] | None): 

- **_exc_value** (BaseException | None): 

- **_traceback** (TracebackType | None): 

#### Returns

None

### `close`

Gracefully close the realtime session.

Sends a final empty message to signal end-of-stream, then closes
the WebSocket connection. Calling this method multiple times is safe.

#### Signature

```python
close() -> None
```

#### Parameters

- **self** (None): 

#### Returns

None

### `send_byte_chunk`

Send a single chunk of raw audio bytes to the realtime stream.

The audio data must match the format declared in the session
configuration (sample rate, channels, encoding).

Args:
    chunk:
        Raw audio bytes to send.

Raises:
    SonioxRealtimeError:
        If the session is not connected or the send operation fails.

#### Signature

```python
send_byte_chunk(chunk: bytes) -> None
```

#### Parameters

- **self** (None): 

- **chunk** (bytes): 

#### Returns

None

### `send_bytes`

Send audio data to the realtime stream.

This method accepts either a single bytes object or an iterator
yielding audio chunks. When an iterator is provided, a
FINISH control message is sent automatically after all chunks
have been transmitted.

Args:
    chunks:
        Audio data as raw bytes or an iterator of byte chunks.

#### Signature

```python
send_bytes(chunks: bytes | AsyncIterator[bytes], *, finish: bool = True) -> None
```

#### Parameters

- **self** (None): 

- **chunks** (bytes | AsyncIterator[bytes]): 

- **finish** (bool): 

#### Returns

None

### `send_control_message`

Send a control message to the realtime session.

Control messages modify the state of the stream, such as signaling
end-of-audio or requesting finalization.

Args:
    control_type:
        The type of control message to send.

Raises:
    SonioxRealtimeError:
        If the session is not connected or the message cannot be sent.

#### Signature

```python
send_control_message(control_type: RealtimeControlType) -> None
```

#### Parameters

- **self** (None): 

- **control_type** (RealtimeControlType): 

#### Returns

None

### `finish`

Signal that no more audio will be sent for this session.

#### Signature

```python
finish() -> None
```

#### Parameters

- **self** (None): 

#### Returns

None

### `keep_alive`

Send a keep-alive message to prevent the session from timing out.

#### Signature

```python
keep_alive() -> None
```

#### Parameters

- **self** (None): 

#### Returns

None

### `finalize`

Finalize all outstanding non-final tokens while keeping the session open.

Subsequent tokens will be delivered with `is_final=True`.

#### Signature

```python
finalize() -> None
```

#### Parameters

- **self** (None): 

#### Returns

None

### `recv_bytes`

Receive a raw message from the WebSocket connection.

Returns:
    The received message as bytes. An empty bytes object indicates
    that the connection has been closed.

#### Signature

```python
recv_bytes() -> bytes
```

#### Parameters

- **self** (None): 

#### Returns

bytes

### `parse_event`

Parse a raw WebSocket message into a structured realtime event.

Args:
    raw:
        Raw message payload received from the server.

Returns:
    A validated RealtimeEvent instance.

#### Signature

```python
parse_event(raw: str | bytes) -> RealtimeEvent
```

#### Parameters

- **self** (None): 

- **raw** (str | bytes): 

#### Returns

RealtimeEvent

### `receive_event`

Receive and parse the next realtime event from the server.

Returns:
    The next RealtimeEvent, or None if the connection has closed.

Raises:
    SonioxRealtimeError:
        If the session is not connected.

#### Signature

```python
receive_event() -> RealtimeEvent | None
```

#### Parameters

- **self** (None): 

#### Returns

RealtimeEvent | None

### `receive_events`

Yield realtime events as they are received from the server.

Iteration stops automatically when the connection is closed.

#### Signature

```python
receive_events() -> AsyncIterator[RealtimeEvent]
```

#### Parameters

- **self** (None): 

#### Returns

AsyncIterator[RealtimeEvent]

### `handle_events`

Receive realtime events and dispatch them to a handler callback.

Args:
    handler:
        Callable invoked for each received RealtimeEvent.

#### Signature

```python
handle_events(handler: Callable[[RealtimeEvent], Awaitable[None]]) -> None
```

#### Parameters

- **self** (None): 

- **handler** (Callable[[RealtimeEvent], Awaitable[None]]): 

#### Returns

None

### `pause`

Pause the session, suppressing outgoing audio and starting a
background keepalive task.

While paused, calls to :meth:`send_byte_chunk` are silently dropped.
A background task sends a keepalive message every
``KEEP_ALIVE_INTERVAL_SEC`` seconds to prevent the server from
timing out the session.

Calling `pause` on an already-paused session is a no-op.

Raises:
    SonioxRealtimeError: If the session is not connected.

#### Signature

```python
pause() -> None
```

#### Parameters

- **self** (None): 

#### Returns

None

### `resume`

Resume a paused session, stopping the keepalive task and
allowing audio to be sent again.

Calling `resume` on a session that is not paused is a no-op.

Raises:
    SonioxRealtimeError: If the session is not connected.

#### Signature

```python
resume() -> None
```

#### Parameters

- **self** (None): 

#### Returns

None

---

## Class `AsyncRealtimeSTTClient`

Factory for creating asynchronous realtime speech-to-text sessions.

This class validates credentials and prepares session configuration,
but does not itself manage WebSocket connections.

### Attributes

- **_client**: 

### `__init__`

Create a realtime STT client bound to an existing API client.

Args:
    client:
        Parent Soniox client providing configuration and credentials.

#### Signature

```python
__init__(client: AsyncSonioxClient) -> None
```

#### Parameters

- **self** (None): 

- **client** (AsyncSonioxClient): 

#### Returns

None

### `connect`

Create a new realtime STT session.

The returned session is not connected until entered as an async
context manager.

Args:
    config:
        Realtime transcription configuration.
    api_key:
        Optional API key override. If not provided, the client's
        default API key is used.

Returns:
    A new AsyncRealtimeSTTSession instance.

Raises:
    SonioxValidationError:
        If no API key is available.

#### Signature

```python
connect(*, config: RealtimeSTTConfig, api_key: str | None = None) -> AsyncRealtimeSTTSession
```

#### Parameters

- **self** (None): 

- **config** (RealtimeSTTConfig): 

- **api_key** (str | None): 

#### Returns

AsyncRealtimeSTTSession