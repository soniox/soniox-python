---
title: "soniox.realtime.async_stt"
description: "Asynchronous WebSocket session for a single real-time speech-to-text stream."
keywords: "AsyncRealtimeSTTClient, AsyncRealtimeSTTSession"
---

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

| Parameter | Type |
| ------ | ------ |
| `url` | `str` |
| `config` | `RealtimeSTTConfig` |

**Returns**

`None`

<a id="asyncrealtimesttsession-properties"></a>

### Properties

| Property | Type |
| ------ | ------ |
| `config` | `RealtimeSTTConfig` |
| `paused` | `bool` |
| `last_message` | `RealtimeEvent \| None` |
| `enter` | `-` |
| `aenter` | `-` |

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

| Parameter | Type |
| ------ | ------ |
| `chunk` | `bytes` |

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

| Parameter | Type |
| ------ | ------ |
| `chunks` | `bytes \| AsyncIterator[bytes]` |
| `finish` | `bool` |

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

| Parameter | Type |
| ------ | ------ |
| `control_type` | `RealtimeControlType` |

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

| Parameter | Type |
| ------ | ------ |
| `raw` | `str \| bytes` |

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

| Parameter | Type |
| ------ | ------ |
| `handler` | `Callable[[RealtimeEvent], Awaitable[None]]` |

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

| Parameter | Type |
| ------ | ------ |
| `client` | `AsyncSonioxClient` |

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

| Parameter | Type |
| ------ | ------ |
| `config` | `RealtimeSTTConfig` |
| `api_key` | `str \| None` |

**Returns**

`AsyncRealtimeSTTSession`

A new AsyncRealtimeSTTSession instance.

**Raises**

- `SonioxValidationError` If no API key is available.