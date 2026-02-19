---
title: "soniox.api"
description: "Soniox Python SDK — soniox.api Reference"
keywords: "AsyncAuthAPI, AsyncFilesAPI, AsyncModelsAPI, AsyncSonioxWebhooksAPI, AsyncSttAPI, AuthAPI, FilesAPI, ModelsAPI, SonioxWebhooksAPI, SttAPI"
---

---

## AsyncAuthAPI

<a id="asyncauthapi-constructor"></a>

### Constructor

```python
AsyncAuthAPI(client: AsyncSonioxClient)
```

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `client` | `AsyncSonioxClient` |

**Returns**

`None`

<a id="asyncauthapi-create_temporary_api_key"></a>

### create_temporary_api_key()

```python
create_temporary_api_key(*, usage_type: TemporaryApiKeyUsageType = 'transcribe_websocket', expires_in_seconds: int = 5 * 60, client_reference_id: str | None = None) -> CreateTemporaryApiKeyResponse
```

Create a temporary API key.

Performs a POST request to ``/auth/temporary-api-key``.

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `usage_type` | `TemporaryApiKeyUsageType` |
| `expires_in_seconds` | `int` |
| `client_reference_id` | `str \| None` |

**Returns**

`CreateTemporaryApiKeyResponse`

**Raises**

- `SonioxAPIError` When the API returns an error.

---

## AsyncFilesAPI

<a id="asyncfilesapi-constructor"></a>

### Constructor

```python
AsyncFilesAPI(client: AsyncSonioxClient)
```

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `client` | `AsyncSonioxClient` |

**Returns**

`None`

<a id="asyncfilesapi-list"></a>

### list()

```python
list(limit: int = 100, cursor: str | None = None) -> GetFilesResponse
```

List uploaded files.

Performs a GET request to ``/files`` with optional pagination.

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `limit` | `int` |
| `cursor` | `str \| None` |

**Returns**

`GetFilesResponse`

**Raises**

- `SonioxAPIError` When the API returns an error.

***

<a id="asyncfilesapi-list_all"></a>

### list_all()

```python
list_all(limit: int = 100) -> AsyncGenerator[File, None]
```

Iterate through all uploaded files across all pages.

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `limit` | `int` |

**Yields**

`AsyncGenerator[File, None]`

File: The next file object from the API.

**Raises**

- `SonioxAPIError` When the API returns an error.

***

<a id="asyncfilesapi-get"></a>

### get()

```python
get(file_id: str) -> File
```

Retrieve a file by ID.

Performs a GET request to ``/files/{file_id}``.

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `file_id` | `str` |

**Returns**

`File`

**Raises**

- `SonioxAPIError` When the API returns an error.

***

<a id="asyncfilesapi-get_or_none"></a>

### get_or_none()

```python
get_or_none(file_id: str) -> File | None
```

Retrieve a file by ID.

Returns ``None`` if the file does not exist.

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `file_id` | `str` |

**Returns**

`File | None`

**Raises**

- `SonioxAPIError` When the API returns an error.

***

<a id="asyncfilesapi-delete"></a>

### delete()

```python
delete(file_id: str) -> None
```

Delete a file by ID.

Performs a DELETE request to ``/files/{file_id}``.

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `file_id` | `str` |

**Returns**

`None`

**Raises**

- `SonioxAPIError` When the API returns an error.

***

<a id="asyncfilesapi-delete_if_exists"></a>

### delete_if_exists()

```python
delete_if_exists(file_id: str) -> None
```

Delete a file by ID if it exists.

Ignores missing files.

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `file_id` | `str` |

**Returns**

`None`

**Raises**

- `SonioxAPIError` When the API returns an error.

***

<a id="asyncfilesapi-upload"></a>

### upload()

```python
upload(file: BinaryIO | bytes | Path | str, *, filename: str | None = None, client_reference_id: str | None = None) -> File
```

Upload a file.

Performs a multipart POST request to ``/files``.

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `file` | `BinaryIO \| bytes \| Path \| str` |
| `filename` | `str \| None` |
| `client_reference_id` | `str \| None` |

**Returns**

`File`

**Raises**

- `SonioxAPIError` When the API returns an error.

***

<a id="asyncfilesapi-delete_all"></a>

### delete_all()

```python
delete_all(limit: int = 100) -> None
```

Delete all files.

