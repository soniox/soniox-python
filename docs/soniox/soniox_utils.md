---
title: soniox.utils
description: Description for utils
keywords: annotations, asyncio, threading, time, AsyncIterator, Iterable, Iterator, Path, BinaryIO, RealtimeSTTSession, Token, stream_audio, stream_audio_async, _async_iter_chunks, _iter_chunks, throttle_audio, throttle_audio_async, render_tokens, start_audio_thread
---


---

### `stream_audio`

Yield fixed-size chunks from an audio source.

Supports bytes, file paths, or binary streams and slices them into
`chunk_size_bytes` blocks for realtime transmission.

#### Signature

```python
stream_audio(file: Path | str | BinaryIO | bytes, *, chunk_size_bytes: int = 4 * 1024) -> Iterator[bytes]
```

#### Parameters

- **file** (Path | str | BinaryIO | bytes): 

- **chunk_size_bytes** (int): 

#### Returns

Iterator[bytes]

---

### `stream_audio_async`

Asynchronously yield fixed-size chunks from an audio source.

Mirrors `stream_audio` but produces an async iterator for later consumption.

#### Signature

```python
stream_audio_async(file: Path | str | BinaryIO | bytes, *, chunk_size_bytes: int = 4 * 1024) -> AsyncIterator[bytes]
```

#### Parameters

- **file** (Path | str | BinaryIO | bytes): 

- **chunk_size_bytes** (int): 

#### Returns

AsyncIterator[bytes]

---

### `_async_iter_chunks`

Asynchronously read a binary stream in fixed-size chunks.

#### Signature

```python
_async_iter_chunks(handle: BinaryIO, chunk_size: int) -> AsyncIterator[bytes]
```

#### Parameters

- **handle** (BinaryIO): 

- **chunk_size** (int): 

#### Returns

AsyncIterator[bytes]

---

### `_iter_chunks`

Synchronously read a binary stream in fixed-size chunks.

#### Signature

```python
_iter_chunks(handle: BinaryIO, chunk_size: int) -> Iterable[bytes]
```

#### Parameters

- **handle** (BinaryIO): 

- **chunk_size** (int): 

#### Returns

Iterable[bytes]

---

### `throttle_audio`

Yield audio chunks at a regulated pace, optionally sleeping between yields.

#### Signature

```python
throttle_audio(file: Path | str | BinaryIO | bytes, *, chunk_size_bytes: int = 4096, delay_seconds: float = 0.0) -> Iterator[bytes]
```

#### Parameters

- **file** (Path | str | BinaryIO | bytes): 

- **chunk_size_bytes** (int): 

- **delay_seconds** (float): 

#### Returns

Iterator[bytes]

---

### `throttle_audio_async`

Async counterpart of `throttle_audio`, yielding chunks with optional delay.

#### Signature

```python
throttle_audio_async(file: Path | str | BinaryIO | bytes, *, chunk_size_bytes: int = 32 * 1024, delay_seconds: float = 0.0) -> AsyncIterator[bytes]
```

#### Parameters

- **file** (Path | str | BinaryIO | bytes): 

- **chunk_size_bytes** (int): 

- **delay_seconds** (float): 

#### Returns

AsyncIterator[bytes]

---

### `render_tokens`

Build a human-friendly transcript from token metadata.

#### Signature

```python
render_tokens(final_tokens: list[Token], non_final_tokens: list[Token]) -> str
```

#### Parameters

- **final_tokens** (list[Token]): 

- **non_final_tokens** (list[Token]): 

#### Returns

str

---

### `start_audio_thread`

Stream audio into the session on a background thread.

#### Signature

```python
start_audio_thread(session: RealtimeSTTSession, chunks: bytes | Iterator[bytes], *, name: str | None = None, daemon: bool = True) -> threading.Thread
```

#### Parameters

- **session** (RealtimeSTTSession): 

- **chunks** (bytes | Iterator[bytes]): 

- **name** (str | None): 

- **daemon** (bool): 

#### Returns

threading.Thread