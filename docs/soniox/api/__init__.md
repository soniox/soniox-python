---
title: soniox.api
description: Description for api
keywords: AsyncAuthAPI, AsyncFilesAPI, AsyncModelsAPI, AsyncSttAPI, AsyncSonioxWebhooksAPI, AuthAPI, FilesAPI, ModelsAPI, SttAPI, SonioxWebhooksAPI, __all__, webhooks, files, async_files, stt, auth, models, async_webhooks, _utils, async_stt, async_auth, async_models
---


---

## Class `AsyncAuthAPI`

### Attributes

- **_client**: 

### `__init__`

#### Signature

```python
__init__(client: AsyncSonioxClient) -> None
```

#### Parameters

- **self** (None): 

- **client** (AsyncSonioxClient): 

#### Returns

None

### `create_temporary_api_key`

Create a temporary API key.

Performs a POST request to ``/auth/temporary-api-key``.

Raises:
    SonioxAPIError: When the API returns an error.

#### Signature

```python
create_temporary_api_key(*, usage_type: TemporaryApiKeyUsageType = 'transcribe_websocket', expires_in_seconds: int = 5 * 60, client_reference_id: str | None = None) -> CreateTemporaryApiKeyResponse
```

#### Parameters

- **self** (None): 

- **usage_type** (TemporaryApiKeyUsageType): 

- **expires_in_seconds** (int): 

- **client_reference_id** (str | None): 

#### Returns

CreateTemporaryApiKeyResponse

---

## Class `AsyncFilesAPI`

### Attributes

- **_client**: 

### `__init__`

#### Signature

```python
__init__(client: AsyncSonioxClient) -> None
```

#### Parameters

- **self** (None): 

- **client** (AsyncSonioxClient): 

#### Returns

None

### `list`

List uploaded files.

Performs a GET request to ``/files`` with optional pagination.

Raises:
    SonioxAPIError: When the API returns an error.

#### Signature

```python
list(limit: int = 100, cursor: str | None = None) -> GetFilesResponse
```

#### Parameters

- **self** (None): 

- **limit** (int): 

- **cursor** (str | None): 

#### Returns

GetFilesResponse

### `list_all`

Iterate through all uploaded files across all pages.

Yields:
    File: The next file object from the API.

Raises:
    SonioxAPIError: When the API returns an error.

#### Signature

```python
list_all(limit: int = 100) -> AsyncGenerator[File, None]
```

#### Parameters

- **self** (None): 

- **limit** (int): 

#### Returns

AsyncGenerator[File, None]

### `get`

Retrieve a file by ID.

Performs a GET request to ``/files/{file_id}``.

Raises:
    SonioxAPIError: When the API returns an error.

#### Signature

```python
get(file_id: str) -> File
```

#### Parameters

- **self** (None): 

- **file_id** (str): 

#### Returns

File

### `get_or_none`

Retrieve a file by ID.

Returns ``None`` if the file does not exist.

Raises:
    SonioxAPIError: When the API returns an error.

#### Signature

```python
get_or_none(file_id: str) -> File | None
```

#### Parameters

- **self** (None): 

- **file_id** (str): 

#### Returns

File | None

### `delete`

Delete a file by ID.

Performs a DELETE request to ``/files/{file_id}``.

Raises:
    SonioxAPIError: When the API returns an error.

#### Signature

```python
delete(file_id: str) -> None
```

#### Parameters

- **self** (None): 

- **file_id** (str): 

#### Returns

None

### `delete_if_exists`

Delete a file by ID if it exists.

Ignores missing files.

Raises:
    SonioxAPIError: When the API returns an error.

#### Signature

```python
delete_if_exists(file_id: str) -> None
```

#### Parameters

- **self** (None): 

- **file_id** (str): 

#### Returns

None

### `upload`

Upload a file.

Performs a multipart POST request to ``/files``.

Raises:
    SonioxAPIError: When the API returns an error.

#### Signature

```python
upload(file: BinaryIO | bytes | Path | str, *, filename: str | None = None, client_reference_id: str | None = None) -> File
```

#### Parameters

- **self** (None): 

- **file** (BinaryIO | bytes | Path | str): 

- **filename** (str | None): 

