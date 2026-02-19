---
title: "soniox.types"
description: "Structured representation of a non-2xx API response payload."
keywords: "ApiError, ApiErrorValidationError, CreateTemporaryApiKeyPayload, CreateTemporaryApiKeyResponse, CreateTranscriptionConfig, CreateTranscriptionPayload, File, GetFilesPayload, GetFilesResponse, GetModelsResponse, GetTranscriptionsPayload, GetTranscriptionsResponse, Model, RealtimeEvent, RealtimeSTTConfig, StructuredContext, StructuredContextGeneralItem, StructuredContextTranslationTerm, Token, Transcription, TranscriptionTranscript, TranslationConfig, TranslationTarget, UploadFilePayload, WebhookAuthConfig, WebhookEvent"
---

---

## ApiError

Structured representation of a non-2xx API response payload.

<a id="apierror-properties"></a>

### Properties

| Property | Type |
| ------ | ------ |
| `status_code` | `int` |
| `error_type` | `str` |
| `message` | `str` |
| `validation_errors` | `list[ApiErrorValidationError]` |
| `request_id` | `str \| None` |

---

## ApiErrorValidationError

Details a single validation error reported by the Soniox API.

<a id="apierrorvalidationerror-properties"></a>

### Properties

| Property | Type |
| ------ | ------ |
| `error_type` | `str` |
| `location` | `str` |
| `message` | `str` |

---

## CreateTemporaryApiKeyPayload

Payload for requesting a temporary API key (e.g., websocket).

<a id="createtemporaryapikeypayload-properties"></a>

### Properties

| Property | Type |
| ------ | ------ |
| `usage_type` | `TemporaryApiKeyUsageType` |
| `expires_in_seconds` | `int` |
| `client_reference_id` | `str \| None` |

---

## CreateTemporaryApiKeyResponse

Response data for a temp API key request.

<a id="createtemporaryapikeyresponse-properties"></a>

### Properties

| Property | Type |
| ------ | ------ |
| `api_key` | `str` |
| `expires_at` | `datetime` |

---

## CreateTranscriptionConfig

Helper config used when building transcription payloads.

<a id="createtranscriptionconfig-properties"></a>

### Properties

| Property | Type |
| ------ | ------ |
| `model` | `str \| None` |
| `language_hints` | `list[str] \| None` |
| `language_hints_strict` | `bool \| None` |
| `enable_speaker_diarization` | `bool \| None` |
| `enable_language_identification` | `bool \| None` |
| `translation` | `TranslationConfig \| None` |
| `context` | `StructuredContext \| None` |
| `webhook_url` | `str \| None` |
| `webhook_auth_header_name` | `str \| None` |
| `webhook_auth_header_value` | `str \| None` |
| `client_reference_id` | `str \| None` |

---

## CreateTranscriptionPayload

Payload sent to create an asynchronous transcription job.

<a id="createtranscriptionpayload-properties"></a>

### Properties

| Property | Type |
| ------ | ------ |
| `model` | `str` |
| `audio_url` | `str \| None` |
| `file_id` | `str \| None` |
| `language_hints` | `list[str] \| None` |
| `language_hints_strict` | `bool \| None` |
| `enable_speaker_diarization` | `bool \| None` |
| `enable_language_identification` | `bool \| None` |
| `translation` | `TranslationConfig \| None` |
| `context` | `StructuredContext \| None` |
| `webhook_url` | `str \| None` |
| `webhook_auth_header_name` | `str \| None` |
| `webhook_auth_header_value` | `str \| None` |
| `client_reference_id` | `str \| None` |

---

## File

Metadata describing an uploaded file in the Soniox API.

<a id="file-properties"></a>

### Properties

| Property | Type |
| ------ | ------ |
| `id` | `str` |
| `filename` | `str` |
| `size` | `int` |
| `created_at` | `datetime` |
| `client_reference_id` | `str \| None` |

---

## GetFilesPayload

Parameters accepted by the file listing endpoint.

<a id="getfilespayload-properties"></a>

### Properties

| Property | Type |
| ------ | ------ |
| `limit` | `int` |
| `cursor` | `str \| None` |

---

## GetFilesResponse

Paginated response returned when listing uploaded files.

<a id="getfilesresponse-properties"></a>

### Properties

| Property | Type |
| ------ | ------ |
| `files` | `list[File]` |
| `next_page_cursor` | `str \| None` |

---

## GetModelsResponse

Response returned when listing available models.

<a id="getmodelsresponse-properties"></a>

### Properties

| Property | Type |
| ------ | ------ |
| `models` | `list[Model]` |

---

## GetTranscriptionsPayload

Parameters for listing transcription jobs.

<a id="gettranscriptionspayload-properties"></a>

### Properties

| Property | Type |
| ------ | ------ |
| `limit` | `int` |
| `cursor` | `str \| None` |

---

## GetTranscriptionsResponse

Paginated response for transcription listings.

<a id="gettranscriptionsresponse-properties"></a>

### Properties

| Property | Type |
| ------ | ------ |
| `transcriptions` | `list[Transcription]` |
| `next_page_cursor` | `str \| None` |

---

## Model

Describes a Soniox transcription model.

<a id="model-properties"></a>

### Properties

| Property | Type |
| ------ | ------ |
| `id` | `str` |
| `aliased_model_id` | `str \| None` |
| `name` | `str` |
| `context_version` | `int \| None` |
| `transcription_mode` | `TranscriptionMode` |
| `languages` | `list[Language]` |
| `supports_language_hints_strict` | `bool` |
| `translation_targets` | `list[TranslationTarget]` |
| `two_way_translation_pairs` | `list[str]` |
| `one_way_translation` | `str \| None` |
| `two_way_translation` | `str \| None` |