Iterates through all pages and deletes each file. Stops and raises on the first failed deletion.

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `limit` | `int` |

**Returns**

`None`

**Raises**

- `SonioxAPIError` When the API returns an error.

---

## AsyncModelsAPI

<a id="asyncmodelsapi-constructor"></a>

### Constructor

```python
AsyncModelsAPI(client: AsyncSonioxClient)
```

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `client` | `AsyncSonioxClient` |

**Returns**

`None`

<a id="asyncmodelsapi-list"></a>

### list()

```python
list() -> GetModelsResponse
```

List available models.

Performs a GET request to ``/models``.

**Returns**

`GetModelsResponse`

**Raises**

- `SonioxAPIError` When the API returns an error.

---

## AsyncSttAPI

<a id="asyncsttapi-constructor"></a>

### Constructor

```python
AsyncSttAPI(client: AsyncSonioxClient)
```

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `client` | `AsyncSonioxClient` |

**Returns**

`None`

<a id="asyncsttapi-list"></a>

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

<a id="asyncsttapi-list_all"></a>

### list_all()

```python
list_all(limit: int = 100) -> AsyncGenerator[Transcription, None]
```

Iterate through all transcriptions across all pages.

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `limit` | `int` |

**Yields**

`AsyncGenerator[Transcription, None]`

File: The next transcription object from the API.

**Raises**

- `SonioxAPIError` When the API returns an error.

***

<a id="asyncsttapi-delete_all"></a>

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

<a id="asyncsttapi-create"></a>

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

<a id="asyncsttapi-get"></a>

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

<a id="asyncsttapi-get_or_none"></a>

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

<a id="asyncsttapi-delete"></a>

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

<a id="asyncsttapi-delete_if_exists"></a>

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

<a id="asyncsttapi-destroy"></a>

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

<a id="asyncsttapi-destroy_all"></a>

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

<a id="asyncsttapi-get_transcript"></a>

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

<a id="asyncsttapi-wait"></a>

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

<a id="asyncsttapi-transcribe_from_url"></a>

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

<a id="asyncsttapi-transcribe_from_file_id"></a>

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

<a id="asyncsttapi-transcribe_from_file"></a>

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

<a id="asyncsttapi-transcribe"></a>

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

<a id="asyncsttapi-transcribe_file_with_webhook"></a>

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

<a id="asyncsttapi-transcribe_and_wait"></a>

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

<a id="asyncsttapi-transcribe_and_wait_with_tokens"></a>

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

---

## AsyncSonioxWebhooksAPI

---

## AuthAPI

<a id="authapi-constructor"></a>

### Constructor

```python
AuthAPI(client: SonioxClient)
```

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `client` | `SonioxClient` |

**Returns**

`None`

<a id="authapi-create_temporary_api_key"></a>

### create_temporary_api_key()

```python
create_temporary_api_key(*, usage_type: TemporaryApiKeyUsageType = 'transcribe_websocket', expires_in_seconds: int = 5 * 60, client_reference_id: str | None = None) -> CreateTemporaryApiKeyResponse
```

Create a temporary API key.

Performs a POST request to ``/auth/temporary-api-key``.

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `usage_type` | `TemporaryApiKeyUsageType` |
| `expires_in_seconds` | `int` |
| `client_reference_id` | `str \| None` |

**Returns**

`CreateTemporaryApiKeyResponse`

**Raises**

- `SonioxAPIError` When the API returns an error.

---

## FilesAPI

<a id="filesapi-constructor"></a>

### Constructor

```python
FilesAPI(client: SonioxClient)
```

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `client` | `SonioxClient` |

**Returns**

`None`

<a id="filesapi-list"></a>

### list()

```python
list(limit: int = 100, cursor: str | None = None) -> GetFilesResponse
```

List uploaded files.

Performs a GET request to ``/files`` with optional pagination.

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `limit` | `int` |
| `cursor` | `str \| None` |

**Returns**

`GetFilesResponse`

**Raises**

- `SonioxAPIError` When the API returns an error.

***

<a id="filesapi-list_all"></a>

### list_all()

```python
list_all(limit: int = 100) -> Generator[File, None, None]
```

Iterate through all uploaded files across all pages.

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `limit` | `int` |

**Yields**

`Generator[File, None, None]`

File: The next file object from the API.

**Raises**

