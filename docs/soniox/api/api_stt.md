---
title: "soniox.api.stt"
description: "Soniox Python SDK — soniox.api.stt Reference"
keywords: "SttAPI"
---

---

## SttAPI

<a id="sttapi-constructor"></a>

### Constructor

```python
SttAPI(client: SonioxClient)
```

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `client` | `SonioxClient` |

**Returns**

`None`

<a id="sttapi-list"></a>

### list()

```python
list(limit: int = 100, cursor: str | None = None) -> GetTranscriptionsResponse
```

List transcriptions.

Performs a GET request to ``/transcriptions`` with optional pagination.

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `limit` | `int` |
| `cursor` | `str \| None` |

**Returns**

`GetTranscriptionsResponse`

**Raises**

- `SonioxAPIError` When the API returns an error.

***

<a id="sttapi-list_all"></a>

### list_all()

```python
list_all(limit: int = 100) -> Generator[Transcription, None, None]
```

Iterate through all transcriptions across all pages.

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `limit` | `int` |

**Yields**

`Generator[Transcription, None, None]`

File: The next transcription object from the API.

**Raises**

- `SonioxAPIError` When the API returns an error.

***

<a id="sttapi-delete_all"></a>

### delete_all()

```python
delete_all(limit: int = 100) -> None
```

Delete all transcriptions.

Iterates through all pages and deletes each transcription. Stops and raises on the first failed deletion.

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `limit` | `int` |

**Returns**

`None`

**Raises**

- `SonioxAPIError` When the API returns an error.

***

<a id="sttapi-create"></a>

### create()

```python
create(*, model: str = DEFAULT_MODEL, file_id: str | None = None, audio_url: str | None = None, client_reference_id: str | None = None, config: CreateTranscriptionConfig | None = None) -> Transcription
```

Create a transcription.

Performs a POST request to ``/transcriptions``.

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `model` | `str` |
| `file_id` | `str \| None` |
| `audio_url` | `str \| None` |
| `client_reference_id` | `str \| None` |
| `config` | `CreateTranscriptionConfig \| None` |

**Returns**

`Transcription`

**Raises**

- `SonioxAPIError` When the API returns an error.

***

<a id="sttapi-get"></a>

### get()

```python
get(transcription_id: str) -> Transcription
```

Retrieve a transcription by ID.

Performs a GET request to ``/transcriptions/{transcription_id}``.

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `transcription_id` | `str` |

**Returns**

`Transcription`

**Raises**

- `SonioxAPIError` When the API returns an error.

***

<a id="sttapi-get_or_none"></a>

### get_or_none()

```python
get_or_none(transcription_id: str) -> Transcription | None
```

Retrieve a transcription by ID.

Returns ``None`` if the transcription does not exist.

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `transcription_id` | `str` |

**Returns**

`Transcription | None`

**Raises**

- `SonioxAPIError` When the API returns an error.

***

<a id="sttapi-delete"></a>

### delete()

```python
delete(transcription_id: str) -> None
```

Delete a transcription by ID.

Performs a DELETE request to ``/transcriptions/{transcription_id}``.

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `transcription_id` | `str` |

**Returns**

`None`

**Raises**

- `SonioxAPIError` When the API returns an error.

***

<a id="sttapi-delete_if_exists"></a>

### delete_if_exists()

```python
delete_if_exists(transcription_id: str) -> None
```

Delete a transcription by ID if it exists.

Ignores missing transcriptions.

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `transcription_id` | `str` |

**Returns**

`None`

**Raises**

- `SonioxAPIError` When the API returns an error.

***

<a id="sttapi-destroy"></a>

### destroy()

```python
destroy(transcription_id: str) -> None
```

Delete a transcription and its associated uploaded file.

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `transcription_id` | `str` |

**Returns**

`None`

**Raises**

- `SonioxAPIError` When the API returns an error.

***