---

## StructuredContext

Optional structured context provided to the transcription engine.

<a id="structuredcontext-properties"></a>

### Properties

| Property | Type |
| ------ | ------ |
| `general` | `list[StructuredContextGeneralItem] \| None` |
| `text` | `str \| None` |
| `terms` | `list[str] \| None` |
| `translation_terms` | `list[StructuredContextTranslationTerm] \| None` |

---

## StructuredContextGeneralItem

Single general context key/value pair for transcription context.

<a id="structuredcontextgeneralitem-properties"></a>

### Properties

| Property | Type |
| ------ | ------ |
| `key` | `str` |
| `value` | `str` |

---

## StructuredContextTranslationTerm

Defines a translation term mapping used in structured context.

<a id="structuredcontexttranslationterm-properties"></a>

### Properties

| Property | Type |
| ------ | ------ |
| `source` | `str` |
| `target` | `str` |

---

## Transcription

Represents a transcription job tracked by Soniox.

<a id="transcription-properties"></a>

### Properties

| Property | Type |
| ------ | ------ |
| `id` | `str` |
| `status` | `TranscriptionStatus` |
| `created_at` | `datetime` |
| `model` | `str` |
| `audio_url` | `str \| None` |
| `file_id` | `str \| None` |
| `filename` | `str` |
| `language_hints` | `list[str] \| None` |
| `enable_speaker_diarization` | `bool` |
| `enable_language_identification` | `bool` |
| `audio_duration_ms` | `int \| None` |
| `error_type` | `str \| None` |
| `error_message` | `str \| None` |
| `webhook_url` | `str \| None` |
| `webhook_auth_header_name` | `str \| None` |
| `webhook_auth_header_value` | `str \| None` |
| `webhook_status_code` | `int \| None` |
| `client_reference_id` | `str \| None` |

---

## TranscriptionTranscript

Transcript data including the full text and tokens.

<a id="transcriptiontranscript-properties"></a>

### Properties

| Property | Type |
| ------ | ------ |
| `id` | `str` |
| `text` | `str` |
| `tokens` | `list[Token]` |

---

## TranslationConfig

Configuration describing how translation should be performed.

<a id="translationconfig-properties"></a>

### Properties

| Property | Type |
| ------ | ------ |
| `type` | `TranslationType` |
| `target_language` | `str \| None` |
| `language_a` | `str \| None` |
| `language_b` | `str \| None` |

---

## TranslationTarget

Describes translation targets offered by a model.

<a id="translationtarget-properties"></a>

### Properties

| Property | Type |
| ------ | ------ |
| `target_language` | `str` |
| `source_languages` | `list[str]` |
| `exclude_source_languages` | `list[str]` |

---

## UploadFilePayload

Optional metadata supplied at upload time.

<a id="uploadfilepayload-properties"></a>

### Properties

| Property | Type |
| ------ | ------ |
| `client_reference_id` | `str \| None` |

---

## Token

Token metadata emitted during realtime streaming transcriptions.

<a id="token-properties"></a>

### Properties

| Property | Type |
| ------ | ------ |
| `model_config` | `-` |
| `text` | `str` |
| `start_ms` | `int \| None` |
| `end_ms` | `int \| None` |
| `confidence` | `float \| None` |
| `is_final` | `bool \| None` |
| `speaker` | `str \| None` |
| `translation_status` | `str \| None` |
| `language` | `str \| None` |
| `source_language` | `str \| None` |

---

## RealtimeEvent

Event payload received from the realtime STT websocket.

<a id="realtimeevent-properties"></a>

### Properties

| Property | Type |
| ------ | ------ |
| `model_config` | `-` |
| `tokens` | `list[Token]` |
| `final_audio_proc_ms` | `int \| None` |
| `total_audio_proc_ms` | `int \| None` |
| `finished` | `bool` |
| `error_code` | `int \| None` |
| `error_message` | `str \| None` |

<a id="realtimeevent-validate_event"></a>

### validate_event()

```python
validate_event(raw: str | bytes) -> RealtimeEvent
```

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `raw` | `str \| bytes` |

**Returns**

`RealtimeEvent`

---

## RealtimeSTTConfig

Configuration for initiating a realtime transcription session.

<a id="realtimesttconfig-properties"></a>

### Properties

| Property | Type |
| ------ | ------ |
| `api_key` | `str \| None` |
| `model` | `str` |
| `audio_format` | `str` |
| `num_channels` | `int \| None` |
| `sample_rate` | `int \| None` |
| `language_hints` | `list[str] \| None` |
| `language_hints_strict` | `bool \| None` |
| `context` | `StructuredContext \| None` |
| `enable_speaker_diarization` | `bool \| None` |
| `enable_language_identification` | `bool \| None` |
| `enable_endpoint_detection` | `bool \| None` |
| `translation` | `TranslationConfig \| None` |
| `client_reference_id` | `str \| None` |

<a id="realtimesttconfig-build_payload"></a>

### build_payload()

```python
build_payload(api_key: str) -> RealtimeSTTConfig
```

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `api_key` | `str` |

**Returns**

`RealtimeSTTConfig`

---

## WebhookAuthConfig

Configuration for webhook authentication headers.

<a id="webhookauthconfig-properties"></a>

### Properties

| Property | Type |
| ------ | ------ |
| `name` | `str` |
| `value` | `str` |

---

## WebhookEvent

Basic webhook event metadata.

<a id="webhookevent-properties"></a>

### Properties

| Property | Type |
| ------ | ------ |
| `id` | `str` |
| `status` | `Literal['completed', 'error']` |