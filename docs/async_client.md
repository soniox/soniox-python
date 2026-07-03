---
title: "Async Client"
description: "Soniox Python SDK - Async Client Reference"
keywords: "AsyncSonioxClient, AsyncFilesAPI, AsyncSttAPI, AsyncTtsAPI, AsyncTtsModelsAPI, AsyncModelsAPI, AsyncUsageLogsAPI, AsyncConcurrencyLimitsAPI, AsyncAuthAPI, AsyncSonioxWebhooksAPI"
---

---

> **Sync mirror:** the synchronous `SonioxClient` exposes the same API as `AsyncSonioxClient` below - drop `await` from each call and treat `AsyncIterator[X]` return types as plain `Iterator[X]`. Only the async surface is documented here to avoid duplicating an otherwise identical reference. Realtime sessions have genuinely different sync/async patterns and are documented in the [Realtime Client](./realtime_client.md) page.

---

## AsyncSonioxClient

Asynchronous Soniox REST client exposing HTTP and realtime helpers.

<a id="asyncsonioxclient-constructor"></a>

### Constructor

```python
AsyncSonioxClient(api_key: str | None = None, api_base_url: str | None = None, websocket_base_url: str | None = None, tts_api_base_url: str | None = None, tts_websocket_base_url: str | None = None, timeout_sec: float | None = None, webhook_secret: str | None = None, webhook_signature_header: str | None = None, **client_kwargs: Any)
```

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `api_key` | `str \| None` | API key used for authentication. |
| `api_base_url` | `str \| None` | Base URL for Soniox REST API requests. |
| `websocket_base_url` | `str \| None` | Base URL for Soniox realtime WebSocket endpoint. |
| `tts_api_base_url` | `str \| None` | Base URL for Soniox Text-to-Speech REST API requests. |
| `tts_websocket_base_url` | `str \| None` | Base URL for Soniox Text-to-Speech realtime WebSocket endpoint. |
| `timeout_sec` | `float \| None` | Maximum wait time in seconds. |
| `webhook_secret` | `str \| None` | Webhook secret used for signature verification. |
| `webhook_signature_header` | `str \| None` | Webhook signature header name. |
| `client_kwargs` | `Any` | Additional HTTP client keyword arguments. |

**Returns**

`None`

<a id="asyncsonioxclient-properties"></a>

### Properties

| Property | Type | Description |
| ------ | ------ | ------ |
| `files` | `AsyncFilesAPI` | List of uploaded files. |
| `stt` | `AsyncSttAPI` | Speech-to-text API namespace. |
| `tts` | `AsyncTtsAPI` | Text-to-Speech API namespace |
| `models` | `AsyncModelsAPI` | Voice readiness status for each available model. |
| `tts_models` | `AsyncTtsModelsAPI` | - |
| `voices` | `AsyncVoicesAPI` | Voices supported by this model. |
| `usage_logs` | `AsyncUsageLogsAPI` | Per-request usage log entries ordered by end_time. |
| `concurrency_limits` | `AsyncConcurrencyLimitsAPI` | - |
| `auth` | `AsyncAuthAPI` | Authentication API namespace. |
| `webhooks` | `AsyncSonioxWebhooksAPI` | Webhook utilities API namespace. |
| `realtime` | `AsyncRealtimeAPI` | Entrypoint for async realtime helpers on AsyncSonioxClient. |

<a id="asyncsonioxclient-request"></a>

### request()

```python
request(method: str, path: str, *, params: Mapping[str, Any] | None = None, json: Any | None = None, data: Mapping[str, Any] | None = None, files: Mapping[str, Any] | None = None) -> httpx.Response
```

Perform a request against the configured Soniox REST endpoint.

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `method` | `str` | HTTP method to use for the request. |
| `path` | `str` | Relative API path for the request. |
| `params` | `Mapping[str, Any] \| None` | Query parameters for the request. |
| `json` | `Any \| None` | JSON request payload. |
| `data` | `Mapping[str, Any] \| None` | Form-encoded request payload. |
| `files` | `Mapping[str, Any] \| None` | Multipart file payload mapping. |

**Returns**

`httpx.Response`

***

<a id="asyncsonioxclient-aclose"></a>