<a id="sttapi-destroy_all"></a>

### destroy_all()

```python
destroy_all(limit: int = 100) -> None
```

Delete all transcriptions and their associated files. Stops and raises on the first failed deletion.

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `limit` | `int` |

**Returns**

`None`

**Raises**

- `SonioxAPIError` When the API returns an error during listing.

***

<a id="sttapi-get_transcript"></a>

### get_transcript()

```python
get_transcript(transcription_id: str) -> TranscriptionTranscript
```

Retrieve the transcript for a transcription.

Performs a GET request to ``/transcriptions/{transcription_id}/transcript``.

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `transcription_id` | `str` |

**Returns**

`TranscriptionTranscript`

**Raises**

- `SonioxAPIError` When the API returns an error.

***

<a id="sttapi-wait"></a>

### wait()

```python
wait(transcription_id: str, *, interval_sec: float = 5.0, timeout_sec: float | None = None) -> Transcription
```

Poll a transcription until it leaves the queued or processing state.

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `transcription_id` | `str` |
| `interval_sec` | `float` |
| `timeout_sec` | `float \| None` |

**Returns**

`Transcription`

**Raises**

- `SonioxAPIError` When the API returns an error.
- `TimeoutError` Waiting for the transcription to finish exceeded `timeout_sec`.

***

<a id="sttapi-transcribe_from_url"></a>

### transcribe_from_url()

```python
transcribe_from_url(*, model: str = DEFAULT_MODEL, audio_url: str, client_reference_id: str | None = None, config: CreateTranscriptionConfig | None = None) -> Transcription
```

Create a transcription from an audio URL.

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `model` | `str` |
| `audio_url` | `str` |
| `client_reference_id` | `str \| None` |
| `config` | `CreateTranscriptionConfig \| None` |

**Returns**

`Transcription`

**Raises**

- `SonioxAPIError` When the API returns an error.

***

<a id="sttapi-transcribe_from_file_id"></a>

### transcribe_from_file_id()

```python
transcribe_from_file_id(*, model: str = DEFAULT_MODEL, file_id: str, client_reference_id: str | None = None, config: CreateTranscriptionConfig | None = None) -> Transcription
```

Create a transcription from an existing uploaded file.

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `model` | `str` |
| `file_id` | `str` |
| `client_reference_id` | `str \| None` |
| `config` | `CreateTranscriptionConfig \| None` |

**Returns**

`Transcription`

**Raises**

- `SonioxAPIError` When the API returns an error.

***

<a id="sttapi-transcribe_from_file"></a>

### transcribe_from_file()

```python
transcribe_from_file(*, model: str = DEFAULT_MODEL, file: BinaryIO | bytes | Path | str, filename: str | None = None, client_reference_id: str | None = None, config: CreateTranscriptionConfig | None = None) -> Transcription
```

Upload a file and create a transcription from it.

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `model` | `str` |
| `file` | `BinaryIO \| bytes \| Path \| str` |
| `filename` | `str \| None` |
| `client_reference_id` | `str \| None` |
| `config` | `CreateTranscriptionConfig \| None` |

**Returns**

`Transcription`

**Raises**

- `SonioxAPIError` When the API returns an error.

***

<a id="sttapi-transcribe"></a>

### transcribe()

```python
transcribe(*, model: str = DEFAULT_MODEL, audio_url: str | None = None, file_id: str | None = None, file: BinaryIO | bytes | Path | str | None = None, filename: str | None = None, client_reference_id: str | None = None, config: CreateTranscriptionConfig | None = None) -> Transcription
```

Create a transcription from a file, file ID, or audio URL.

Validates mutually exclusive inputs before submission.

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `model` | `str` |
| `audio_url` | `str \| None` |
| `file_id` | `str \| None` |
| `file` | `BinaryIO \| bytes \| Path \| str \| None` |
| `filename` | `str \| None` |
| `client_reference_id` | `str \| None` |
| `config` | `CreateTranscriptionConfig \| None` |

