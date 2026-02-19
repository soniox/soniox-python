---
title: "Types"
description: "Soniox Python SDK - Types Reference"
keywords: "Token, ApiError, ApiErrorValidationError, CreateTemporaryApiKeyPayload, CreateTemporaryApiKeyResponse, CreateTranscriptionPayload, CreateTranscriptionConfig, File, GetFilesPayload, GetFilesResponse, GetModelsResponse, GetTranscriptionsPayload, GetTranscriptionsResponse, Model, StructuredContext, StructuredContextGeneralItem, StructuredContextTranslationTerm, Transcription, TranscriptionStatus, TranscriptionTranscript, TranslationConfig, TranslationTarget, TranslationType, TemporaryApiKeyUsageType, UploadFilePayload, RealtimeEvent, RealtimeSTTConfig, Headers, WebhookAuthConfig, WebhookEvent"
---

---

## Token

Token metadata emitted during realtime streaming transcriptions.

<a id="token-properties"></a>

### Properties

| Property | Type | Description |
| ------ | ------ | ------ |
| `text` | `str` | The transcribed text. |
| `start_ms` | `int \| None` | Start time in milliseconds relative to audio start. |
| `end_ms` | `int \| None` | End time in milliseconds relative to audio start. |
| `confidence` | `float \| None` | Confidence score (0.0 to 1.0). |
| `is_final` | `bool \| None` | Whether this is a finalized token. |
| `speaker` | `str \| None` | Speaker identifier (if diarization enabled). |
| `translation_status` | `str \| None` | Translation status of this token. |
| `language` | `str \| None` | Detected language code (if language identification enabled). |
| `source_language` | `str \| None` | Source language for translated tokens. |

---

## ApiError

Structured representation of a non-2xx API response payload.

<a id="apierror-properties"></a>

### Properties

| Property | Type | Description |
| ------ | ------ | ------ |
| `status_code` | `int` | HTTP status code. |
| `error_type` | `str` | High-level error code (e.g., 'bad_request', 'quota_exceeded') for programmatic handling. |
| `message` | `str` | Detailed error message describing the failure. |
| `validation_errors` | `list[ApiErrorValidationError]` | List of specific field validation failures, if applicable. |
| `request_id` | `str \| None` | Unique identifier for the request, useful for troubleshooting. |

---

## ApiErrorValidationError

Details a single validation error reported by the Soniox API.

<a id="apierrorvalidationerror-properties"></a>

### Properties

| Property | Type | Description |
| ------ | ------ | ------ |
| `error_type` | `str` | The category of validation error. |
| `location` | `str` | The location of the error, e.g. ['body', 'audio_url']. |
| `message` | `str` | A human-readable description of the validation failure. |

---

## CreateTemporaryApiKeyPayload

Payload for requesting a temporary API key (e.g., websocket).

<a id="createtemporaryapikeypayload-properties"></a>

### Properties

| Property | Type | Description |
| ------ | ------ | ------ |
| `usage_type` | `TemporaryApiKeyUsageType` | Intended usage of the temporary API key. |
| `expires_in_seconds` | `int` | Duration in seconds until the temporary API key expires |
| `client_reference_id` | `str \| None` | Optional tracking identifier string. Does not need to be unique |

---

## CreateTemporaryApiKeyResponse

Response data for a temp API key request.

<a id="createtemporaryapikeyresponse-properties"></a>

### Properties

| Property | Type | Description |
| ------ | ------ | ------ |
| `api_key` | `str` | Created temporary API key. |
| `expires_at` | `datetime` | UTC timestamp indicating when generated temporary API key will expire |

---

## CreateTranscriptionPayload

Payload sent to create an asynchronous transcription job.

<a id="createtranscriptionpayload-properties"></a>

### Properties

| Property | Type | Description |
| ------ | ------ | ------ |
| `model` | `str` | Speech-to-text model to use. |
| `audio_url` | `str \| None` | URL of a publicly accessible audio file. |
| `file_id` | `str \| None` | ID of a previously uploaded file (UUID). |
| `language_hints` | `list[str] \| None` | Array of expected ISO language codes to bias recognition. |
| `language_hints_strict` | `bool \| None` | When true, model relies more heavily on language hints (best results with one language hint set). |
| `enable_speaker_diarization` | `bool \| None` | Enable speaker diarization to identify different speakers. |
| `enable_language_identification` | `bool \| None` | Enable automatic language identification. |
| `translation` | `TranslationConfig \| None` | Translation configuration. |
| `context` | `StructuredContext \| None` | Additional context to improve transcription accuracy and formatting of specialized terms. |
| `webhook_url` | `str \| None` | URL to receive webhook notifications when transcription is completed or fails. |
| `webhook_auth_header_name` | `str \| None` | Name of the authentication header sent with webhook notifications |
| `webhook_auth_header_value` | `str \| None` | Authentication header value sent with webhook notifications. |
| `client_reference_id` | `str \| None` | Optional tracking identifier. |

