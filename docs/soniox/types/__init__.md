---
title: soniox.types
description: Description for types
keywords: annotations, ApiError, ApiErrorValidationError, CreateTemporaryApiKeyPayload, CreateTemporaryApiKeyResponse, CreateTranscriptionConfig, CreateTranscriptionPayload, File, GetFilesPayload, GetFilesResponse, GetModelsResponse, GetTranscriptionsPayload, GetTranscriptionsResponse, Model, StructuredContext, StructuredContextGeneralItem, StructuredContextTranslationTerm, TemporaryApiKeyUsageType, Transcription, TranscriptionStatus, TranscriptionTranscript, TranslationConfig, TranslationTarget, TranslationType, UploadFilePayload, Token, RealtimeEvent, RealtimeSTTConfig, Headers, WebhookAuthConfig, WebhookEvent, __all__, common, webhooks, realtime, api
---


---

## Class `ApiError`

Structured representation of a non-2xx API response payload.

### Attributes

- **status_code**: HTTP status code.

- **error_type**: High-level error code (e.g., 'bad_request', 'quota_exceeded') for programmatic handling.

- **message**: Detailed error message describing the failure.

- **validation_errors**: List of specific field validation failures, if applicable.

- **request_id**: Unique identifier for the request, useful for troubleshooting.

---

## Class `ApiErrorValidationError`

Details a single validation error reported by the Soniox API.

### Attributes

- **error_type**: The category of validation error.

- **location**: The location of the error, e.g. ['body', 'audio_url'].

- **message**: A human-readable description of the validation failure.

---

## Class `CreateTemporaryApiKeyPayload`

Payload for requesting a temporary API key (e.g., websocket).

### Attributes

- **usage_type**: Intended usage of the temporary API key.

- **expires_in_seconds**: Duration in seconds until the temporary API key expires

- **client_reference_id**: Optional tracking identifier string. Does not need to be unique

---

## Class `CreateTemporaryApiKeyResponse`

Response data for a temp API key request.

### Attributes

- **api_key**: Created temporary API key.

- **expires_at**: UTC timestamp indicating when generated temporary API key will expire

---

## Class `CreateTranscriptionConfig`

Helper config used when building transcription payloads.

### Attributes

- **model**: Speech-to-text model to use.

- **language_hints**: Array of expected ISO language codes to bias recognition.

- **language_hints_strict**: When true, model relies more heavily on language hints.

- **enable_speaker_diarization**: Enable speaker diarization to identify different speakers.

- **enable_language_identification**: Enable automatic language identification

- **translation**: Translation configuration

- **context**: Additional context to improve transcription accuracy and formatting of specialized terms.

- **webhook_url**: URL to receive webhook notifications when transcription is completed or fails.

- **webhook_auth_header_name**: Name of the authentication header sent with webhook notifications

- **webhook_auth_header_value**: Authentication header value sent with webhook notifications

- **client_reference_id**: Optional tracking identifier

---

## Class `CreateTranscriptionPayload`

Payload sent to create an asynchronous transcription job.

### Attributes

- **model**: Speech-to-text model to use.

- **audio_url**: URL of a publicly accessible audio file.

- **file_id**: ID of a previously uploaded file (UUID).

- **language_hints**: Array of expected ISO language codes to bias recognition.

- **language_hints_strict**: When true, model relies more heavily on language hints (best results with one language hint set).

- **enable_speaker_diarization**: Enable speaker diarization to identify different speakers.

- **enable_language_identification**: Enable automatic language identification.

- **translation**: Translation configuration.

- **context**: Additional context to improve transcription accuracy and formatting of specialized terms.

- **webhook_url**: URL to receive webhook notifications when transcription is completed or fails.

- **webhook_auth_header_name**: Name of the authentication header sent with webhook notifications

- **webhook_auth_header_value**: Authentication header value sent with webhook notifications.

- **client_reference_id**: Optional tracking identifier.

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

## Class `File`