- **client_reference_id** (str | None): 

#### Returns

File

### `delete_all`

Delete all files.

Iterates through all pages and deletes each file. Stops and raises on the first failed deletion.

Raises:
    SonioxAPIError: When the API returns an error.

#### Signature

```python
delete_all(limit: int = 100) -> None
```

#### Parameters

- **self** (None): 

- **limit** (int): 

#### Returns

None

---

## Class `AsyncModelsAPI`

### Attributes

- **_client**: 

### `__init__`

#### Signature

```python
__init__(client: AsyncSonioxClient) -> None
```

#### Parameters

- **self** (None): 

- **client** (AsyncSonioxClient): 

#### Returns

None

### `list`

List available models.

Performs a GET request to ``/models``.

Raises:
    SonioxAPIError: When the API returns an error.

#### Signature

```python
list() -> GetModelsResponse
```

#### Parameters

- **self** (None): 

#### Returns

GetModelsResponse

---

## Class `AsyncSttAPI`

### Attributes

- **_client**: 

### `__init__`

#### Signature

```python
__init__(client: AsyncSonioxClient) -> None
```

#### Parameters

- **self** (None): 

- **client** (AsyncSonioxClient): 

#### Returns

None

### `list`

List transcriptions.

Performs a GET request to ``/transcriptions`` with optional pagination.

Raises:
    SonioxAPIError: When the API returns an error.

#### Signature

```python
list(limit: int = 100, cursor: str | None = None) -> GetTranscriptionsResponse
```

#### Parameters

- **self** (None): 

- **limit** (int): 

- **cursor** (str | None): 

#### Returns

GetTranscriptionsResponse

### `list_all`

Iterate through all transcriptions across all pages.

Yields:
    File: The next transcription object from the API.

Raises:
    SonioxAPIError: When the API returns an error.

#### Signature

```python
list_all(limit: int = 100) -> AsyncGenerator[Transcription, None]
```

#### Parameters

- **self** (None): 

- **limit** (int): 

#### Returns

AsyncGenerator[Transcription, None]

### `delete_all`

Delete all transcriptions.

Iterates through all pages and deletes each transcription. Stops and raises on the first failed deletion.

Raises:
    SonioxAPIError: When the API returns an error.

#### Signature

```python
delete_all(limit: int = 100) -> None
```

#### Parameters

- **self** (None): 

- **limit** (int): 

#### Returns

None

### `create`

Create a transcription.

Performs a POST request to ``/transcriptions``.

Raises:
    SonioxAPIError: When the API returns an error.

#### Signature

```python
create(*, model: str = DEFAULT_MODEL, file_id: str | None = None, audio_url: str | None = None, client_reference_id: str | None = None, config: CreateTranscriptionConfig | None = None) -> Transcription
```

#### Parameters

- **self** (None): 

- **model** (str): 

- **file_id** (str | None): 

- **audio_url** (str | None): 

- **client_reference_id** (str | None): 

- **config** (CreateTranscriptionConfig | None): 

#### Returns

Transcription

### `get`

Retrieve a transcription by ID.

Performs a GET request to ``/transcriptions/{transcription_id}``.

Raises:
    SonioxAPIError: When the API returns an error.

#### Signature

```python
get(transcription_id: str) -> Transcription
```

#### Parameters

- **self** (None): 

- **transcription_id** (str): 

#### Returns

Transcription

### `get_or_none`

Retrieve a transcription by ID.

Returns ``None`` if the transcription does not exist.

Raises:
    SonioxAPIError: When the API returns an error.

#### Signature

```python
get_or_none(transcription_id: str) -> Transcription | None
```

#### Parameters

- **self** (None): 

- **transcription_id** (str): 

#### Returns

Transcription | None

### `delete`

Delete a transcription by ID.

Performs a DELETE request to ``/transcriptions/{transcription_id}``.

Raises:
    SonioxAPIError: When the API returns an error.

#### Signature

```python
delete(transcription_id: str) -> None
```

#### Parameters

- **self** (None): 

- **transcription_id** (str): 

#### Returns

None

### `delete_if_exists`

Delete a transcription by ID if it exists.

Ignores missing transcriptions.

Raises:
    SonioxAPIError: When the API returns an error.

