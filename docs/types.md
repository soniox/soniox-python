---
title: "Types"
description: "Soniox Python SDK - Types Reference"
keywords: "Token, ApiError, ApiErrorValidationError, CreateTemporaryApiKeyPayload, CreateTemporaryApiKeyResponse, CreateTtsPayload, ConcurrencyCurrentValues, ConcurrencyLimitValues, ConcurrencyScopeValues, CreateTtsConfig, CreateTranscriptionPayload, CreateTranscriptionConfig, File, GetConcurrencyLimitsResponse, GetFilesCountResponse, GetFilesPayload, GetFilesResponse, GetModelsResponse, GetTTSModelsResponse, GetTtsModelsResponse, GetTranscriptionsCountResponse, GetTranscriptionsPayload, GetTranscriptionsResponse, GetUsageLogsPayload, GetUsageLogsResponse, Language, LanguageCode, SupportedLanguage, Model, RealtimeSTTAudioFormat, RealtimeSTTHeaderFormat, RealtimeSTTRawFormat, StructuredContext, StructuredContextGeneralInput, StructuredContextGeneralItem, StructuredContextInput, StructuredContextTranslationTerm, StructuredContextTranslationTermsInput, Transcription, TranscriptionStatus, TranscriptionTranscript, TranslationConfig, TranslationConfigInput, TranslationTarget, TranslationType, TTSModel, TTSVoice, TtsAudioFormat, TtsBitrate, TtsModel, TtsSampleRate, TtsVoice, TtsVoiceGender, TemporaryApiKeyUsageType, UploadFilePayload, UsageLogEntry, UsageLogsSort, RealtimeEvent, RealtimeSTTConfig, RealtimeTTSConfig, RealtimeTTSEvent, RealtimeTTSTextMessage, Headers, WebhookAuthConfig, WebhookEvent"
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
| `more_info` | `str \| None` | Optional URL pointing to documentation for resolving this error. |

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
| `single_use` | `bool \| None` | When true, restricts the temporary API key to a single use. |
| `max_session_duration_seconds` | `int \| None` | Maximum connection duration in seconds for WebSocket and TTS HTTP streaming endpoints. |

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

## CreateTtsPayload

Payload sent to generate speech audio from text via REST.

<a id="createttspayload-properties"></a>

### Properties

| Property | Type | Description |
| ------ | ------ | ------ |
| `model` | `str` | Text-to-Speech model to use. |
| `language` | `str` | Language code for Text-to-Speech (e.g., "en"). |
| `voice` | `str` | Voice identifier to generate speech audio with. |
| `audio_format` | `TtsAudioFormat` | Requested output audio format. |
| `sample_rate` | `TtsSampleRate \| None` | Output sample rate in Hz. |
| `bitrate` | `TtsBitrate \| None` | Output bitrate in bits-per-second for compressed formats. |
| `text` | `str` | Input text to generate into speech. |

---

## ConcurrencyCurrentValues

Live counts of concurrent sessions.

<a id="concurrencycurrentvalues-properties"></a>

### Properties

| Property | Type | Description |
| ------ | ------ | ------ |
| `transcribe_concurrent` | `int` | Number of concurrent realtime STT sessions currently active. |
| `tts_concurrent` | `int` | Number of concurrent realtime TTS sessions currently active. |

---

## ConcurrencyLimitValues

Configured concurrency limits. None means no limit.

<a id="concurrencylimitvalues-properties"></a>

### Properties

| Property | Type | Description |
| ------ | ------ | ------ |
| `transcribe_concurrent` | `int \| None` | Maximum concurrent realtime STT sessions, or None if unlimited. |
| `tts_concurrent` | `int \| None` | Maximum concurrent realtime TTS sessions, or None if unlimited. |

---

## ConcurrencyScopeValues

Current and limit values for a single scope (project or organization).

<a id="concurrencyscopevalues-properties"></a>

### Properties

| Property | Type | Description |
| ------ | ------ | ------ |
| `current` | `ConcurrencyCurrentValues` | Live counts of active sessions. |
| `limits` | `ConcurrencyLimitValues` | Configured limits. |

---

## CreateTtsConfig

Helper config used when building Text-to-Speech payloads.

<a id="createttsconfig-properties"></a>

### Properties

