---
title: soniox.api.async_transcriptions
description: Description for async_transcriptions
keywords: annotations, asyncio, time, Path, TYPE_CHECKING, BinaryIO, SonioxNotFoundError, SonioxValidationError, CreateTranscriptionConfig, GetTranscriptionsPayload, GetTranscriptionsResponse, Transcription, TranscriptionTranscript, WebhookAuthConfig, build_create_payload, ensure_success, parse_async_response, AsyncSonioxClient, DEFAULT_MODEL, AsyncTranscriptionsAPI
---


---

## Class `AsyncTranscriptionsAPI`

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

### `delete_all`

Delete all transcriptions.

Iterates through all pages and deletes each transcription.

Raises:
    SonioxAPIError: When the API returns an error.

#### Signature

```python
delete_all(*, limit: int = 100) -> None
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