Metadata describing an uploaded file in the Soniox API.

### Attributes

- **id**: Unique identifier of the file (UUID).

- **filename**: Name of the file.

- **size**: Size of the file in bytes.

- **created_at**: UTC timestamp indicating when the file was uploaded.

- **client_reference_id**: Optional tracking identifier string.

---

## Class `GetFilesPayload`

Parameters accepted by the file listing endpoint.

### Attributes

- **limit**: Maximum number of files to return.

- **cursor**: Pagination cursor for the next page of results.

---

## Class `GetFilesResponse`

Paginated response returned when listing uploaded files.

### Attributes

- **files**: List of uploaded files.

- **next_page_cursor**: A pagination token that references the next page of results. When None, no additional results are available.

---

## Class `GetModelsResponse`

Response returned when listing available models.

### Attributes

- **models**: List of all available models.

---

## Class `GetTranscriptionsPayload`

Parameters for listing transcription jobs.

### Attributes

- **limit**: Maximum number of transcriptions to return.

- **cursor**: Pagination cursor for the next page of results.

---

## Class `GetTranscriptionsResponse`

Paginated response for transcription listings.

### Attributes

- **transcriptions**: List of transcriptions.

- **next_page_cursor**: A pagination token that references the next page of results. When None, no additional results are available.

---

## Class `Model`

Describes a Soniox transcription model.

### Attributes

- **id**: Unique identifier of the model.

- **aliased_model_id**: If this is an alias, the id of the aliased model. None for non-alias models.

- **name**: Name of the model.

- **context_version**: Version of context supported.

- **transcription_mode**: Transcription mode of the model.

- **languages**: List of languages supported by the model.

- **supports_language_hints_strict**: If model supports 'language_hints_strict' option.

- **translation_targets**: List of supported one-way translation targets. If list is empty, check for one_way_translation field.

- **two_way_translation_pairs**: List of supported two-way translation pairs. If list is empty, check for one_way_translation field.

- **one_way_translation**: When contains string 'all_languages', any language from languages can be used

- **two_way_translation**: When contains string 'all_languages',' any language pair from languages can be used

---

## Class `StructuredContext`

Optional structured context provided to the transcription engine.

### Attributes

- **general**: Structured key-value pairs describing domain, topic, intent, participant names, etc.

- **text**: Longer free-form background text, prior interaction history, reference documents, or meeting notes.

- **terms**: Domain-specific or uncommon words to recognize.

- **translation_terms**: Custom translations for ambiguous terms.

---

## Class `StructuredContextGeneralItem`

Single general context key/value pair for transcription context.

### Attributes

- **key**: The key describing the context type (e.g., "domain", "topic", "doctor").

- **value**: The value for the context key.

---

## Class `StructuredContextTranslationTerm`

Defines a translation term mapping used in structured context.

### Attributes

- **source**: The source term to translate.

- **target**: The target translation for the term.

---

## Class `Transcription`

Represents a transcription job tracked by Soniox.

### Attributes

- **id**: Unique identifier of the transcription (UUID).

- **status**: Current status of the transcription.

- **created_at**: UTC timestamp when the transcription was created.

- **model**: Speech-to-text model used.

- **audio_url**: URL of the audio file being transcribed.

- **file_id**: ID of the uploaded file being transcribed (UUID).

- **filename**: Name of the file being transcribed.

- **language_hints**: Expected languages in the audio. If not specified, languages are automatically detected.

- **enable_speaker_diarization**: When true, speakers are identified and separated in the transcription output.

- **enable_language_identification**: When true, language is detected for each part of the transcription.

- **audio_duration_ms**: Duration of the audio in milliseconds. Only available after processing begins.

- **error_type**: Error type if transcription failed. None for successful or in-progress transcriptions.

- **error_message**: Error message if transcription failed. None for successful or in-progress transcriptions.

- **webhook_url**: URL to receive webhook notifications when transcription is completed or fails.

- **webhook_auth_header_name**: Name of the authentication header sent with webhook notifications.