**Returns**

`Transcription`

**Raises**

- `SonioxAPIError` When the API returns an error.
- `SonioxValidationError` When the payload fails validation.

***

<a id="sttapi-transcribe_file_with_webhook"></a>

### transcribe_file_with_webhook()

```python
transcribe_file_with_webhook(*, model: str = DEFAULT_MODEL, file: BinaryIO | bytes | Path | str, webhook_url: str, filename: str | None = None, client_reference_id: str | None = None, webhook_auth: WebhookAuthConfig | None = None, config: CreateTranscriptionConfig | None = None) -> Transcription
```

Upload a file, configure a webhook, and start transcription.

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `model` | `str` |
| `file` | `BinaryIO \| bytes \| Path \| str` |
| `webhook_url` | `str` |
| `filename` | `str \| None` |
| `client_reference_id` | `str \| None` |
| `webhook_auth` | `WebhookAuthConfig \| None` |
| `config` | `CreateTranscriptionConfig \| None` |

**Returns**

`Transcription`

**Raises**

- `SonioxAPIError` When the API returns an error.

***

<a id="sttapi-transcribe_and_wait"></a>

### transcribe_and_wait()

```python
transcribe_and_wait(*, model: str = DEFAULT_MODEL, audio_url: str | None = None, file_id: str | None = None, file: BinaryIO | bytes | Path | str | None = None, filename: str | None = None, client_reference_id: str | None = None, delete_after: bool = False, wait_interval_sec: float = 5.0, wait_timeout_sec: float | None = None, config: CreateTranscriptionConfig | None = None) -> Transcription
```

Create a transcription and wait for completion.

Returns a Transcription object after it is completed. Optionally deletes
the transcription and the uploaded file after completion.

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `model` | `str` |
| `audio_url` | `str \| None` |
| `file_id` | `str \| None` |
| `file` | `BinaryIO \| bytes \| Path \| str \| None` |
| `filename` | `str \| None` |
| `client_reference_id` | `str \| None` |
| `delete_after` | `bool` |
| `wait_interval_sec` | `float` |
| `wait_timeout_sec` | `float \| None` |
| `config` | `CreateTranscriptionConfig \| None` |

**Returns**

`Transcription`

**Raises**

- `SonioxAPIError` When the API returns an error.
- `SonioxValidationError` When the payload fails validation.
- `TimeoutError` Waiting for the transcription to finish exceeded `timeout_sec`.

***

<a id="sttapi-transcribe_and_wait_with_tokens"></a>

### transcribe_and_wait_with_tokens()

```python
transcribe_and_wait_with_tokens(*, model: str = DEFAULT_MODEL, audio_url: str | None = None, file_id: str | None = None, file: BinaryIO | bytes | Path | str | None = None, filename: str | None = None, client_reference_id: str | None = None, delete_after: bool = False, wait_interval_sec: float = 5.0, wait_timeout_sec: float | None = None, config: CreateTranscriptionConfig | None = None) -> TranscriptionTranscript
```

Create a transcription, wait for completion, and return the transcript.

Optionally deletes the transcription and uploaded file after completion.

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `model` | `str` |
| `audio_url` | `str \| None` |
| `file_id` | `str \| None` |
| `file` | `BinaryIO \| bytes \| Path \| str \| None` |
| `filename` | `str \| None` |
| `client_reference_id` | `str \| None` |
| `delete_after` | `bool` |
| `wait_interval_sec` | `float` |
| `wait_timeout_sec` | `float \| None` |
| `config` | `CreateTranscriptionConfig \| None` |

**Returns**

`TranscriptionTranscript`

**Raises**

- `SonioxAPIError` When the API returns an error.
- `SonioxValidationError` When the payload fails validation.
- `TimeoutError` Waiting for the transcription to finish exceeded `timeout_sec`.