#### Signature

```python
delete_if_exists(transcription_id: str) -> None
```

#### Parameters

- **self** (None): 

- **transcription_id** (str): 

#### Returns

None

### `destroy`

Delete a transcription and its associated uploaded file.

Raises:
    SonioxAPIError: When the API returns an error.

#### Signature

```python
destroy(transcription_id: str) -> None
```

#### Parameters

- **self** (None): 

- **transcription_id** (str): 

#### Returns

None

### `destroy_all`

Delete all transcriptions and their associated files. Stops and raises on the first failed deletion.

Raises:
    SonioxAPIError: When the API returns an error during listing.

#### Signature

```python
destroy_all(limit: int = 100) -> None
```

#### Parameters

- **self** (None): 

- **limit** (int): 

#### Returns

None

### `get_transcript`

Retrieve the transcript for a transcription.

Performs a GET request to ``/transcriptions/{transcription_id}/transcript``.

Raises:
    SonioxAPIError: When the API returns an error.

#### Signature

```python
get_transcript(transcription_id: str) -> TranscriptionTranscript
```

#### Parameters

- **self** (None): 

- **transcription_id** (str): 

#### Returns

TranscriptionTranscript

### `wait`

Poll a transcription until it leaves the queued or processing state.

Raises:
    SonioxAPIError: When the API returns an error.
    TimeoutError: Waiting for the transcription to finish exceeded `timeout_sec`.

#### Signature

```python
wait(transcription_id: str, *, interval_sec: float = 5.0, timeout_sec: float | None = None) -> Transcription
```

#### Parameters

- **self** (None): 

- **transcription_id** (str): 

- **interval_sec** (float): 

- **timeout_sec** (float | None): 

#### Returns

Transcription

### `transcribe_from_url`

Create a transcription from an audio URL.

Raises:
    SonioxAPIError: When the API returns an error.

#### Signature

```python
transcribe_from_url(*, model: str = DEFAULT_MODEL, audio_url: str, client_reference_id: str | None = None, config: CreateTranscriptionConfig | None = None) -> Transcription
```

#### Parameters

- **self** (None): 

- **model** (str): 

- **audio_url** (str): 

- **client_reference_id** (str | None): 

- **config** (CreateTranscriptionConfig | None): 

#### Returns

Transcription

### `transcribe_from_file_id`

Create a transcription from an existing uploaded file.

Raises:
    SonioxAPIError: When the API returns an error.

#### Signature

```python
transcribe_from_file_id(*, model: str = DEFAULT_MODEL, file_id: str, client_reference_id: str | None = None, config: CreateTranscriptionConfig | None = None) -> Transcription
```

#### Parameters

- **self** (None): 

- **model** (str): 

- **file_id** (str): 

- **client_reference_id** (str | None): 

- **config** (CreateTranscriptionConfig | None): 

#### Returns

Transcription

### `transcribe_from_file`

Upload a file and create a transcription from it.

Raises:
    SonioxAPIError: When the API returns an error.

#### Signature

```python
transcribe_from_file(*, model: str = DEFAULT_MODEL, file: BinaryIO | bytes | Path | str, filename: str | None = None, client_reference_id: str | None = None, config: CreateTranscriptionConfig | None = None) -> Transcription
```

#### Parameters

- **self** (None): 

- **model** (str): 

- **file** (BinaryIO | bytes | Path | str): 

- **filename** (str | None): 

- **client_reference_id** (str | None): 

- **config** (CreateTranscriptionConfig | None): 

#### Returns

Transcription

### `transcribe`

Create a transcription from a file, file ID, or audio URL.

Validates mutually exclusive inputs before submission.

Raises:
    SonioxAPIError: When the API returns an error.
    SonioxValidationError: When the payload fails validation.

#### Signature

```python
transcribe(*, model: str = DEFAULT_MODEL, audio_url: str | None = None, file_id: str | None = None, file: BinaryIO | bytes | Path | str | None = None, filename: str | None = None, client_reference_id: str | None = None, config: CreateTranscriptionConfig | None = None) -> Transcription
```

#### Parameters

- **self** (None): 

- **model** (str): 

- **audio_url** (str | None): 

- **file_id** (str | None): 