---

## CreateTranscriptionConfig

Helper config used when building transcription payloads.

<a id="createtranscriptionconfig-properties"></a>

### Properties

| Property | Type | Description |
| ------ | ------ | ------ |
| `model` | `str \| None` | Speech-to-text model to use. |
| `language_hints` | `list[str] \| None` | Array of expected ISO language codes to bias recognition. |
| `language_hints_strict` | `bool \| None` | When true, model relies more heavily on language hints. |
| `enable_speaker_diarization` | `bool \| None` | Enable speaker diarization to identify different speakers. |
| `enable_language_identification` | `bool \| None` | Enable automatic language identification |
| `translation` | `TranslationConfig \| None` | Translation configuration |
| `context` | `StructuredContext \| None` | Additional context to improve transcription accuracy and formatting of specialized terms. |
| `webhook_url` | `str \| None` | URL to receive webhook notifications when transcription is completed or fails. |
| `webhook_auth_header_name` | `str \| None` | Name of the authentication header sent with webhook notifications |
| `webhook_auth_header_value` | `str \| None` | Authentication header value sent with webhook notifications |
| `client_reference_id` | `str \| None` | Optional tracking identifier |

---

## File

Metadata describing an uploaded file in the Soniox API.

<a id="file-properties"></a>

### Properties

| Property | Type | Description |
| ------ | ------ | ------ |
| `id` | `str` | Unique identifier of the file (UUID). |
| `filename` | `str` | Name of the file. |
| `size` | `int` | Size of the file in bytes. |
| `created_at` | `datetime` | UTC timestamp indicating when the file was uploaded. |
| `client_reference_id` | `str \| None` | Optional tracking identifier string. |

---

## GetFilesPayload

Parameters accepted by the file listing endpoint.

<a id="getfilespayload-properties"></a>

### Properties

| Property | Type | Description |
| ------ | ------ | ------ |
| `limit` | `int` | Maximum number of files to return. |
| `cursor` | `str \| None` | Pagination cursor for the next page of results. |

---

## GetFilesResponse

Paginated response returned when listing uploaded files.

<a id="getfilesresponse-properties"></a>

### Properties

| Property | Type | Description |
| ------ | ------ | ------ |
| `files` | `list[File]` | List of uploaded files. |
| `next_page_cursor` | `str \| None` | A pagination token that references the next page of results. When None, no additional results are available. |

---

## GetModelsResponse

Response returned when listing available models.

<a id="getmodelsresponse-properties"></a>

### Properties

| Property | Type | Description |
| ------ | ------ | ------ |
| `models` | `list[Model]` | List of all available models. |

---

## GetTranscriptionsPayload

Parameters for listing transcription jobs.

<a id="gettranscriptionspayload-properties"></a>

### Properties

| Property | Type | Description |
| ------ | ------ | ------ |
| `limit` | `int` | Maximum number of transcriptions to return. |
| `cursor` | `str \| None` | Pagination cursor for the next page of results. |

---

## GetTranscriptionsResponse

Paginated response for transcription listings.

<a id="gettranscriptionsresponse-properties"></a>

### Properties

| Property | Type | Description |
| ------ | ------ | ------ |
| `transcriptions` | `list[Transcription]` | List of transcriptions. |
| `next_page_cursor` | `str \| None` | A pagination token that references the next page of results. When None, no additional results are available. |

---

## Model

Describes a Soniox transcription model.

<a id="model-properties"></a>

### Properties

| Property | Type | Description |
| ------ | ------ | ------ |
| `id` | `str` | Unique identifier of the model. |
| `aliased_model_id` | `str \| None` | If this is an alias, the id of the aliased model. None for non-alias models. |
| `name` | `str` | Name of the model. |
| `context_version` | `int \| None` | Version of context supported. |
| `transcription_mode` | `TranscriptionMode` | Transcription mode of the model. |
| `languages` | `list[Language]` | List of languages supported by the model. |
| `supports_language_hints_strict` | `bool` | If model supports 'language_hints_strict' option. |
| `translation_targets` | `list[TranslationTarget]` | List of supported one-way translation targets. If list is empty, check for one_way_translation field. |
| `two_way_translation_pairs` | `list[str]` | List of supported two-way translation pairs. If list is empty, check for one_way_translation field. |
| `one_way_translation` | `str \| None` | When contains string 'all_languages', any language from languages can be used |
| `two_way_translation` | `str \| None` | When contains string 'all_languages',' any language pair from languages can be used |

