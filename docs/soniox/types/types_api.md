---
title: "soniox.types.api"
description: "Details a single validation error reported by the Soniox API."
keywords: "ApiError, ApiErrorValidationError, CreateTemporaryApiKeyPayload, CreateTemporaryApiKeyResponse, CreateTranscriptionConfig, CreateTranscriptionPayload, File, GetFilesPayload, GetFilesResponse, GetModelsResponse, GetTranscriptionsPayload, GetTranscriptionsResponse, Language, Model, StructuredContext, StructuredContextGeneralItem, StructuredContextTranslationTerm, Transcription, TranscriptionTranscript, TranslationConfig, TranslationTarget, UploadFilePayload"
---

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

## GetFilesPayload

Parameters accepted by the file listing endpoint.

<a id="getfilespayload-properties"></a>

### Properties

| Property | Type |
| ------ | ------ |
| `limit` | `int` |
| `cursor` | `str \| None` |

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

## GetFilesResponse

Paginated response returned when listing uploaded files.

<a id="getfilesresponse-properties"></a>

### Properties

| Property | Type |
| ------ | ------ |
| `files` | `list[File]` |
| `next_page_cursor` | `str \| None` |

---

## UploadFilePayload

Optional metadata supplied at upload time.

<a id="uploadfilepayload-properties"></a>

### Properties

| Property | Type |
| ------ | ------ |
| `client_reference_id` | `str \| None` |

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

## Language

Represents a supported language for transcription or translation.

<a id="language-properties"></a>

### Properties

| Property | Type |
| ------ | ------ |
| `code` | `str` |
| `name` | `str` |

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

## GetModelsResponse

Response returned when listing available models.

<a id="getmodelsresponse-properties"></a>

### Properties

| Property | Type |
| ------ | ------ |
| `models` | `list[Model]` |

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

## GetTranscriptionsResponse

Paginated response for transcription listings.

<a id="gettranscriptionsresponse-properties"></a>

### Properties

| Property | Type |
| ------ | ------ |
| `transcriptions` | `list[Transcription]` |
| `next_page_cursor` | `str \| None` |