### aclose()

```python
aclose() -> None
```

Close any outstanding async HTTP connections.

**Returns**

`None`

---

## AsyncFilesAPI

<a id="asyncfilesapi-constructor"></a>

### Constructor

```python
AsyncFilesAPI(client: AsyncSonioxClient)
```

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `client` | `AsyncSonioxClient` | Soniox client instance. |

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

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `limit` | `int` | Maximum number of files to return. |
| `cursor` | `str \| None` | Pagination cursor for the next page of results. |

**Returns**

`GetFilesResponse`

**Raises**

- `SonioxAPIError` When the API returns an error.

***

<a id="asyncfilesapi-count"></a>

### count()

```python
count() -> GetFilesCountResponse
```

Return a breakdown of uploaded file counts.

Performs a GET request to ``/files/count``.

**Returns**

`GetFilesCountResponse`

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

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `limit` | `int` | Maximum number of files to return. |

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

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `file_id` | `str` | ID of a previously uploaded file. |

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

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `file_id` | `str` | ID of a previously uploaded file. |

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

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `file_id` | `str` | ID of a previously uploaded file. |

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

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `file_id` | `str` | ID of a previously uploaded file. |

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

Uploaded files are automatically deleted 30 days after upload.

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `file` | `BinaryIO \| bytes \| Path \| str` | File input to upload or transcribe. |
| `filename` | `str \| None` | Filename associated with uploaded file data. |
| `client_reference_id` | `str \| None` | Optional tracking identifier string. Does not need to be unique |

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

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `limit` | `int` | Maximum number of files to return. |

**Returns**

`None`

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

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `client` | `AsyncSonioxClient` | Soniox client instance. |

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

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `limit` | `int` | Maximum number of transcriptions to return. |
| `cursor` | `str \| None` | Pagination cursor for the next page of results. |

**Returns**

`GetTranscriptionsResponse`

**Raises**

- `SonioxAPIError` When the API returns an error.

***

<a id="asyncsttapi-count"></a>

### count()

```python
count() -> GetTranscriptionsCountResponse
```

Return a breakdown of transcription counts.

Performs a GET request to ``/transcriptions/count``.

**Returns**

`GetTranscriptionsCountResponse`

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

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `limit` | `int` | Maximum number of transcriptions to return. |

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

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `limit` | `int` | Maximum number of transcriptions to return. |

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