| Property | Type | Description |
| ------ | ------ | ------ |
| `model` | `str \| None` | Deprecated: pass ``model`` to generate()/generate_to_file() instead. |
| `language` | `str \| None` | Deprecated: pass ``language`` to generate()/generate_to_file() instead. |
| `voice` | `str \| None` | Deprecated: pass ``voice`` to generate()/generate_to_file() instead. |
| `audio_format` | `TtsAudioFormat \| None` | Requested output audio format. |
| `sample_rate` | `TtsSampleRate \| None` | Output sample rate in Hz. |
| `bitrate` | `TtsBitrate \| None` | Output bitrate in bits-per-second for compressed formats. |

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
| `language_hints` | `list[LanguageCode] \| None` | Array of expected ISO language codes to bias recognition. |
| `language_hints_strict` | `bool \| None` | When true, model relies more heavily on language hints (best results with one language hint set). |
| `enable_speaker_diarization` | `bool \| None` | Enable speaker diarization to identify different speakers. |
| `enable_language_identification` | `bool \| None` | Enable automatic language identification. |
| `translation` | `TranslationConfigInput \| None` | Translation configuration. |
| `context` | `StructuredContextInput \| None` | Additional context to improve transcription accuracy and formatting of specialized terms. |
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
| `model` | `str \| None` | Deprecated: pass ``model`` to the create call instead. |
| `language_hints` | `list[LanguageCode] \| None` | Array of expected ISO language codes to bias recognition. |
| `language_hints_strict` | `bool \| None` | When true, model relies more heavily on language hints. |
| `enable_speaker_diarization` | `bool \| None` | Enable speaker diarization to identify different speakers. |
| `enable_language_identification` | `bool \| None` | Enable automatic language identification |
| `translation` | `TranslationConfigInput \| None` | Translation configuration |
| `context` | `StructuredContextInput \| None` | Additional context to improve transcription accuracy and formatting of specialized terms. |
| `webhook_url` | `str \| None` | URL to receive webhook notifications when transcription is completed or fails. |
| `webhook_auth_header_name` | `str \| None` | Name of the authentication header sent with webhook notifications |
| `webhook_auth_header_value` | `str \| None` | Authentication header value sent with webhook notifications |
| `client_reference_id` | `str \| None` | Deprecated: pass ``client_reference_id`` to the create call instead. |

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

## GetConcurrencyLimitsResponse

Response returned when fetching concurrency limits.

<a id="getconcurrencylimitsresponse-properties"></a>

### Properties

| Property | Type | Description |
| ------ | ------ | ------ |
| `project` | `ConcurrencyScopeValues` | Project-scoped current counts and configured limits. |
| `organization` | `ConcurrencyScopeValues` | Organization-scoped current counts and configured limits. |

---

## GetFilesCountResponse

Breakdown of uploaded file counts by source.

<a id="getfilescountresponse-properties"></a>

### Properties

| Property | Type | Description |
| ------ | ------ | ------ |
| `total` | `int` | Total number of files across all sources. |
| `public_api` | `int` | Number of files uploaded via Public API. |
| `playground` | `int` | Number of files uploaded via the Playground. |

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

<a id="getttsmodelsresponse"></a>

## GetTTSModelsResponse

```python
GetTTSModelsResponse = GetTtsModelsResponse
```

---

## GetTtsModelsResponse

Response returned when listing available Text-to-Speech models.

<a id="getttsmodelsresponse-properties"></a>

### Properties

| Property | Type | Description |
| ------ | ------ | ------ |
| `models` | `list[TtsModel]` | List of available Text-to-Speech models. |

---

## GetTranscriptionsCountResponse

Breakdown of transcription counts by scope.

<a id="gettranscriptionscountresponse-properties"></a>

### Properties

| Property | Type | Description |
| ------ | ------ | ------ |
| `total` | `int` | Total number of transcriptions across all scopes. |
| `public_api` | `int` | Number of transcriptions created via Public API. |
| `playground` | `int` | Number of transcriptions created via the Playground. |

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

## GetUsageLogsPayload

Parameters accepted by the usage logs listing endpoint.

<a id="getusagelogspayload-properties"></a>

### Properties

| Property | Type | Description |
| ------ | ------ | ------ |
| `start_time` | `str` | Start of the time window (inclusive). Filters by request end time. |
| `end_time` | `str` | End of the time window (exclusive). Filters by request end time. |
| `limit` | `int` | Maximum number of usage log entries to return. |
| `sort` | `UsageLogsSort` | Sort order by end_time. Use `end_time_desc` to get the most recent entries first. |
| `cursor` | `str \| None` | Pagination cursor for the next page of results. |

---

## GetUsageLogsResponse

Paginated response for usage-log listings.

<a id="getusagelogsresponse-properties"></a>