- **file** (BinaryIO | bytes | Path | str | None): 

- **filename** (str | None): 

- **client_reference_id** (str | None): 

- **config** (CreateTranscriptionConfig | None): 

#### Returns

Transcription

### `transcribe_file_with_webhook`

Upload a file, configure a webhook, and start transcription.

Raises:
    SonioxAPIError: When the API returns an error.

#### Signature

```python
transcribe_file_with_webhook(*, model: str = DEFAULT_MODEL, file: BinaryIO | bytes | Path | str, webhook_url: str, filename: str | None = None, client_reference_id: str | None = None, webhook_auth: WebhookAuthConfig | None = None, config: CreateTranscriptionConfig | None = None) -> Transcription
```

#### Parameters

- **self** (None): 

- **model** (str): 

- **file** (BinaryIO | bytes | Path | str): 

- **webhook_url** (str): 

- **filename** (str | None): 

- **client_reference_id** (str | None): 

- **webhook_auth** (WebhookAuthConfig | None): 

- **config** (CreateTranscriptionConfig | None): 

#### Returns

Transcription

### `transcribe_and_wait`

Create a transcription and wait for completion.

Returns a Transcription object after it is completed. Optionally deletes
the transcription and the uploaded file after completion.

Raises:
    SonioxAPIError: When the API returns an error.
    SonioxValidationError: When the payload fails validation.
    TimeoutError: Waiting for the transcription to finish exceeded `timeout_sec`.

#### Signature

```python
transcribe_and_wait(*, model: str = DEFAULT_MODEL, audio_url: str | None = None, file_id: str | None = None, file: BinaryIO | bytes | Path | str | None = None, filename: str | None = None, client_reference_id: str | None = None, delete_after: bool = False, wait_interval_sec: float = 5.0, wait_timeout_sec: float | None = None, config: CreateTranscriptionConfig | None = None) -> Transcription
```

#### Parameters

- **self** (None): 

- **model** (str): 

- **audio_url** (str | None): 

- **file_id** (str | None): 

- **file** (BinaryIO | bytes | Path | str | None): 

- **filename** (str | None): 

- **client_reference_id** (str | None): 

- **delete_after** (bool): 

- **wait_interval_sec** (float): 

- **wait_timeout_sec** (float | None): 

- **config** (CreateTranscriptionConfig | None): 

#### Returns

Transcription

### `transcribe_and_wait_with_tokens`

Create a transcription, wait for completion, and return the transcript.

Optionally deletes the transcription and uploaded file after completion.

Raises:
    SonioxAPIError: When the API returns an error.
    SonioxValidationError: When the payload fails validation.
    TimeoutError: Waiting for the transcription to finish exceeded `timeout_sec`.

#### Signature

```python
transcribe_and_wait_with_tokens(*, model: str = DEFAULT_MODEL, audio_url: str | None = None, file_id: str | None = None, file: BinaryIO | bytes | Path | str | None = None, filename: str | None = None, client_reference_id: str | None = None, delete_after: bool = False, wait_interval_sec: float = 5.0, wait_timeout_sec: float | None = None, config: CreateTranscriptionConfig | None = None) -> TranscriptionTranscript
```

#### Parameters

- **self** (None): 

- **model** (str): 

- **audio_url** (str | None): 

- **file_id** (str | None): 

- **file** (BinaryIO | bytes | Path | str | None): 

- **filename** (str | None): 

- **client_reference_id** (str | None): 

- **delete_after** (bool): 

- **wait_interval_sec** (float): 

- **wait_timeout_sec** (float | None): 

- **config** (CreateTranscriptionConfig | None): 

#### Returns

TranscriptionTranscript

---

## Class `AsyncSonioxWebhooksAPI`

---

## Class `AuthAPI`

### Attributes

- **_client**: 

### `__init__`

#### Signature

```python
__init__(client: SonioxClient) -> None
```

#### Parameters

- **self** (None): 

- **client** (SonioxClient): 

#### Returns

None

### `create_temporary_api_key`

Create a temporary API key.

Performs a POST request to ``/auth/temporary-api-key``.

Raises:
    SonioxAPIError: When the API returns an error.

#### Signature