Transcriptions are automatically deleted 30 days after creation.

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `model` | `str` | Speech-to-text model to use. |
| `file_id` | `str \| None` | ID of a previously uploaded file. |
| `audio_url` | `str \| None` | Publicly accessible audio URL. |
| `client_reference_id` | `str \| None` | Optional tracking identifier. |
| `config` | `CreateTranscriptionConfig \| None` | Configuration options for this operation. |

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

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `transcription_id` | `str` | Transcription identifier. |

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

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `transcription_id` | `str` | Transcription identifier. |

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

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `transcription_id` | `str` | Transcription identifier. |

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

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `transcription_id` | `str` | Transcription identifier. |

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

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `transcription_id` | `str` | Transcription identifier. |

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

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `limit` | `int` | Maximum number of transcriptions to return. |

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

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `transcription_id` | `str` | Transcription identifier. |

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

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `transcription_id` | `str` | Transcription identifier. |
| `interval_sec` | `float` | Polling interval in seconds. |
| `timeout_sec` | `float \| None` | Maximum wait time in seconds. |

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

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `model` | `str` | Speech-to-text model to use. |
| `audio_url` | `str` | Publicly accessible audio URL. |
| `client_reference_id` | `str \| None` | Optional tracking identifier. |
| `config` | `CreateTranscriptionConfig \| None` | Configuration options for this operation. |

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

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `model` | `str` | Speech-to-text model to use. |
| `file_id` | `str` | ID of a previously uploaded file. |
| `client_reference_id` | `str \| None` | Optional tracking identifier. |
| `config` | `CreateTranscriptionConfig \| None` | Configuration options for this operation. |

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

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `model` | `str` | Speech-to-text model to use. |
| `file` | `BinaryIO \| bytes \| Path \| str` | File input to upload or transcribe. |
| `filename` | `str \| None` | Filename associated with uploaded file data. |
| `client_reference_id` | `str \| None` | Optional tracking identifier. |
| `config` | `CreateTranscriptionConfig \| None` | Configuration options for this operation. |

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

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `model` | `str` | Speech-to-text model to use. |
| `audio_url` | `str \| None` | Publicly accessible audio URL. |
| `file_id` | `str \| None` | ID of a previously uploaded file. |
| `file` | `BinaryIO \| bytes \| Path \| str \| None` | File input to upload or transcribe. |
| `filename` | `str \| None` | Filename associated with uploaded file data. |
| `client_reference_id` | `str \| None` | Optional tracking identifier. |
| `config` | `CreateTranscriptionConfig \| None` | Configuration options for this operation. |

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

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `model` | `str` | Speech-to-text model to use. |
| `file` | `BinaryIO \| bytes \| Path \| str` | File input to upload or transcribe. |
| `webhook_url` | `str` | URL to receive webhook notifications. |
| `filename` | `str \| None` | Filename associated with uploaded file data. |
| `client_reference_id` | `str \| None` | Optional tracking identifier. |
| `webhook_auth` | `WebhookAuthConfig \| None` | Webhook authentication configuration. |
| `config` | `CreateTranscriptionConfig \| None` | Configuration options for this operation. |

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

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `model` | `str` | Speech-to-text model to use. |
| `audio_url` | `str \| None` | Publicly accessible audio URL. |
| `file_id` | `str \| None` | ID of a previously uploaded file. |
| `file` | `BinaryIO \| bytes \| Path \| str \| None` | File input to upload or transcribe. |
| `filename` | `str \| None` | Filename associated with uploaded file data. |
| `client_reference_id` | `str \| None` | Optional tracking identifier. |
| `delete_after` | `bool` | Whether to delete created resources after completion. |
| `wait_interval_sec` | `float` | Polling interval in seconds while waiting. |
| `wait_timeout_sec` | `float \| None` | Maximum wait time in seconds while polling. |
| `config` | `CreateTranscriptionConfig \| None` | Configuration options for this operation. |

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

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `model` | `str` | Speech-to-text model to use. |
| `audio_url` | `str \| None` | Publicly accessible audio URL. |
| `file_id` | `str \| None` | ID of a previously uploaded file. |
| `file` | `BinaryIO \| bytes \| Path \| str \| None` | File input to upload or transcribe. |
| `filename` | `str \| None` | Filename associated with uploaded file data. |
| `client_reference_id` | `str \| None` | Optional tracking identifier. |
| `delete_after` | `bool` | Whether to delete created resources after completion. |
| `wait_interval_sec` | `float` | Polling interval in seconds while waiting. |
| `wait_timeout_sec` | `float \| None` | Maximum wait time in seconds while polling. |
| `config` | `CreateTranscriptionConfig \| None` | Configuration options for this operation. |

**Returns**

`TranscriptionTranscript`

**Raises**

- `SonioxAPIError` When the API returns an error.
- `SonioxValidationError` When the payload fails validation.
- `TimeoutError` Waiting for the transcription to finish exceeded `timeout_sec`.

***

<a id="asyncsttapi-translate_from_url"></a>

### translate_from_url()

```python
translate_from_url(*, audio_url: str, to: LanguageCode | None = None, source: LanguageCode | None = None, between: tuple[LanguageCode, LanguageCode] | None = None, model: str = DEFAULT_MODEL, client_reference_id: str | None = None, config: CreateTranscriptionConfig | None = None) -> Transcription
```

Translate audio at a URL.

Provide exactly one of ``to`` (one-way) or ``between`` (two-way). ``source`` is
an optional language hint and is only valid with ``to``.

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `audio_url` | `str` | Publicly accessible audio URL. |
| `to` | `LanguageCode \| None` | - |
| `source` | `LanguageCode \| None` | The source term to translate. |
| `between` | `tuple[LanguageCode, LanguageCode] \| None` | - |
| `model` | `str` | Speech-to-text model to use. |
| `client_reference_id` | `str \| None` | Optional tracking identifier. |
| `config` | `CreateTranscriptionConfig \| None` | Configuration options for this operation. |