### Properties

| Property | Type | Description |
| ------ | ------ | ------ |
| `usage_logs` | `list[UsageLogEntry]` | Per-request usage log entries ordered by end_time. |
| `next_page_cursor` | `str \| None` | Pagination cursor for the next page of results. None if no more pages. |

---

## Language

Deprecated alias for :class:`SupportedLanguage`.

---

<a id="languagecode"></a>

## LanguageCode

```python
LanguageCode = Annotated[str, Field(min_length=2, max_length=2)]
```

ISO 639-1 two-letter language code (e.g. ``"en"``, ``"fr"``).

---

## SupportedLanguage

Represents a supported language for transcription or translation.

<a id="supportedlanguage-properties"></a>

### Properties

| Property | Type | Description |
| ------ | ------ | ------ |
| `code` | `str` | 2-letter language code (ISO format). |
| `name` | `str` | Language name. |

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
| `languages` | `list[SupportedLanguage]` | List of languages supported by the model. |
| `supports_language_hints_strict` | `bool` | If model supports 'language_hints_strict' option. |
| `supports_max_endpoint_delay` | `bool` | If model supports 'max_endpoint_delay_ms' option. |
| `translation_targets` | `list[TranslationTarget]` | List of supported one-way translation targets. If list is empty, check for one_way_translation field. |
| `two_way_translation_pairs` | `list[str]` | List of supported two-way translation pairs. If list is empty, check for one_way_translation field. |
| `one_way_translation` | `str \| None` | When contains string 'all_languages', any language from languages can be used |
| `two_way_translation` | `str \| None` | When contains string 'all_languages',' any language pair from languages can be used |

---

<a id="realtimesttaudioformat"></a>

## RealtimeSTTAudioFormat

```python
RealtimeSTTAudioFormat = Literal["auto"] | RealtimeSTTHeaderFormat | RealtimeSTTRawFormat
```

Audio formats accepted by the realtime STT websocket.

---

<a id="realtimesttheaderformat"></a>

## RealtimeSTTHeaderFormat

```python
RealtimeSTTHeaderFormat = Literal[
    "aac", "aiff", "amr", "asf", "flac", "mp3", "ogg", "wav", "webm",
]
```

Container formats whose header carries sample rate and channels.

---

<a id="realtimesttrawformat"></a>

## RealtimeSTTRawFormat

```python
RealtimeSTTRawFormat = Literal[
    "pcm_s8",
    "pcm_s16le", "pcm_s16be",
    "pcm_s24le", "pcm_s24be",
    "pcm_s32le", "pcm_s32be",
    "pcm_u8",
    "pcm_u16le", "pcm_u16be",
    "pcm_u24le", "pcm_u24be",
    "pcm_u32le", "pcm_u32be",
    "pcm_f32le", "pcm_f32be",
    "pcm_f64le", "pcm_f64be",
    "mulaw", "alaw",
]
```

Raw formats with no header - require ``sample_rate`` and ``num_channels``.

---

## StructuredContext

Optional structured context provided to the transcription engine.

For ergonomics, ``general`` and ``translation_terms`` also accept a plain
dict in addition to the typed item lists:

- ``general={"domain": "Healthcare"}`` (dict of key -> value)
- ``translation_terms={"Mr. Smith": "Sr. Smith"}`` (dict of source -> target)

<a id="structuredcontext-properties"></a>

### Properties

| Property | Type | Description |
| ------ | ------ | ------ |
| `general` | `Annotated[StructuredContextGeneralInput, Field(union_mode='left_to_right')] \| None` | Structured key-value pairs describing domain, topic, intent, participant names, etc. |
| `text` | `str \| None` | Longer free-form background text, prior interaction history, reference documents, or meeting notes. |
| `terms` | `list[str] \| None` | Domain-specific or uncommon words to recognize. |
| `translation_terms` | `Annotated[StructuredContextTranslationTermsInput, Field(union_mode='left_to_right')] \| None` | Custom translations for ambiguous terms. |

---

<a id="structuredcontextgeneralinput"></a>

## StructuredContextGeneralInput

```python
StructuredContextGeneralInput = list[StructuredContextGeneralItem] | dict[str, str]
```

Accepted input shapes for ``StructuredContext.general``.

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

<a id="structuredcontextinput"></a>

## StructuredContextInput

```python
StructuredContextInput = StructuredContext | dict[str, Any]
```

Accepted input for the ``context`` field - typed object or a plain dict.

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

<a id="structuredcontexttranslationtermsinput"></a>

