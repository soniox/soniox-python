---
title: "Helpers"
description: "Soniox Python SDK - Helper Functions Reference"
keywords: "output_file_for_audio_format, render_tokens, start_audio_thread, start_text_thread, stream_audio, stream_audio_async, throttle_audio, throttle_audio_async"
---

---

<a id="output_file_for_audio_format"></a>

## output_file_for_audio_format()

```python
output_file_for_audio_format(audio_format: str, prefix: str) -> Path
```

Build an output file path with the correct extension for the audio format.

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `audio_format` | `str` | Audio format name (e.g. ``"wav"``, ``"mp3"``, ``"pcm_s16le"``). |
| `prefix` | `str` | Filename prefix without extension. The chosen extension is appended to this prefix to form the returned path. |

**Returns**

`Path`

---

<a id="render_tokens"></a>

## render_tokens()

```python
render_tokens(final_tokens: list[Token], non_final_tokens: list[Token]) -> str
```

Build a human-friendly transcript from token metadata.

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `final_tokens` | `list[Token]` | Token metadata emitted during realtime streaming transcriptions. |
| `non_final_tokens` | `list[Token]` | Token metadata emitted during realtime streaming transcriptions. |

**Returns**

`str`

---

<a id="start_audio_thread"></a>

## start_audio_thread()

```python
start_audio_thread(session: RealtimeSTTSession, chunks: bytes | Iterator[bytes], *, name: str | None = None, daemon: bool = True) -> threading.Thread
```

Stream audio into the session on a background thread.

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `session` | `RealtimeSTTSession` | Synchronous WebSocket session for a single real-time speech-to-text stream. |
| `chunks` | `bytes \| Iterator[bytes]` | Audio chunks to stream to realtime transcription. |
| `name` | `str \| None` | Name of the model. |
| `daemon` | `bool` | - |

**Returns**

`threading.Thread`

---

<a id="start_text_thread"></a>

## start_text_thread()

```python
start_text_thread(session: RealtimeTTSConnection | RealtimeTTSStream, chunks: str | Iterator[str], *, text_end: bool = True, name: str | None = None, daemon: bool = True) -> threading.Thread
```

Stream text into a realtime TTS session on a background thread.

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `session` | `RealtimeTTSConnection \| RealtimeTTSStream` | Synchronous WebSocket connection for one realtime Text-to-Speech stream. |
| `chunks` | `str \| Iterator[str]` | Audio chunks to stream to realtime transcription. |
| `text_end` | `bool` | Whether this message marks the final text chunk for the stream. |
| `name` | `str \| None` | Name of the model. |
| `daemon` | `bool` | - |

**Returns**

`threading.Thread`

---

<a id="stream_audio"></a>

## stream_audio()

```python
stream_audio(file: Path | str | BinaryIO | bytes, *, chunk_size_bytes: int = 4 * 1024) -> Iterator[bytes]
```

Yield fixed-size chunks from an audio source.

Supports bytes, file paths, or binary streams and slices them into
`chunk_size_bytes` blocks for realtime transmission.

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `file` | `Path \| str \| BinaryIO \| bytes` | File input to upload or transcribe. |
| `chunk_size_bytes` | `int` | - |

**Returns**

`Iterator[bytes]`

---

<a id="stream_audio_async"></a>

## stream_audio_async()

```python
stream_audio_async(file: Path | str | BinaryIO | bytes, *, chunk_size_bytes: int = 4 * 1024) -> AsyncIterator[bytes]
```

Asynchronously yield fixed-size chunks from an audio source.

Mirrors `stream_audio` but produces an async iterator for later consumption.

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `file` | `Path \| str \| BinaryIO \| bytes` | File input to upload or transcribe. |
| `chunk_size_bytes` | `int` | - |

**Returns**

`AsyncIterator[bytes]`

---

<a id="throttle_audio"></a>

## throttle_audio()

```python
throttle_audio(file: Path | str | BinaryIO | bytes, *, chunk_size_bytes: int = 4096, delay_seconds: float = 0.0) -> Iterator[bytes]
```

Yield audio chunks at a regulated pace, optionally sleeping between yields.

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `file` | `Path \| str \| BinaryIO \| bytes` | File input to upload or transcribe. |
| `chunk_size_bytes` | `int` | - |
| `delay_seconds` | `float` | - |

**Returns**

`Iterator[bytes]`

---

<a id="throttle_audio_async"></a>

## throttle_audio_async()

```python
throttle_audio_async(file: Path | str | BinaryIO | bytes, *, chunk_size_bytes: int = 32 * 1024, delay_seconds: float = 0.0) -> AsyncIterator[bytes]
```

Async counterpart of `throttle_audio`, yielding chunks with optional delay.

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `file` | `Path \| str \| BinaryIO \| bytes` | File input to upload or transcribe. |
| `chunk_size_bytes` | `int` | - |
| `delay_seconds` | `float` | - |

**Returns**

`AsyncIterator[bytes]`