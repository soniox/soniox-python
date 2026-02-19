---
title: "soniox.utils"
description: "Soniox Python SDK — soniox.utils Reference"
keywords: "render_tokens, start_audio_thread, stream_audio, stream_audio_async, throttle_audio, throttle_audio_async"
---

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

| Parameter | Type |
| ------ | ------ |
| `file` | `Path \| str \| BinaryIO \| bytes` |
| `chunk_size_bytes` | `int` |

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

| Parameter | Type |
| ------ | ------ |
| `file` | `Path \| str \| BinaryIO \| bytes` |
| `chunk_size_bytes` | `int` |

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

| Parameter | Type |
| ------ | ------ |
| `file` | `Path \| str \| BinaryIO \| bytes` |
| `chunk_size_bytes` | `int` |
| `delay_seconds` | `float` |

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

| Parameter | Type |
| ------ | ------ |
| `file` | `Path \| str \| BinaryIO \| bytes` |
| `chunk_size_bytes` | `int` |
| `delay_seconds` | `float` |

**Returns**

`AsyncIterator[bytes]`

---

<a id="render_tokens"></a>

## render_tokens()

```python
render_tokens(final_tokens: list[Token], non_final_tokens: list[Token]) -> str
```

Build a human-friendly transcript from token metadata.

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `final_tokens` | `list[Token]` |
| `non_final_tokens` | `list[Token]` |

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

| Parameter | Type |
| ------ | ------ |
| `session` | `RealtimeSTTSession` |
| `chunks` | `bytes \| Iterator[bytes]` |
| `name` | `str \| None` |
| `daemon` | `bool` |

**Returns**

`threading.Thread`