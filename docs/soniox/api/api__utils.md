---
title: "soniox.api._utils"
description: "Soniox Python SDK — soniox.api._utils Reference"
keywords: "build_create_payload, ensure_success, normalize_file, parse_async_response, parse_response"
---

---

<a id="ensure_success"></a>

## ensure_success()

```python
ensure_success(response: httpx.Response) -> None
```

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `response` | `httpx.Response` |

**Returns**

`None`

---

<a id="parse_response"></a>

## parse_response()

```python
parse_response(response: httpx.Response, model: type[ModelT]) -> ModelT
```

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `response` | `httpx.Response` |
| `model` | `type[ModelT]` |

**Returns**

`ModelT`

---

<a id="parse_async_response"></a>

## parse_async_response()

```python
parse_async_response(response: httpx.Response, model: type[ModelT]) -> ModelT
```

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `response` | `httpx.Response` |
| `model` | `type[ModelT]` |

**Returns**

`ModelT`

---

<a id="normalize_file"></a>

## normalize_file()

```python
normalize_file(file: BinaryIO | bytes | Path | str, filename: str | None = None) -> tuple[BinaryIO, str, bool]
```

Return (file-like, filename, should_close) tuple for upload.

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `file` | `BinaryIO \| bytes \| Path \| str` |
| `filename` | `str \| None` |

**Returns**

`tuple[BinaryIO, str, bool]`

---

<a id="build_create_payload"></a>

## build_create_payload()

```python
build_create_payload(*, model: str, file_id: str | None, audio_url: str | None, client_reference_id: str | None, config: CreateTranscriptionConfig | None) -> CreateTranscriptionPayload
```

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `model` | `str` |
| `file_id` | `str \| None` |
| `audio_url` | `str \| None` |
| `client_reference_id` | `str \| None` |
| `config` | `CreateTranscriptionConfig \| None` |

**Returns**

`CreateTranscriptionPayload`