**Returns**

`Transcription`

**Raises**

- `SonioxAPIError` When the API returns an error.
- `SonioxValidationError` When the translate kwargs are invalid.

***

<a id="asyncsttapi-translate_from_file_id"></a>

### translate_from_file_id()

```python
translate_from_file_id(*, file_id: str, to: LanguageCode | None = None, source: LanguageCode | None = None, between: tuple[LanguageCode, LanguageCode] | None = None, model: str = DEFAULT_MODEL, client_reference_id: str | None = None, config: CreateTranscriptionConfig | None = None) -> Transcription
```

Translate an already-uploaded file.

Provide exactly one of ``to`` (one-way) or ``between`` (two-way). ``source`` is
an optional language hint and is only valid with ``to``.

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `file_id` | `str` | ID of a previously uploaded file. |
| `to` | `LanguageCode \| None` | - |
| `source` | `LanguageCode \| None` | The source term to translate. |
| `between` | `tuple[LanguageCode, LanguageCode] \| None` | - |
| `model` | `str` | Speech-to-text model to use. |
| `client_reference_id` | `str \| None` | Optional tracking identifier. |
| `config` | `CreateTranscriptionConfig \| None` | Configuration options for this operation. |

**Returns**

`Transcription`

**Raises**

- `SonioxAPIError` When the API returns an error.
- `SonioxValidationError` When the translate kwargs are invalid.

***

<a id="asyncsttapi-translate_from_file"></a>

### translate_from_file()

```python
translate_from_file(*, file: BinaryIO | bytes | Path | str, to: LanguageCode | None = None, source: LanguageCode | None = None, between: tuple[LanguageCode, LanguageCode] | None = None, filename: str | None = None, model: str = DEFAULT_MODEL, client_reference_id: str | None = None, config: CreateTranscriptionConfig | None = None) -> Transcription
```

Upload a file and translate it.

Provide exactly one of ``to`` (one-way) or ``between`` (two-way). ``source`` is
an optional language hint and is only valid with ``to``.

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `file` | `BinaryIO \| bytes \| Path \| str` | File input to upload or transcribe. |
| `to` | `LanguageCode \| None` | - |
| `source` | `LanguageCode \| None` | The source term to translate. |
| `between` | `tuple[LanguageCode, LanguageCode] \| None` | - |
| `filename` | `str \| None` | Filename associated with uploaded file data. |
| `model` | `str` | Speech-to-text model to use. |
| `client_reference_id` | `str \| None` | Optional tracking identifier. |
| `config` | `CreateTranscriptionConfig \| None` | Configuration options for this operation. |

**Returns**

`Transcription`

**Raises**

- `SonioxAPIError` When the API returns an error.
- `SonioxValidationError` When the translate kwargs are invalid.

***

<a id="asyncsttapi-translate"></a>

### translate()

```python
translate(*, to: LanguageCode | None = None, source: LanguageCode | None = None, between: tuple[LanguageCode, LanguageCode] | None = None, audio_url: str | None = None, file_id: str | None = None, file: BinaryIO | bytes | Path | str | None = None, filename: str | None = None, model: str = DEFAULT_MODEL, client_reference_id: str | None = None, config: CreateTranscriptionConfig | None = None) -> Transcription
```

Translate audio from a file, file ID, or URL.

Provide exactly one of ``to`` (one-way) or ``between`` (two-way). ``source`` is
an optional language hint and is only valid with ``to``. Convenience over
``transcribe()`` that fills in the ``translation`` config and forces
``enable_language_identification=True``.

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `to` | `LanguageCode \| None` | - |
| `source` | `LanguageCode \| None` | The source term to translate. |
| `between` | `tuple[LanguageCode, LanguageCode] \| None` | - |
| `audio_url` | `str \| None` | Publicly accessible audio URL. |
| `file_id` | `str \| None` | ID of a previously uploaded file. |
| `file` | `BinaryIO \| bytes \| Path \| str \| None` | File input to upload or transcribe. |
| `filename` | `str \| None` | Filename associated with uploaded file data. |
| `model` | `str` | Speech-to-text model to use. |
| `client_reference_id` | `str \| None` | Optional tracking identifier. |
| `config` | `CreateTranscriptionConfig \| None` | Configuration options for this operation. |