```python
create_temporary_api_key(*, usage_type: TemporaryApiKeyUsageType = 'transcribe_websocket', expires_in_seconds: int = 5 * 60, client_reference_id: str | None = None) -> CreateTemporaryApiKeyResponse
```

#### Parameters

- **self** (None): 

- **usage_type** (TemporaryApiKeyUsageType): 

- **expires_in_seconds** (int): 

- **client_reference_id** (str | None): 

#### Returns

CreateTemporaryApiKeyResponse

---

## Class `FilesAPI`

### Attributes

- **_client**: 

### `__init__`

#### Signature

```python
__init__(client: SonioxClient) -> None
```

#### Parameters

- **self** (None): 

- **client** (SonioxClient): 

#### Returns

None

### `list`

List uploaded files.

Performs a GET request to ``/files`` with optional pagination.

Raises:
    SonioxAPIError: When the API returns an error.

#### Signature

```python
list(limit: int = 100, cursor: str | None = None) -> GetFilesResponse
```

#### Parameters

- **self** (None): 

- **limit** (int): 

- **cursor** (str | None): 

#### Returns

GetFilesResponse

### `list_all`

Iterate through all uploaded files across all pages.

Yields:
    File: The next file object from the API.

Raises:
    SonioxAPIError: When the API returns an error.

#### Signature

```python
list_all(limit: int = 100) -> Generator[File, None, None]
```

#### Parameters

- **self** (None): 

- **limit** (int): 

#### Returns

Generator[File, None, None]

### `get`

Retrieve a file by ID.

Performs a GET request to ``/files/{file_id}``.

Raises:
    SonioxAPIError: When the API returns an error.

#### Signature

```python
get(file_id: str) -> File
```

#### Parameters

- **self** (None): 

- **file_id** (str): 

#### Returns

File

### `get_or_none`

Retrieve a file by ID.

Returns ``None`` if the file does not exist.

Raises:
    SonioxAPIError: When the API returns an error.

#### Signature

```python
get_or_none(file_id: str) -> File | None
```

#### Parameters

- **self** (None): 

- **file_id** (str): 

#### Returns

File | None

### `delete`

Delete a file by ID.

Performs a DELETE request to ``/files/{file_id}``.

Raises:
    SonioxAPIError: When the API returns an error.

#### Signature

```python
delete(file_id: str) -> None
```

#### Parameters

- **self** (None): 

- **file_id** (str): 

#### Returns

None

### `delete_if_exists`

Delete a file by ID if it exists.

Ignores missing files.

Raises:
    SonioxAPIError: When the API returns an error.

#### Signature

```python
delete_if_exists(file_id: str) -> None
```

#### Parameters

- **self** (None): 

- **file_id** (str): 

#### Returns

None

### `upload`

Upload a file.

Performs a multipart POST request to ``/files``.

Raises:
    SonioxAPIError: When the API returns an error.

#### Signature

```python
upload(file: BinaryIO | bytes | Path | str, *, filename: str | None = None, client_reference_id: str | None = None) -> File
```

#### Parameters

- **self** (None): 

- **file** (BinaryIO | bytes | Path | str): 

- **filename** (str | None): 

- **client_reference_id** (str | None): 

#### Returns

File

### `delete_all`

Delete all files.

Iterates through all pages and deletes each file. Stops and raises on the first failed deletion.

Raises:
    SonioxAPIError: When the API returns an error.

#### Signature

```python
delete_all(limit: int = 100) -> None
```

#### Parameters

- **self** (None): 

- **limit** (int): 

#### Returns

None

---

## Class `ModelsAPI`

### Attributes

- **_client**: 

### `__init__`

#### Signature

```python
__init__(client: SonioxClient) -> None
```

#### Parameters

- **self** (None): 

- **client** (SonioxClient): 

#### Returns

None

### `list`

List available models.

Performs a GET request to ``/models``.

Raises:
    SonioxAPIError: When the API returns an error.

#### Signature

```python
list() -> GetModelsResponse
```

#### Parameters

- **self** (None): 

#### Returns

GetModelsResponse

---

## Class `SttAPI`

### Attributes

- **_client**: 

### `__init__`

#### Signature

```python
__init__(client: SonioxClient) -> None
```

#### Parameters

