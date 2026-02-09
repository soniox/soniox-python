---
title: soniox.types.api
description: Description for api
keywords: annotations, datetime, Literal, BaseModel, Field, model_validator, Self, Token, TranscriptionStatus, TranscriptionMode, TranslationType, TemporaryApiKeyUsageType, ApiErrorValidationError, ApiError, GetFilesPayload, File, GetFilesResponse, UploadFilePayload, GetTranscriptionsPayload, StructuredContextGeneralItem, StructuredContextTranslationTerm, StructuredContext, TranslationConfig, CreateTranscriptionPayload, CreateTranscriptionConfig, CreateTemporaryApiKeyPayload, CreateTemporaryApiKeyResponse, Language, TranslationTarget, Model, GetModelsResponse, TranscriptionTranscript, Transcription, GetTranscriptionsResponse
---


---

## Class `ApiErrorValidationError`

Details a single validation error reported by the Soniox API.

### Attributes

- **error_type**: 

- **location**: 

- **message**: 

---

## Class `ApiError`

Structured representation of a non-2xx API response payload.

### Attributes

- **status_code**: 

- **error_type**: 

- **message**: 

- **validation_errors**: 

- **request_id**: 

---

## Class `GetFilesPayload`

Parameters accepted by the file listing endpoint.

### Attributes

- **limit**: 

- **cursor**: 

---

## Class `File`

Metadata describing an uploaded file in the Soniox API.

### Attributes

- **id**: 

- **filename**: 

- **size**: 

- **created_at**: 

- **client_reference_id**: 

---

## Class `GetFilesResponse`

Paginated response returned when listing uploaded files.

### Attributes

- **files**: 

- **next_page_cursor**: 

---

## Class `UploadFilePayload`

Optional metadata supplied at upload time.

### Attributes

- **client_reference_id**: 

---

## Class `GetTranscriptionsPayload`

Parameters for listing transcription jobs.

### Attributes

- **limit**: 

- **cursor**: 

---

## Class `StructuredContextGeneralItem`

Single general context key/value pair for transcription context.

### Attributes

- **key**: 

- **value**: 

---

## Class `StructuredContextTranslationTerm`

Defines a translation term mapping used in structured context.

### Attributes

- **source**: 

- **target**: 

---

## Class `StructuredContext`

Optional structured context provided to the transcription engine.

### Attributes

- **general**: 

- **text**: 

- **terms**: 

- **translation_terms**: 

---

## Class `TranslationConfig`

Configuration describing how translation should be performed.

### Attributes

- **type**: 

- **target_language**: 

- **language_a**: 

- **language_b**: 

---

## Class `CreateTranscriptionPayload`

Payload sent to create an asynchronous transcription job.

### Attributes

- **model**: 

- **audio_url**: 

- **file_id**: 

- **language_hints**: 

- **language_hints_strict**: 

- **enable_speaker_diarization**: 

- **enable_language_identification**: 

- **translation**: 

- **context**: 

- **webhook_url**: 

- **webhook_auth_header_name**: 

- **webhook_auth_header_value**: 

- **client_reference_id**: 

### `_validate_audio_source`

#### Signature

```python
_validate_audio_source() -> Self
```

#### Parameters

- **self** (None): 

#### Returns

Self

---

## Class `CreateTranscriptionConfig`

Helper config used when building transcription payloads.

### Attributes

- **model**: 

- **language_hints**: 

- **language_hints_strict**: 

- **enable_speaker_diarization**: 

- **enable_language_identification**: 

- **translation**: 

- **context**: 

- **webhook_url**: 

- **webhook_auth_header_name**: 

- **webhook_auth_header_value**: 

- **client_reference_id**: 

---

## Class `CreateTemporaryApiKeyPayload`

Payload for requesting a temporary API key (e.g., websocket).

### Attributes

- **usage_type**: 

- **expires_in_seconds**: 

- **client_reference_id**: 

---

## Class `CreateTemporaryApiKeyResponse`

Response data for a temp API key request.

### Attributes

- **api_key**: 

- **expires_at**: 

---

## Class `Language`

Represents a supported language for transcription or translation.

### Attributes

- **code**: 

- **name**: 

---

## Class `TranslationTarget`

Describes translation targets offered by a model.

### Attributes

- **target_language**: 

- **source_languages**: 

- **exclude_source_languages**: 

---

## Class `Model`

Describes a Soniox transcription model.

### Attributes

- **id**: 

- **aliased_model_id**: 

- **name**: 

- **context_version**: 

- **transcription_mode**: 

- **languages**: 

- **supports_language_hints_strict**: 

- **translation_targets**: 

- **two_way_translation_pairs**: 

- **one_way_translation**: 

- **two_way_translation**: 

---

## Class `GetModelsResponse`

Response returned when listing available models.

### Attributes

- **models**: 

---

## Class `TranscriptionTranscript`

Transcript data including the full text and tokens.

### Attributes

- **id**: 

- **text**: 

- **tokens**: 

---

## Class `Transcription`

Represents a transcription job tracked by Soniox.

### Attributes

- **id**: 

- **status**: 

- **created_at**: 

- **model**: 

- **audio_url**: 

- **file_id**: 

- **filename**: 

- **language_hints**: 

- **enable_speaker_diarization**: 

- **enable_language_identification**: 

- **audio_duration_ms**: 

- **error_type**: 

- **error_message**: 

- **webhook_url**: 

- **webhook_auth_header_name**: 

- **webhook_auth_header_value**: 

- **webhook_status_code**: 

- **client_reference_id**: 

---

## Class `GetTranscriptionsResponse`

Paginated response for transcription listings.

### Attributes

- **transcriptions**: 

- **next_page_cursor**: 