**Returns**

`Transcription`

**Raises**

- `SonioxAPIError` When the API returns an error.
- `SonioxValidationError` When the payload or translate kwargs are invalid.

***

<a id="asyncsttapi-translate_and_wait"></a>

### translate_and_wait()

```python
translate_and_wait(*, to: LanguageCode | None = None, source: LanguageCode | None = None, between: tuple[LanguageCode, LanguageCode] | None = None, audio_url: str | None = None, file_id: str | None = None, file: BinaryIO | bytes | Path | str | None = None, filename: str | None = None, model: str = DEFAULT_MODEL, client_reference_id: str | None = None, delete_after: bool = False, wait_interval_sec: float = 5.0, wait_timeout_sec: float | None = None, config: CreateTranscriptionConfig | None = None) -> Transcription
```

Translate and wait for completion. Returns the finished ``Transcription``.

Provide exactly one of ``to`` (one-way) or ``between`` (two-way). ``source`` is
an optional language hint and is only valid with ``to``.

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `to` | `LanguageCode \| None` | - |
| `source` | `LanguageCode \| None` | The source term to translate. |
| `between` | `tuple[LanguageCode, LanguageCode] \| None` | - |
| `audio_url` | `str \| None` | Publicly accessible audio URL. |
| `file_id` | `str \| None` | ID of a previously uploaded file. |
| `file` | `BinaryIO \| bytes \| Path \| str \| None` | File input to upload or transcribe. |
| `filename` | `str \| None` | Filename associated with uploaded file data. |
| `model` | `str` | Speech-to-text model to use. |
| `client_reference_id` | `str \| None` | Optional tracking identifier. |
| `delete_after` | `bool` | Whether to delete created resources after completion. |
| `wait_interval_sec` | `float` | Polling interval in seconds while waiting. |
| `wait_timeout_sec` | `float \| None` | Maximum wait time in seconds while polling. |
| `config` | `CreateTranscriptionConfig \| None` | Configuration options for this operation. |

**Returns**

`Transcription`

**Raises**

- `SonioxAPIError` When the API returns an error.
- `SonioxValidationError` When the payload or translate kwargs are invalid.
- `TimeoutError` Waiting for the transcription to finish exceeded `wait_timeout_sec`.

***

<a id="asyncsttapi-translate_and_wait_with_tokens"></a>

### translate_and_wait_with_tokens()

```python
translate_and_wait_with_tokens(*, to: LanguageCode | None = None, source: LanguageCode | None = None, between: tuple[LanguageCode, LanguageCode] | None = None, audio_url: str | None = None, file_id: str | None = None, file: BinaryIO | bytes | Path | str | None = None, filename: str | None = None, model: str = DEFAULT_MODEL, client_reference_id: str | None = None, delete_after: bool = False, wait_interval_sec: float = 5.0, wait_timeout_sec: float | None = None, config: CreateTranscriptionConfig | None = None) -> TranscriptionTranscript
```

Translate, wait for completion, and return the transcript with tokens.

Provide exactly one of ``to`` (one-way) or ``between`` (two-way). ``source`` is
an optional language hint and is only valid with ``to``. Optionally deletes the
transcription and uploaded file after completion.

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `to` | `LanguageCode \| None` | - |
| `source` | `LanguageCode \| None` | The source term to translate. |
| `between` | `tuple[LanguageCode, LanguageCode] \| None` | - |
| `audio_url` | `str \| None` | Publicly accessible audio URL. |
| `file_id` | `str \| None` | ID of a previously uploaded file. |
| `file` | `BinaryIO \| bytes \| Path \| str \| None` | File input to upload or transcribe. |
| `filename` | `str \| None` | Filename associated with uploaded file data. |
| `model` | `str` | Speech-to-text model to use. |
| `client_reference_id` | `str \| None` | Optional tracking identifier. |
| `delete_after` | `bool` | Whether to delete created resources after completion. |
| `wait_interval_sec` | `float` | Polling interval in seconds while waiting. |
| `wait_timeout_sec` | `float \| None` | Maximum wait time in seconds while polling. |
| `config` | `CreateTranscriptionConfig \| None` | Configuration options for this operation. |