---

## StructuredContext

Optional structured context provided to the transcription engine.

<a id="structuredcontext-properties"></a>

### Properties

| Property | Type | Description |
| ------ | ------ | ------ |
| `general` | `list[StructuredContextGeneralItem] \| None` | Structured key-value pairs describing domain, topic, intent, participant names, etc. |
| `text` | `str \| None` | Longer free-form background text, prior interaction history, reference documents, or meeting notes. |
| `terms` | `list[str] \| None` | Domain-specific or uncommon words to recognize. |
| `translation_terms` | `list[StructuredContextTranslationTerm] \| None` | Custom translations for ambiguous terms. |

---

## StructuredContextGeneralItem

Single general context key/value pair for transcription context.

<a id="structuredcontextgeneralitem-properties"></a>

### Properties

| Property | Type | Description |
| ------ | ------ | ------ |
| `key` | `str` | The key describing the context type (e.g., "domain", "topic", "doctor"). |
| `value` | `str` | The value for the context key. |

---

## StructuredContextTranslationTerm

Defines a translation term mapping used in structured context.

<a id="structuredcontexttranslationterm-properties"></a>

### Properties

| Property | Type | Description |
| ------ | ------ | ------ |
| `source` | `str` | The source term to translate. |
| `target` | `str` | The target translation for the term. |

---

## Transcription

Represents a transcription job tracked by Soniox.

<a id="transcription-properties"></a>

### Properties

| Property | Type | Description |
| ------ | ------ | ------ |
| `id` | `str` | Unique identifier of the transcription (UUID). |
| `status` | `TranscriptionStatus` | Current status of the transcription. |
| `created_at` | `datetime` | UTC timestamp when the transcription was created. |
| `model` | `str` | Speech-to-text model used. |
| `audio_url` | `str \| None` | URL of the audio file being transcribed. |
| `file_id` | `str \| None` | ID of the uploaded file being transcribed (UUID). |
| `filename` | `str` | Name of the file being transcribed. |
| `language_hints` | `list[str] \| None` | Expected languages in the audio. If not specified, languages are automatically detected. |
| `enable_speaker_diarization` | `bool` | When true, speakers are identified and separated in the transcription output. |
| `enable_language_identification` | `bool` | When true, language is detected for each part of the transcription. |
| `audio_duration_ms` | `int \| None` | Duration of the audio in milliseconds. Only available after processing begins. |
| `error_type` | `str \| None` | Error type if transcription failed. None for successful or in-progress transcriptions. |
| `error_message` | `str \| None` | Error message if transcription failed. None for successful or in-progress transcriptions. |
| `webhook_url` | `str \| None` | URL to receive webhook notifications when transcription is completed or fails. |
| `webhook_auth_header_name` | `str \| None` | Name of the authentication header sent with webhook notifications. |
| `webhook_auth_header_value` | `str \| None` | Authentication header value. Always returned masked. |
| `webhook_status_code` | `int \| None` | HTTP status code received from your server when webhook was delivered. None if not yet sent. |
| `client_reference_id` | `str \| None` | Optional tracking identifier. |

---

<a id="transcriptionstatus"></a>

## TranscriptionStatus

```python
TranscriptionStatus = Literal["queued", "processing", "completed", "error"]
```

Current status of the transcription job.

---

## TranscriptionTranscript

Transcript data including the full text and tokens.

<a id="transcriptiontranscript-properties"></a>

### Properties

| Property | Type | Description |
| ------ | ------ | ------ |
| `id` | `str` | Unique identifier of the transcription this transcript belongs to (UUID). |
| `text` | `str` | Complete transcribed text content. |
| `tokens` | `list[Token]` | List of detailed token information with timestamps and metadata. |

---

## TranslationConfig

Configuration describing how translation should be performed.

<a id="translationconfig-properties"></a>

### Properties