## StructuredContextTranslationTermsInput

```python
StructuredContextTranslationTermsInput = list[StructuredContextTranslationTerm] | dict[str, str]
```

Accepted input shapes for ``StructuredContext.translation_terms``.

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
| `target_language` | `LanguageCode \| None` | Target language code for translation (e.g., "fr", "es", "de") (one_way). |
| `language_a` | `LanguageCode \| None` | First language code (two_way). |
| `language_b` | `LanguageCode \| None` | Second language code (two_way). |

<a id="translationconfig-validate_logic"></a>

### validate_logic()

```python
validate_logic() -> TranslationConfig
```

**Returns**

`TranslationConfig`

---

<a id="translationconfiginput"></a>

## TranslationConfigInput

```python
TranslationConfigInput = TranslationConfig | dict[str, Any]
```

Accepted input for the ``translation`` field - typed object or a plain dict.

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

<a id="ttsmodel"></a>

## TTSModel

```python
TTSModel = TtsModel
```

---

<a id="ttsvoice"></a>

## TTSVoice

```python
TTSVoice = TtsVoice
```

---

<a id="ttsaudioformat"></a>

## TtsAudioFormat

```python
TtsAudioFormat = Literal[
    "pcm_f32le",
    "pcm_s16le",
    "pcm_mulaw",
    "pcm_alaw",
    "wav",
    "aac",
    "mp3",
    "opus",
    "flac",
]
```

Allowed audio formats for Text-to-Speech output.

---

<a id="ttsbitrate"></a>

## TtsBitrate

```python
TtsBitrate = Literal[32000, 64000, 96000, 128000, 192000, 256000, 320000]
```

Allowed output bitrates in bits-per-second for compressed Text-to-Speech formats.

---

## TtsModel

Represents a Text-to-Speech model.

<a id="ttsmodel-properties"></a>

### Properties

| Property | Type | Description |
| ------ | ------ | ------ |
| `id` | `str` | Unique identifier of the model. |
| `aliased_model_id` | `str \| None` | If this is an alias, the id of the aliased model. None for non-alias models. |
| `name` | `str` | Name of the model. |
| `voices` | `list[TtsVoice]` | Voices supported by this model. |
| `languages` | `list[SupportedLanguage]` | Languages supported by this model. |

---

<a id="ttssamplerate"></a>

## TtsSampleRate

```python
TtsSampleRate = Literal[8000, 16000, 24000, 44100, 48000]
```

Allowed output sample rates in Hz for Text-to-Speech.

---

## TtsVoice

Represents a Text-to-Speech voice.

<a id="ttsvoice-properties"></a>

### Properties

| Property | Type | Description |
| ------ | ------ | ------ |
| `id` | `str` | Unique identifier of the voice. |
| `description` | `str` | Description of the voice. |
| `gender` | `TtsVoiceGender` | Gender of the voice. |

---

<a id="ttsvoicegender"></a>

## TtsVoiceGender

```python
TtsVoiceGender = Literal["male", "female", "neutral"]
```

Reported gender of a Text-to-Speech voice.

---

<a id="temporaryapikeyusagetype"></a>

## TemporaryApiKeyUsageType