- **self** (None): 

- **client** (SonioxClient): 

#### Returns

None

### `list`

List transcriptions.

Performs a GET request to ``/transcriptions`` with optional pagination.

Raises:
    SonioxAPIError: When the API returns an error.

#### Signature

```python
list(limit: int = 100, cursor: str | None = None) -> GetTranscriptionsResponse
```

#### Parameters

- **self** (None): 

- **limit** (int): 

- **cursor** (str | None): 

#### Returns

GetTranscriptionsResponse

### `list_all`

Iterate through all transcriptions across all pages.

Yields:
    File: The next transcription object from the API.

Raises:
    SonioxAPIError: When the API returns an error.

#### Signature

```python
list_all(limit: int = 100) -> Generator[Transcription, None, None]
```

#### Parameters

- **self** (None): 

- **limit** (int): 

#### Returns

Generator[Transcription, None, None]

### `delete_all`

Delete all transcriptions.

Iterates through all pages and deletes each transcription. Stops and raises on the first failed deletion.

Raises:
    SonioxAPIError: When the API returns an error.

#### Signature

```python
delete_all(limit: int = 100) -> None
```

#### Parameters

- **self** (None): 

- **limit** (int): 

#### Returns

None

### `create`

Create a transcription.

Performs a POST request to ``/transcriptions``.

Raises:
    SonioxAPIError: When the API returns an error.

#### Signature

```python
create(*, model: str = DEFAULT_MODEL, file_id: str | None = None, audio_url: str | None = None, client_reference_id: str | None = None, config: CreateTranscriptionConfig | None = None) -> Transcription
```

#### Parameters

- **self** (None): 

- **model** (str): 

- **file_id** (str | None): 

- **audio_url** (str | None): 

- **client_reference_id** (str | None): 

- **config** (CreateTranscriptionConfig | None): 

#### Returns

Transcription

### `get`

Retrieve a transcription by ID.

Performs a GET request to ``/transcriptions/{transcription_id}``.

Raises:
    SonioxAPIError: When the API returns an error.

#### Signature

```python
get(transcription_id: str) -> Transcription
```

#### Parameters

- **self** (None): 

- **transcription_id** (str): 

#### Returns

Transcription

### `get_or_none`

Retrieve a transcription by ID.

Returns ``None`` if the transcription does not exist.

Raises:
    SonioxAPIError: When the API returns an error.

#### Signature

```python
get_or_none(transcription_id: str) -> Transcription | None
```

#### Parameters

- **self** (None): 

- **transcription_id** (str): 

#### Returns

Transcription | None

### `delete`

Delete a transcription by ID.

Performs a DELETE request to ``/transcriptions/{transcription_id}``.

Raises:
    SonioxAPIError: When the API returns an error.

#### Signature

```python
delete(transcription_id: str) -> None
```

#### Parameters

- **self** (None): 

- **transcription_id** (str): 

#### Returns

None

### `delete_if_exists`

Delete a transcription by ID if it exists.

Ignores missing transcriptions.

Raises:
    SonioxAPIError: When the API returns an error.

#### Signature

```python
delete_if_exists(transcription_id: str) -> None
```

#### Parameters

- **self** (None): 

- **transcription_id** (str): 

#### Returns

None

### `destroy`

Delete a transcription and its associated uploaded file.

Raises:
    SonioxAPIError: When the API returns an error.

#### Signature

```python
destroy(transcription_id: str) -> None
```

#### Parameters

- **self** (None): 

- **transcription_id** (str): 

#### Returns

None

### `destroy_all`

Delete all transcriptions and their associated files. Stops and raises on the first failed deletion.

Raises:
    SonioxAPIError: When the API returns an error during listing.

#### Signature

```python
destroy_all(limit: int = 100) -> None
```

#### Parameters

- **self** (None): 

- **limit** (int): 

#### Returns

None

### `get_transcript`

Retrieve the transcript for a transcription.

Performs a GET request to ``/transcriptions/{transcription_id}/transcript``.

Raises:
    SonioxAPIError: When the API returns an error.

#### Signature

```python
get_transcript(transcription_id: str) -> TranscriptionTranscript
```

#### Parameters

- **self** (None): 

- **transcription_id** (str): 