| Property | Type | Description |
| ------ | ------ | ------ |
| `type` | `TranslationType` | Translation type. |
| `target_language` | `str \| None` | Target language code for translation (e.g., "fr", "es", "de") (one_way). |
| `language_a` | `str \| None` | First language code (two_way). |
| `language_b` | `str \| None` | Second language code (two_way). |

---

## TranslationTarget

Describes translation targets offered by a model.

<a id="translationtarget-properties"></a>

### Properties

| Property | Type | Description |
| ------ | ------ | ------ |
| `target_language` | `str` | Target language code for translation (e.g., "fr", "es", "de") (one_way). |
| `source_languages` | `list[str]` | List of source language codes. |
| `exclude_source_languages` | `list[str]` | Source language codes excluded for this target. |

---

<a id="translationtype"></a>

## TranslationType

```python
TranslationType = Literal["one_way", "two_way"]
```

Supported translation configuration types.

---

<a id="temporaryapikeyusagetype"></a>

## TemporaryApiKeyUsageType

```python
TemporaryApiKeyUsageType = Literal["transcribe_websocket"]
```

Intended usage for temporary API keys.

---

## UploadFilePayload

Optional metadata supplied at upload time.

<a id="uploadfilepayload-properties"></a>

### Properties

| Property | Type | Description |
| ------ | ------ | ------ |
| `client_reference_id` | `str \| None` | Optional tracking identifier string. Does not need to be unique |

---

## RealtimeEvent

Event payload received from the realtime STT websocket.

<a id="realtimeevent-properties"></a>

### Properties

| Property | Type | Description |
| ------ | ------ | ------ |
| `tokens` | `list[Token]` | Tokens in this result. |
| `final_audio_proc_ms` | `int \| None` | Milliseconds of audio that have been finalized. |
| `total_audio_proc_ms` | `int \| None` | Total milliseconds of audio processed. |
| `finished` | `bool` | Whether this is the final result (session ending). |
| `error_code` | `int \| None` | Error code if the realtime operation failed. |
| `error_message` | `str \| None` | Human-readable description of the error. |

<a id="realtimeevent-validate_event"></a>

### validate_event()

```python
validate_event(raw: str | bytes) -> RealtimeEvent
```

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `raw` | `str \| bytes` | Raw event payload from the realtime API. |

**Returns**

`RealtimeEvent`

---

## RealtimeSTTConfig

Configuration for initiating a realtime transcription session.

<a id="realtimesttconfig-properties"></a>

### Properties

| Property | Type | Description |
| ------ | ------ | ------ |
| `api_key` | `str \| None` | API key for real-time sessions. |
| `model` | `str` | Speech-to-text model to use. |
| `audio_format` | `str` | Audio format. Use 'auto' for automatic detection of container formats. |
| `num_channels` | `int \| None` | Number of audio channels (required for raw audio formats). |
| `sample_rate` | `int \| None` | Sample rate in Hz (required for PCM formats). |
| `language_hints` | `list[str] \| None` | Expected languages in the audio (ISO language codes). |
| `language_hints_strict` | `bool \| None` | When true, recognition is strongly biased toward language hints (best results when using one language in language_hints). |
| `context` | `StructuredContext \| None` | Additional context to improve transcription accuracy. |
| `enable_speaker_diarization` | `bool \| None` | Enable speaker identification. |
| `enable_language_identification` | `bool \| None` | Enable automatic language detection. |
| `enable_endpoint_detection` | `bool \| None` | Enable endpoint detection for utterance boundaries. |
| `translation` | `TranslationConfig \| None` | Translation configuration. |
| `client_reference_id` | `str \| None` | Optional tracking identifier (max 256 chars). |

<a id="realtimesttconfig-build_payload"></a>

### build_payload()

```python
build_payload(api_key: str) -> RealtimeSTTConfig
```

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `api_key` | `str` | API key used for authentication. |

**Returns**

`RealtimeSTTConfig`

---

<a id="headers"></a>

## Headers

```python
Headers = Mapping[str, str]
```

---

## WebhookAuthConfig

Configuration for webhook authentication headers.

<a id="webhookauthconfig-properties"></a>

### Properties

| Property | Type | Description |
| ------ | ------ | ------ |
| `name` | `str` | Expected header name (case-insensitive comparison). |
| `value` | `str` | Expected header value (exact match). |

---

## WebhookEvent

Basic webhook event metadata.

<a id="webhookevent-properties"></a>

### Properties

| Property | Type | Description |
| ------ | ------ | ------ |
| `id` | `str` | Transcription ID (UUID). |
| `status` | `Literal['completed', 'error']` | Transcription result status. |