**Returns**

`TranscriptionTranscript`

**Raises**

- `SonioxAPIError` When the API returns an error.
- `SonioxValidationError` When the payload or translate kwargs are invalid.
- `TimeoutError` Waiting for the transcription to finish exceeded `wait_timeout_sec`.

---

## AsyncTtsAPI

<a id="asyncttsapi-constructor"></a>

### Constructor

```python
AsyncTtsAPI(client: AsyncSonioxClient)
```

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `client` | `AsyncSonioxClient` | Soniox client instance. |

**Returns**

`None`

<a id="asyncttsapi-generate"></a>

### generate()

```python
generate(*, text: str, voice: str, model: str = DEFAULT_MODEL, config: CreateTtsConfig | None = None, language: str | None = None, audio_format: TtsAudioFormat | None = None, sample_rate: TtsSampleRate | None = None, bitrate: TtsBitrate | None = None) -> bytes
```

Generate speech audio from text and return raw audio bytes.

Performs a POST request to the TTS REST endpoint.

``audio_format``/``sample_rate``/``bitrate`` are deprecated; set them on
``CreateTtsConfig`` instead. Pass ``language`` explicitly — relying on the default
("en") is deprecated and ``language`` will be required in the next major release.

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `text` | `str` | Longer free-form background text, prior interaction history, reference documents, or meeting notes. |
| `voice` | `str` | Voice identifier to generate speech audio with. |
| `model` | `str` | Speech-to-text model to use. |
| `config` | `CreateTtsConfig \| None` | Configuration options for this operation. |
| `language` | `str \| None` | Language code for Text-to-Speech (e.g., "en"). |
| `audio_format` | `TtsAudioFormat \| None` | Audio format for realtime transcription. |
| `sample_rate` | `TtsSampleRate \| None` | Audio sample rate in Hz. |
| `bitrate` | `TtsBitrate \| None` | Output bitrate in bits-per-second for compressed formats. |

**Returns**

`bytes`

**Raises**

- `SonioxAPIError` When the API returns an error.

***

<a id="asyncttsapi-generate_to_file"></a>

### generate_to_file()

```python
generate_to_file(output: BinaryIO | Path | str, *, text: str, voice: str = DEFAULT_VOICE, model: str = DEFAULT_MODEL, config: CreateTtsConfig | None = None, language: str | None = None, audio_format: TtsAudioFormat | None = None, sample_rate: TtsSampleRate | None = None, bitrate: TtsBitrate | None = None) -> int
```

Generate speech audio from text and write the audio bytes to a file-like output.

``audio_format``/``sample_rate``/``bitrate`` are deprecated; set them on
``CreateTtsConfig`` instead. Pass ``language`` explicitly — relying on the default
("en") is deprecated and ``language`` will be required in the next major release.

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `output` | `BinaryIO \| Path \| str` | - |
| `text` | `str` | Longer free-form background text, prior interaction history, reference documents, or meeting notes. |
| `voice` | `str` | Voice identifier to generate speech audio with. |
| `model` | `str` | Speech-to-text model to use. |
| `config` | `CreateTtsConfig \| None` | Configuration options for this operation. |
| `language` | `str \| None` | Language code for Text-to-Speech (e.g., "en"). |
| `audio_format` | `TtsAudioFormat \| None` | Audio format for realtime transcription. |
| `sample_rate` | `TtsSampleRate \| None` | Audio sample rate in Hz. |
| `bitrate` | `TtsBitrate \| None` | Output bitrate in bits-per-second for compressed formats. |

**Returns**

`int`

Number of bytes written.

---

## AsyncTtsModelsAPI

<a id="asyncttsmodelsapi-constructor"></a>

### Constructor

```python
AsyncTtsModelsAPI(client: AsyncSonioxClient)
```

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `client` | `AsyncSonioxClient` | Soniox client instance. |

**Returns**

`None`

<a id="asyncttsmodelsapi-list"></a>

### list()

```python
list() -> GetTtsModelsResponse
```

List available Text-to-Speech models.