#### Returns

TranscriptionTranscript

### `wait`

Poll a transcription until it leaves the queued or processing state.

Raises:
    SonioxAPIError: When the API returns an error.
    TimeoutError: Waiting for the transcription to finish exceeded `timeout_sec`.

#### Signature

```python
wait(transcription_id: str, *, interval_sec: float = 5.0, timeout_sec: float | None = None) -> Transcription
```

#### Parameters

- **self** (None): 

- **transcription_id** (str): 

- **interval_sec** (float): 

- **timeout_sec** (float | None): 

#### Returns

Transcription

### `transcribe_from_url`

Create a transcription from an audio URL.

Raises:
    SonioxAPIError: When the API returns an error.

#### Signature

```python
transcribe_from_url(*, model: str = DEFAULT_MODEL, audio_url: str, client_reference_id: str | None = None, config: CreateTranscriptionConfig | None = None) -> Transcription
```

#### Parameters

- **self** (None): 

- **model** (str): 

- **audio_url** (str): 

- **client_reference_id** (str | None): 

- **config** (CreateTranscriptionConfig | None): 

#### Returns

Transcription

### `transcribe_from_file_id`

Create a transcription from an existing uploaded file.

Raises:
    SonioxAPIError: When the API returns an error.

#### Signature

```python
transcribe_from_file_id(*, model: str = DEFAULT_MODEL, file_id: str, client_reference_id: str | None = None, config: CreateTranscriptionConfig | None = None) -> Transcription
```

#### Parameters

- **self** (None): 

- **model** (str): 

- **file_id** (str): 

- **client_reference_id** (str | None): 

- **config** (CreateTranscriptionConfig | None): 

#### Returns

Transcription

### `transcribe_from_file`

Upload a file and create a transcription from it.

Raises:
    SonioxAPIError: When the API returns an error.

#### Signature

```python
transcribe_from_file(*, model: str = DEFAULT_MODEL, file: BinaryIO | bytes | Path | str, filename: str | None = None, client_reference_id: str | None = None, config: CreateTranscriptionConfig | None = None) -> Transcription
```

#### Parameters

- **self** (None): 

- **model** (str): 

- **file** (BinaryIO | bytes | Path | str): 

- **filename** (str | None): 

- **client_reference_id** (str | None): 

- **config** (CreateTranscriptionConfig | None): 

#### Returns

Transcription

### `transcribe`

Create a transcription from a file, file ID, or audio URL.

Validates mutually exclusive inputs before submission.

Raises:
    SonioxAPIError: When the API returns an error.
    SonioxValidationError: When the payload fails validation.

#### Signature

```python
transcribe(*, model: str = DEFAULT_MODEL, audio_url: str | None = None, file_id: str | None = None, file: BinaryIO | bytes | Path | str | None = None, filename: str | None = None, client_reference_id: str | None = None, config: CreateTranscriptionConfig | None = None) -> Transcription
```

#### Parameters

- **self** (None): 

- **model** (str): 

- **audio_url** (str | None): 

- **file_id** (str | None): 

- **file** (BinaryIO | bytes | Path | str | None): 

- **filename** (str | None): 

- **client_reference_id** (str | None): 

- **config** (CreateTranscriptionConfig | None): 

#### Returns

Transcription

### `transcribe_file_with_webhook`

Upload a file, configure a webhook, and start transcription.

Raises:
    SonioxAPIError: When the API returns an error.

#### Signature

```python
transcribe_file_with_webhook(*, model: str = DEFAULT_MODEL, file: BinaryIO | bytes | Path | str, webhook_url: str, filename: str | None = None, client_reference_id: str | None = None, webhook_auth: WebhookAuthConfig | None = None, config: CreateTranscriptionConfig | None = None) -> Transcription
```

#### Parameters

- **self** (None): 

- **model** (str): 

- **file** (BinaryIO | bytes | Path | str): 

- **webhook_url** (str): 

- **filename** (str | None): 

- **client_reference_id** (str | None): 

- **webhook_auth** (WebhookAuthConfig | None): 

- **config** (CreateTranscriptionConfig | None): 

#### Returns

Transcription

### `transcribe_and_wait`

Create a transcription and wait for completion.

