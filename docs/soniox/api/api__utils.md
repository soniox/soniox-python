---
title: soniox.api._utils
description: Description for _utils
keywords: annotations, io, Path, BinaryIO, TypeVar, httpx, BaseModel, SonioxAPIError, CreateTranscriptionConfig, CreateTranscriptionPayload, ModelT, ensure_success, parse_response, parse_async_response, normalize_file, build_create_payload
---


---

### `ensure_success`

#### Signature

```python
ensure_success(response: httpx.Response) -> None
```

#### Parameters

- **response** (httpx.Response): 

#### Returns

None

---

### `parse_response`

#### Signature

```python
parse_response(response: httpx.Response, model: type[ModelT]) -> ModelT
```

#### Parameters

- **response** (httpx.Response): 

- **model** (type[ModelT]): 

#### Returns

ModelT

---

### `parse_async_response`

#### Signature

```python
parse_async_response(response: httpx.Response, model: type[ModelT]) -> ModelT
```

#### Parameters

- **response** (httpx.Response): 

- **model** (type[ModelT]): 

#### Returns

ModelT

---

### `normalize_file`

Return (file-like, filename, should_close) tuple for upload.

#### Signature

```python
normalize_file(file: BinaryIO | bytes | Path | str, filename: str | None = None) -> tuple[BinaryIO, str, bool]
```

#### Parameters

- **file** (BinaryIO | bytes | Path | str): 

- **filename** (str | None): 

#### Returns

tuple[BinaryIO, str, bool]

---

### `build_create_payload`

#### Signature

```python
build_create_payload(*, model: str, file_id: str | None, audio_url: str | None, client_reference_id: str | None, config: CreateTranscriptionConfig | None) -> CreateTranscriptionPayload
```

#### Parameters

- **model** (str): 

- **file_id** (str | None): 

- **audio_url** (str | None): 

- **client_reference_id** (str | None): 

- **config** (CreateTranscriptionConfig | None): 

#### Returns

CreateTranscriptionPayload