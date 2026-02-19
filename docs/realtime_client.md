---
title: "Realtime Client"
description: "Soniox Python SDK - Realtime Client Reference"
keywords: "RealtimeAPI, AsyncRealtimeAPI, RealtimeSTTClient, RealtimeSTTSession, AsyncRealtimeSTTClient, AsyncRealtimeSTTSession"
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
connect(*, config: RealtimeSTTConfig, api_key: str | None = None) -> RealtimeSTTSession
```

Create a new realtime STT session.

The returned session is not connected until entered as a
context manager.

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `config` | `RealtimeSTTConfig` | Realtime transcription configuration. |
| `api_key` | `str \| None` | Optional API key override. If not provided, the client's default API key is used. |

**Returns**

`RealtimeSTTSession`

A new RealtimeSTTSession instance.

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
RealtimeSTTSession(url: str, config: RealtimeSTTConfig)
```

Create a new realtime STT session.

This does not open a network connection. The WebSocket connection
is established when entering the context manager.

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `url` | `str` | WebSocket URL for the realtime transcription endpoint. |
| `config` | `RealtimeSTTConfig` | Configuration describing the audio format and transcription behavior for this session. |

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

Gracefully close the realtime session.

Sends a final empty message to signal end-of-stream, then closes
the WebSocket connection. Calling this method multiple times is safe.

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

This method accepts either a single bytes object or an iterator
yielding audio chunks. When an iterator is provided, a FINISH
control message is sent automatically after all chunks have
been transmitted.

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `chunks` | `bytes \| Iterator[bytes]` | Audio data as raw bytes or an iterator of byte chunks. |
| `finish` | `bool` | Whether to send a finish signal after streaming completes. |

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

Signal that no more audio will be sent for this session.

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
pause() -> None
```

Pause the session, suppressing outgoing audio and starting a
background keepalive thread.

While paused, calls to :meth:`send_byte_chunk` are silently dropped.
A background thread sends a keepalive message every
``KEEP_ALIVE_INTERVAL_SEC`` seconds to prevent the server from
timing out the session.

Calling `pause` on an already-paused session is a no-op.

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
connect(*, config: RealtimeSTTConfig, api_key: str | None = None) -> AsyncRealtimeSTTSession
```

Create a new realtime STT session.

The returned session is not connected until entered as an async
context manager.

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `config` | `RealtimeSTTConfig` | Realtime transcription configuration. |
| `api_key` | `str \| None` | Optional API key override. If not provided, the client's default API key is used. |

**Returns**

`AsyncRealtimeSTTSession`

A new AsyncRealtimeSTTSession instance.

**Raises**

- `SonioxValidationError` If no API key is available.

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
AsyncRealtimeSTTSession(url: str, config: RealtimeSTTConfig)
```

Create a new realtime STT session.

This does not open a network connection. The WebSocket connection
is established when entering the async context manager.

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `url` | `str` | WebSocket URL for the realtime transcription endpoint. |
| `config` | `RealtimeSTTConfig` | Configuration describing the audio format and transcription behavior for this session. |

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

Gracefully close the realtime session.

Sends a final empty message to signal end-of-stream, then closes
the WebSocket connection. Calling this method multiple times is safe.

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

This method accepts either a single bytes object or an iterator
yielding audio chunks. When an iterator is provided, a
FINISH control message is sent automatically after all chunks
have been transmitted.

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `chunks` | `bytes \| AsyncIterator[bytes]` | Audio data as raw bytes or an iterator of byte chunks. |
| `finish` | `bool` | Whether to send a finish signal after streaming completes. |

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

Signal that no more audio will be sent for this session.

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
pause() -> None
```

Pause the session, suppressing outgoing audio and starting a
background keepalive task.

While paused, calls to :meth:`send_byte_chunk` are silently dropped.
A background task sends a keepalive message every
``KEEP_ALIVE_INTERVAL_SEC`` seconds to prevent the server from
timing out the session.

Calling `pause` on an already-paused session is a no-op.

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