```python
TemporaryApiKeyUsageType = Literal["transcribe_websocket", "tts_rt"]
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

## UsageLogEntry

A single usage-log entry describing one API request.

<a id="usagelogentry-properties"></a>

### Properties

| Property | Type | Description |
| ------ | ------ | ------ |
| `uuid` | `str` | Unique identifier of the request. |
| `request_scope` | `str` | Scope of the request (api / playground). |
| `client_reference_id` | `str` | Client reference ID supplied on the original request. Empty string if none. |
| `model` | `str` | Model identifier. |
| `start_time` | `datetime` | When the request started. |
| `end_time` | `datetime` | When the request ended. |
| `input_text_tokens` | `int` | - |
| `input_audio_tokens` | `int` | - |
| `input_audio_duration_ms` | `int` | - |
| `output_text_tokens` | `int` | - |
| `output_audio_tokens` | `int` | - |
| `output_audio_duration_ms` | `int` | - |
| `cost_usd` | `str` | - |
| `input_cost_usd` | `str` | - |
| `input_text_cost_usd` | `str` | - |
| `input_audio_cost_usd` | `str` | - |
| `output_cost_usd` | `str` | - |
| `output_text_cost_usd` | `str` | - |
| `output_audio_cost_usd` | `str` | - |

---

<a id="usagelogssort"></a>

## UsageLogsSort

```python
UsageLogsSort = Literal["end_time_asc", "end_time_desc"]
```

Sort order for usage-log entries by end_time.

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
| `audio_format` | `RealtimeSTTAudioFormat` | Audio format. Use 'auto' for automatic detection of container formats. |
| `num_channels` | `int \| None` | Number of audio channels (required for raw audio formats). |
| `sample_rate` | `int \| None` | Sample rate in Hz (required for PCM formats). |
| `language_hints` | `list[LanguageCode] \| None` | Expected languages in the audio (ISO language codes). |
| `language_hints_strict` | `bool \| None` | When true, recognition is strongly biased toward language hints (best results when using one language in language_hints). |
| `context` | `StructuredContextInput \| None` | Additional context to improve transcription accuracy. |
| `enable_speaker_diarization` | `bool \| None` | Enable speaker identification. |
| `enable_language_identification` | `bool \| None` | Enable automatic language detection. |
| `enable_endpoint_detection` | `bool \| None` | Enable endpoint detection for utterance boundaries. |
| `max_endpoint_delay_ms` | `int \| None` | Maximum delay between the end of speech and returned endpoint. Allowed values for maximum delay are between 500ms and 3000ms. The default value is 2000ms |
| `endpoint_sensitivity` | `float \| None` | Adjusts how likely the model is to emit an endpoint. Higher values make endpoints more likely (finalizing sooner); lower values make them less likely. Allowed values are between -1.0 and 1.0; the default is 0.0. Introduced in the Soniox v5 model; earlier models reject it. |
| `endpoint_latency_adjustment_level` | `int \| None` | Fine-tunes the latency/accuracy trade-off of endpoint detection. Allowed values are integers from 0 to 3. |
| `translation` | `TranslationConfigInput \| None` | Translation configuration. |
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

## RealtimeTTSConfig

Configuration for initiating a realtime Text-to-Speech stream.

<a id="realtimettsconfig-properties"></a>

### Properties

| Property | Type | Description |
| ------ | ------ | ------ |
| `api_key` | `str \| None` | API key for real-time sessions. |
| `stream_id` | `str` | Client stream identifier unique among active streams on a connection. |
| `model` | `str` | Text-to-Speech model to use. |
| `language` | `str` | Language code for Text-to-Speech (e.g., "en"). |
| `voice` | `str` | Voice identifier to generate speech audio with. |
| `audio_format` | `TtsAudioFormat` | Requested output audio format. |
| `sample_rate` | `TtsSampleRate \| None` | Output sample rate in Hz. |
| `bitrate` | `TtsBitrate \| None` | Output bitrate in bits-per-second for compressed formats. |

<a id="realtimettsconfig-build_payload"></a>

### build_payload()

```python
build_payload(api_key: str) -> RealtimeTTSConfig
```

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `api_key` | `str` | API key used for authentication. |

**Returns**

`RealtimeTTSConfig`

---

## RealtimeTTSEvent

Event payload received from the realtime Text-to-Speech websocket.

<a id="realtimettsevent-properties"></a>

### Properties

| Property | Type | Description |
| ------ | ------ | ------ |
| `stream_id` | `str \| None` | Stream identifier associated with this event. |
| `audio` | `str \| None` | Base64 encoded audio chunk, when present. |
| `audio_end` | `bool` | Whether this event contains the last audio payload for the stream. |
| `terminated` | `bool` | Whether the stream has been fully terminated. |
| `error_code` | `int \| None` | Error code if the Text-to-Speech stream failed. |
| `error_message` | `str \| None` | Human-readable error message. |

<a id="realtimettsevent-validate_event"></a>

### validate_event()

```python
validate_event(raw: str | bytes) -> RealtimeTTSEvent
```

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `raw` | `str \| bytes` | Raw event payload from the realtime API. |

**Returns**

`RealtimeTTSEvent`

***

<a id="realtimettsevent-audio_bytes"></a>

### audio_bytes()

```python
audio_bytes() -> bytes | None
```

Decode and return the audio bytes for this event, if present.

**Returns**

`bytes | None`

---

## RealtimeTTSTextMessage

Text chunk message sent over realtime Text-to-Speech websocket.

<a id="realtimettstextmessage-properties"></a>

### Properties

| Property | Type | Description |
| ------ | ------ | ------ |
| `text` | `str` | Text chunk to generate into speech. |
| `text_end` | `bool` | Whether this message marks the final text chunk for the stream. |
| `stream_id` | `str` | Stream identifier the chunk belongs to. |

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