- `SonioxAPIError` When the API returns an error.

***

<a id="filesapi-get"></a>

### get()

```python
get(file_id: str) -> File
```

Retrieve a file by ID.

Performs a GET request to ``/files/{file_id}``.

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `file_id` | `str` |

**Returns**

`File`

**Raises**

- `SonioxAPIError` When the API returns an error.

***

<a id="filesapi-get_or_none"></a>

### get_or_none()

```python
get_or_none(file_id: str) -> File | None
```

Retrieve a file by ID.

Returns ``None`` if the file does not exist.

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `file_id` | `str` |

**Returns**

`File | None`

**Raises**

- `SonioxAPIError` When the API returns an error.

***

<a id="filesapi-delete"></a>

### delete()

```python
delete(file_id: str) -> None
```

Delete a file by ID.

Performs a DELETE request to ``/files/{file_id}``.

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `file_id` | `str` |

**Returns**

`None`

**Raises**

- `SonioxAPIError` When the API returns an error.

***

<a id="filesapi-delete_if_exists"></a>

### delete_if_exists()

```python
delete_if_exists(file_id: str) -> None
```

Delete a file by ID if it exists.

Ignores missing files.

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `file_id` | `str` |

**Returns**

`None`

**Raises**

- `SonioxAPIError` When the API returns an error.

***

<a id="filesapi-upload"></a>

### upload()

```python
upload(file: BinaryIO | bytes | Path | str, *, filename: str | None = None, client_reference_id: str | None = None) -> File
```

Upload a file.

Performs a multipart POST request to ``/files``.

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `file` | `BinaryIO \| bytes \| Path \| str` |
| `filename` | `str \| None` |
| `client_reference_id` | `str \| None` |

**Returns**

`File`

**Raises**

- `SonioxAPIError` When the API returns an error.

***

<a id="filesapi-delete_all"></a>

### delete_all()

```python
delete_all(limit: int = 100) -> None
```

Delete all files.

Iterates through all pages and deletes each file. Stops and raises on the first failed deletion.

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `limit` | `int` |

**Returns**

`None`

**Raises**

- `SonioxAPIError` When the API returns an error.

---

## ModelsAPI

<a id="modelsapi-constructor"></a>

### Constructor

```python
ModelsAPI(client: SonioxClient)
```

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `client` | `SonioxClient` |

**Returns**

`None`

<a id="modelsapi-list"></a>

### list()

```python
list() -> GetModelsResponse
```

List available models.

Performs a GET request to ``/models``.

**Returns**

`GetModelsResponse`

**Raises**

- `SonioxAPIError` When the API returns an error.

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

---

## SonioxWebhooksAPI

<a id="sonioxwebhooksapi-constructor"></a>

### Constructor

```python
SonioxWebhooksAPI(*, webhook_secret: str | None = None, webhook_header: str | None = None)
```

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `webhook_secret` | `str \| None` |
| `webhook_header` | `str \| None` |

**Returns**

`None`

<a id="sonioxwebhooksapi-verify_signature"></a>

### verify_signature()

```python
verify_signature(headers: Headers, *, auth: WebhookAuthConfig | None = None) -> None
```

Verify a webhook signature from headers.

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `headers` | `Headers` |
| `auth` | `WebhookAuthConfig \| None` |

**Returns**

`None`

**Raises**

- `InvalidWebhookSignatureError` When the webhook signature cannot be validated.

***

<a id="sonioxwebhooksapi-unwrap"></a>

### unwrap()

```python
unwrap(payload: str | bytes, headers: Headers, *, auth: WebhookAuthConfig | None = None) -> WebhookEvent
```

Validate and parse a webhook payload.

Returns a WebhookEvent.

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `payload` | `str \| bytes` |
| `headers` | `Headers` |
| `auth` | `WebhookAuthConfig \| None` |

**Returns**

`WebhookEvent`

**Raises**

- `InvalidWebhookSignatureError` When the webhook signature cannot be validated.

***

<a id="sonioxwebhooksapi-webhook_payload"></a>

### webhook_payload()

```python
webhook_payload(webhook_url: str, *, auth: WebhookAuthConfig | None = None) -> dict[str, str]
```

Return fields for webhook configuration when creating a transcription.

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `webhook_url` | `str` |
| `auth` | `WebhookAuthConfig \| None` |

**Returns**

`dict[str, str]`