- **webhook_auth_header_value**: Authentication header value. Always returned masked.

- **webhook_status_code**: HTTP status code received from your server when webhook was delivered. None if not yet sent.

- **client_reference_id**: Optional tracking identifier.

---

## Class `TranscriptionTranscript`

Transcript data including the full text and tokens.

### Attributes

- **id**: Unique identifier of the transcription this transcript belongs to (UUID).

- **text**: Complete transcribed text content.

- **tokens**: List of detailed token information with timestamps and metadata.

---

## Class `TranslationConfig`

Configuration describing how translation should be performed.

### Attributes

- **type**: Translation type.

- **target_language**: Target language code for translation (e.g., "fr", "es", "de") (one_way).

- **language_a**: First language code (two_way).

- **language_b**: Second language code (two_way).

---

## Class `TranslationTarget`

Describes translation targets offered by a model.

### Attributes

- **target_language**: 

- **source_languages**: 

- **exclude_source_languages**: 

---

## Class `UploadFilePayload`

Optional metadata supplied at upload time.

### Attributes

- **client_reference_id**: Optional tracking identifier string. Does not need to be unique

---

## Class `Token`

Token metadata emitted during realtime streaming transcriptions.

### Attributes

- **model_config**: 

- **text**: The transcribed text.

- **start_ms**: Start time in milliseconds relative to audio start.

- **end_ms**: End time in milliseconds relative to audio start.

- **confidence**: Confidence score (0.0 to 1.0).

- **is_final**: Whether this is a finalized token.

- **speaker**: Speaker identifier (if diarization enabled).

- **translation_status**: Translation status of this token.

- **language**: Detected language code (if language identification enabled).

- **source_language**: Source language for translated tokens.

---

## Class `RealtimeEvent`

Event payload received from the realtime STT websocket.

### Attributes

- **model_config**: 

- **tokens**: Tokens in this result.

- **final_audio_proc_ms**: Milliseconds of audio that have been finalized.

- **total_audio_proc_ms**: Total milliseconds of audio processed.

- **finished**: Whether this is the final result (session ending).

- **error_code**: Error code if the realtime operation failed.

- **error_message**: Human-readable description of the error.

### `validate_event`

#### Signature

```python
validate_event(raw: str | bytes) -> RealtimeEvent
```

#### Parameters

- **cls** (None): 

- **raw** (str | bytes): 

#### Returns

RealtimeEvent

---

## Class `RealtimeSTTConfig`

Configuration for initiating a realtime transcription session.

### Attributes

- **api_key**: API key for real-time sessions.

- **model**: Speech-to-text model to use.

- **audio_format**: Audio format. Use 'auto' for automatic detection of container formats.

- **num_channels**: Number of audio channels (required for raw audio formats).

- **sample_rate**: Sample rate in Hz (required for PCM formats).

- **language_hints**: Expected languages in the audio (ISO language codes).

- **language_hints_strict**: When true, recognition is strongly biased toward language hints (best results when using one language in language_hints).

- **context**: Additional context to improve transcription accuracy.

- **enable_speaker_diarization**: Enable speaker identification.

- **enable_language_identification**: Enable automatic language detection.

- **enable_endpoint_detection**: Enable endpoint detection for utterance boundaries.

- **translation**: Translation configuration.

- **client_reference_id**: Optional tracking identifier (max 256 chars).

### `build_payload`

#### Signature

```python
build_payload(api_key: str) -> RealtimeSTTConfig
```

#### Parameters

- **self** (None): 

- **api_key** (str): 

#### Returns

RealtimeSTTConfig

---

## Class `WebhookAuthConfig`

Configuration for webhook authentication headers.

### Attributes

- **name**: Expected header name (case-insensitive comparison).

- **value**: Expected header value (exact match).

---

## Class `WebhookEvent`

Basic webhook event metadata.

### Attributes

- **id**: Transcription ID (UUID).

- **status**: Transcription result status.