Performs a GET request to ``/tts-models``.

**Returns**

`GetTtsModelsResponse`

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

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `client` | `AsyncSonioxClient` | Soniox client instance. |

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

## AsyncUsageLogsAPI

<a id="asyncusagelogsapi-constructor"></a>

### Constructor

```python
AsyncUsageLogsAPI(client: AsyncSonioxClient)
```

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `client` | `AsyncSonioxClient` | Soniox client instance. |

**Returns**

`None`

<a id="asyncusagelogsapi-list"></a>

### list()

```python
list(start_time: str, end_time: str, limit: int = 1000, sort: UsageLogsSort = 'end_time_asc', cursor: str | None = None) -> GetUsageLogsResponse
```

List usage-log entries for a time window.

Performs a GET request to ``/usage-logs``.

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `start_time` | `str` | Start of the window (inclusive). Filters by request end time. |
| `end_time` | `str` | End of the window (exclusive). Filters by request end time. |
| `limit` | `int` | Maximum number of entries to return (1–1000). |
| `sort` | `UsageLogsSort` | Sort order by end_time. |
| `cursor` | `str \| None` | Pagination cursor for the next page. |

**Returns**

`GetUsageLogsResponse`

**Raises**

- `SonioxAPIError` When the API returns an error.

***

<a id="asyncusagelogsapi-list_all"></a>

### list_all()

```python
list_all(start_time: str, end_time: str, limit: int = 1000, sort: UsageLogsSort = 'end_time_asc') -> AsyncGenerator[UsageLogEntry, None]
```

Iterate through all usage-log entries across all pages.

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `start_time` | `str` | Start of the window (inclusive). Filters by request end time. |
| `end_time` | `str` | End of the window (exclusive). Filters by request end time. |
| `limit` | `int` | Maximum number of entries to return (1–1000). |
| `sort` | `UsageLogsSort` | Sort order by end_time. |

**Returns**

`AsyncGenerator[UsageLogEntry, None]`

---

## AsyncConcurrencyLimitsAPI

<a id="asyncconcurrencylimitsapi-constructor"></a>

### Constructor

```python
AsyncConcurrencyLimitsAPI(client: AsyncSonioxClient)
```

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `client` | `AsyncSonioxClient` | Soniox client instance. |

**Returns**

`None`

<a id="asyncconcurrencylimitsapi-get"></a>

### get()

```python
get() -> GetConcurrencyLimitsResponse
```

Get current concurrent sessions and configured limits.

Performs a GET request to ``/concurrency-limits``.

**Returns**

`GetConcurrencyLimitsResponse`

Project- and organization-scoped current counts and configured
limits for realtime STT and TTS sessions.

**Raises**

- `SonioxAPIError` When the API returns an error.

---

## AsyncAuthAPI

<a id="asyncauthapi-constructor"></a>

### Constructor

```python
AsyncAuthAPI(client: AsyncSonioxClient)
```

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `client` | `AsyncSonioxClient` | Soniox client instance. |

**Returns**

`None`

<a id="asyncauthapi-create_temporary_api_key"></a>

### create_temporary_api_key()

```python
create_temporary_api_key(*, usage_type: TemporaryApiKeyUsageType = 'transcribe_websocket', expires_in_seconds: int = 5 * 60, client_reference_id: str | None = None, single_use: bool | None = None, max_session_duration_seconds: int | None = None) -> CreateTemporaryApiKeyResponse
```

Create a temporary API key.

Performs a POST request to ``/auth/temporary-api-key``.

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `usage_type` | `TemporaryApiKeyUsageType` | Intended usage of the temporary API key. |
| `expires_in_seconds` | `int` | Duration in seconds until the temporary API key expires |
| `client_reference_id` | `str \| None` | Optional tracking identifier string. Does not need to be unique |
| `single_use` | `bool \| None` | When true, restricts the temporary API key to a single use. |
| `max_session_duration_seconds` | `int \| None` | Maximum connection duration in seconds for WebSocket and TTS HTTP streaming endpoints. |

**Returns**

`CreateTemporaryApiKeyResponse`

**Raises**

- `SonioxAPIError` When the API returns an error.

---

## AsyncSonioxWebhooksAPI