Returns a Transcription object after it is completed. Optionally deletes
the transcription and the uploaded file after completion.

Raises:
    SonioxAPIError: When the API returns an error.
    SonioxValidationError: When the payload fails validation.
    TimeoutError: Waiting for the transcription to finish exceeded `timeout_sec`.

#### Signature

```python
transcribe_and_wait(*, model: str = DEFAULT_MODEL, audio_url: str | None = None, file_id: str | None = None, file: BinaryIO | bytes | Path | str | None = None, filename: str | None = None, client_reference_id: str | None = None, delete_after: bool = False, wait_interval_sec: float = 5.0, wait_timeout_sec: float | None = None, config: CreateTranscriptionConfig | None = None) -> Transcription
```

#### Parameters

- **self** (None): 

- **model** (str): 

- **audio_url** (str | None): 

- **file_id** (str | None): 

- **file** (BinaryIO | bytes | Path | str | None): 

- **filename** (str | None): 

- **client_reference_id** (str | None): 

- **delete_after** (bool): 

- **wait_interval_sec** (float): 

- **wait_timeout_sec** (float | None): 

- **config** (CreateTranscriptionConfig | None): 

#### Returns

Transcription

### `transcribe_and_wait_with_tokens`

Create a transcription, wait for completion, and return the transcript.

Optionally deletes the transcription and uploaded file after completion.

Raises:
    SonioxAPIError: When the API returns an error.
    SonioxValidationError: When the payload fails validation.
    TimeoutError: Waiting for the transcription to finish exceeded `timeout_sec`.

#### Signature

```python
transcribe_and_wait_with_tokens(*, model: str = DEFAULT_MODEL, audio_url: str | None = None, file_id: str | None = None, file: BinaryIO | bytes | Path | str | None = None, filename: str | None = None, client_reference_id: str | None = None, delete_after: bool = False, wait_interval_sec: float = 5.0, wait_timeout_sec: float | None = None, config: CreateTranscriptionConfig | None = None) -> TranscriptionTranscript
```

#### Parameters

- **self** (None): 

- **model** (str): 

- **audio_url** (str | None): 

- **file_id** (str | None): 

- **file** (BinaryIO | bytes | Path | str | None): 

- **filename** (str | None): 

- **client_reference_id** (str | None): 

- **delete_after** (bool): 

- **wait_interval_sec** (float): 

- **wait_timeout_sec** (float | None): 

- **config** (CreateTranscriptionConfig | None): 

#### Returns

TranscriptionTranscript

---

## Class `SonioxWebhooksAPI`

### Attributes

- **_webhook_secret**: 

- **_webhook_header**: 

### `__init__`

#### Signature

```python
__init__(*, webhook_secret: str | None = None, webhook_header: str | None = None) -> None
```

#### Parameters

- **self** (None): 

- **webhook_secret** (str | None): 

- **webhook_header** (str | None): 

#### Returns

None

### `verify_signature`

Verify a webhook signature from headers.

Raises:
    InvalidWebhookSignatureError: When the webhook signature cannot be validated.

#### Signature

```python
verify_signature(headers: Headers, *, auth: WebhookAuthConfig | None = None) -> None
```

#### Parameters

- **self** (None): 

- **headers** (Headers): 

- **auth** (WebhookAuthConfig | None): 

#### Returns

None

### `unwrap`

Validate and parse a webhook payload.

Returns a WebhookEvent.

Raises:
    InvalidWebhookSignatureError: When the webhook signature cannot be validated.

#### Signature

```python
unwrap(payload: str | bytes, headers: Headers, *, auth: WebhookAuthConfig | None = None) -> WebhookEvent
```

#### Parameters

- **self** (None): 

- **payload** (str | bytes): 

- **headers** (Headers): 

- **auth** (WebhookAuthConfig | None): 

#### Returns

WebhookEvent

### `webhook_payload`

Return fields for webhook configuration when creating a transcription.

#### Signature

```python
webhook_payload(webhook_url: str, *, auth: WebhookAuthConfig | None = None) -> dict[str, str]
```

#### Parameters

- **self** (None): 

- **webhook_url** (str): 

- **auth** (WebhookAuthConfig | None): 

#### Returns

dict[str, str]