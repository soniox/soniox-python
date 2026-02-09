---
title: soniox.realtime.stt
description: Description for stt
keywords: annotations, json, Callable, Iterator, TracebackType, TYPE_CHECKING, ConnectionClosed, sync_ws_connect, SonioxRealtimeError, SonioxValidationError, RealtimeControlType, RealtimeEvent, RealtimeSTTConfig, SonioxClient, RealtimeSTTSession, RealtimeSTTClient
---


---

## Class `RealtimeSTTSession`

Synchronous WebSocket session for a single real-time speech-to-text stream.

This class manages the full lifecycle of a real-time transcription session:
connecting to the WebSocket endpoint, streaming audio data, receiving events,
and gracefully closing the stream. A session is stateful and represents
exactly one streaming interaction with the Soniox realtime API.

Instances are designed to be used as context managers.

### Attributes

- **_url**: 

- **_config**: 

- **_ws**: 

- **_last_message**: 

- **config**: Return the configuration used to initialize this session.

- **last_message**: Return the most recently received realtime event, if any.

- **enter**: 

### `__init__`

Create a new realtime STT session.

This does not open a network connection. The WebSocket connection
is established when entering the context manager.

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

### `__enter__`

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
__enter__() -> RealtimeSTTSession
```

#### Parameters

- **self** (None): 

#### Returns

RealtimeSTTSession

### `__exit__`

Close the realtime session and release network resources.

This method is called automatically when exiting the
context manager.

#### Signature

```python
__exit__(_exc_type: type[BaseException] | None, _exc_value: BaseException | None, _traceback: TracebackType | None) -> None
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
yielding audio chunks. When an iterator is provided, a FINISH
control message is sent automatically after all chunks have
been transmitted.

Args:
    chunks:
        Audio data as raw bytes or an iterator of byte chunks.

#### Signature

```python
send_bytes(chunks: bytes | Iterator[bytes]) -> None
```

#### Parameters

- **self** (None): 

- **chunks** (bytes | Iterator[bytes]): 

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

### `send_finish`

Signal that no more audio will be sent for this session.

#### Signature

```python
send_finish() -> None
```

#### Parameters

- **self** (None): 

#### Returns

None

### `send_keep_alive`

Send a keep-alive message to prevent the session from timing out.

#### Signature

```python
send_keep_alive() -> None
```

#### Parameters

- **self** (None): 

#### Returns

None

### `send_finalize`

Finalize all outstanding non-final tokens while keeping the session open.

Subsequent tokens will be delivered with `is_final=True`.

#### Signature

```python
send_finalize() -> None
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
receive_events() -> Iterator[RealtimeEvent]
```

#### Parameters

- **self** (None): 

#### Returns

Iterator[RealtimeEvent]

### `handle_events`

Receive realtime events and dispatch them to a handler callback.

Args:
    handler:
        Callable invoked for each received RealtimeEvent.

#### Signature

```python
handle_events(handler: Callable[[RealtimeEvent], None]) -> None
```

#### Parameters

- **self** (None): 

- **handler** (Callable[[RealtimeEvent], None]): 

#### Returns

None

---

## Class `RealtimeSTTClient`

Factory for creating synchronous realtime speech-to-text sessions.

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
__init__(client: SonioxClient) -> None
```

#### Parameters

- **self** (None): 

- **client** (SonioxClient): 

#### Returns

None

### `connect`

Create a new realtime STT session.

The returned session is not connected until entered as a
context manager.

Args:
    config:
        Realtime transcription configuration.
    api_key:
        Optional API key override. If not provided, the client's
        default API key is used.

Returns:
    A new RealtimeSTTSession instance.

Raises:
    SonioxValidationError:
        If no API key is available.

#### Signature

```python
connect(*, config: RealtimeSTTConfig, api_key: str | None = None) -> RealtimeSTTSession
```

#### Parameters

- **self** (None): 

- **config** (RealtimeSTTConfig): 

- **api_key** (str | None): 

#### Returns

RealtimeSTTSession