from __future__ import annotations

from datetime import datetime
from typing import Annotated, Any, Literal, TypeAlias, cast

from pydantic import BaseModel, Field, field_validator, model_validator
from typing_extensions import Self

from .common import Token

TranscriptionStatus = Literal["queued", "processing", "completed", "error"]
"""Current status of the transcription job."""

TranscriptionMode = Literal["real_time", "async"]
"""Transcription mode supported by a model."""

TranslationType = Literal["one_way", "two_way"]
"""Supported translation configuration types."""

TemporaryApiKeyUsageType = Literal["transcribe_websocket", "tts_rt"]
"""Intended usage for temporary API keys."""


RealtimeSTTHeaderFormat = Literal[
    "aac", "aiff", "amr", "asf", "flac", "mp3", "ogg", "wav", "webm",
]
"""Container formats whose header carries sample rate and channels."""

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
"""Raw formats with no header - require ``sample_rate`` and ``num_channels``."""

RealtimeSTTAudioFormat = Literal["auto"] | RealtimeSTTHeaderFormat | RealtimeSTTRawFormat
"""Audio formats accepted by the realtime STT websocket."""


UsageLogsSort = Literal["end_time_asc", "end_time_desc"]
"""Sort order for usage-log entries by end_time."""

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
"""Allowed audio formats for Text-to-Speech output."""

TtsSampleRate = Literal[8000, 16000, 24000, 44100, 48000]
"""Allowed output sample rates in Hz for Text-to-Speech."""

TtsBitrate = Literal[32000, 64000, 96000, 128000, 192000, 256000, 320000]
"""Allowed output bitrates in bits-per-second for compressed Text-to-Speech formats."""

TtsVoiceGender = Literal["male", "female", "neutral"]
"""Reported gender of a Text-to-Speech voice."""


class ApiErrorValidationError(BaseModel):
    """Details a single validation error reported by the Soniox API."""

    error_type: str
    """The category of validation error."""

    location: str
    """The location of the error, e.g. ['body', 'audio_url']."""

    message: str
    """A human-readable description of the validation failure."""


class ApiError(BaseModel):
    """Structured representation of a non-2xx API response payload."""

    status_code: int
    """HTTP status code."""

    error_type: str
    """High-level error code (e.g., 'bad_request', 'quota_exceeded') for programmatic handling."""

    message: str
    """Detailed error message describing the failure."""

    validation_errors: list[ApiErrorValidationError] = Field(default=[])
    """List of specific field validation failures, if applicable."""

    request_id: str | None = None
    """Unique identifier for the request, useful for troubleshooting."""

    more_info: str | None = None
    """Optional URL pointing to documentation for resolving this error."""


class GetFilesPayload(BaseModel):
    """Parameters accepted by the file listing endpoint."""

    limit: int = Field(default=1000, ge=1, le=1000)
    """Maximum number of files to return."""

    cursor: str | None = None
    """Pagination cursor for the next page of results."""


class File(BaseModel):
    """Metadata describing an uploaded file in the Soniox API."""

    id: str
    """Unique identifier of the file (UUID)."""

    filename: str
    """Name of the file."""

    size: int
    """Size of the file in bytes."""

    created_at: datetime
    """UTC timestamp indicating when the file was uploaded."""

    client_reference_id: str | None = None
    """Optional tracking identifier string."""


class GetFilesResponse(BaseModel):
    """Paginated response returned when listing uploaded files."""

    files: list[File]
    """List of uploaded files."""

    next_page_cursor: str | None = None
    """A pagination token that references the next page of results. When None, no additional results are available."""


class GetFilesCountResponse(BaseModel):
    """Breakdown of uploaded file counts by source."""

    total: int
    """Total number of files across all sources."""

    public_api: int
    """Number of files uploaded via Public API."""

    playground: int
    """Number of files uploaded via the Playground."""


class UploadFilePayload(BaseModel):
    """Optional metadata supplied at upload time."""

    client_reference_id: str | None = Field(default=None, max_length=256)
    """Optional tracking identifier string. Does not need to be unique"""


class GetTranscriptionsPayload(BaseModel):
    """Parameters for listing transcription jobs."""

    limit: int = Field(default=1000, ge=1, le=1000)
    """Maximum number of transcriptions to return."""

    cursor: str | None = None
    """Pagination cursor for the next page of results."""


class StructuredContextGeneralItem(BaseModel):
    """Single general context key/value pair for transcription context."""

    key: str
    """The key describing the context type (e.g., "domain", "topic", "doctor")."""

    value: str
    """The value for the context key."""


class StructuredContextTranslationTerm(BaseModel):
    """Defines a translation term mapping used in structured context."""

    source: str
    """The source term to translate."""

    target: str
    """The target translation for the term."""


StructuredContextGeneralInput: TypeAlias = (
    list[StructuredContextGeneralItem] | dict[str, str]
)
"""Accepted input shapes for ``StructuredContext.general``."""

StructuredContextTranslationTermsInput: TypeAlias = (
    list[StructuredContextTranslationTerm] | dict[str, str]
)
"""Accepted input shapes for ``StructuredContext.translation_terms``."""


class StructuredContext(BaseModel):
    """Optional structured context provided to the transcription engine.

    For ergonomics, ``general`` and ``translation_terms`` also accept a plain
    dict in addition to the typed item lists:

    - ``general={"domain": "Healthcare"}`` (dict of key -> value)
    - ``translation_terms={"Mr. Smith": "Sr. Smith"}`` (dict of source -> target)
    """

    general: Annotated[StructuredContextGeneralInput, Field(union_mode="left_to_right")] | None = (
        None
    )
    """Structured key-value pairs describing domain, topic, intent, participant names, etc."""

    text: str | None = None
    """Longer free-form background text, prior interaction history, reference documents, or meeting notes."""

    terms: list[str] | None = None
    """Domain-specific or uncommon words to recognize."""

    translation_terms: (
        Annotated[StructuredContextTranslationTermsInput, Field(union_mode="left_to_right")] | None
    ) = None
    """Custom translations for ambiguous terms."""

    @field_validator("general", mode="before")
    @classmethod
    def _coerce_general(cls, v: Any) -> Any:
        if isinstance(v, dict):
            items_dict = cast("dict[str, str]", v)
            return [{"key": k, "value": val} for k, val in items_dict.items()]
        return v

    @field_validator("translation_terms", mode="before")
    @classmethod
    def _coerce_translation_terms(cls, v: Any) -> Any:
        if isinstance(v, dict):
            items_dict = cast("dict[str, str]", v)
            return [{"source": k, "target": val} for k, val in items_dict.items()]
        return v


StructuredContextInput: TypeAlias = StructuredContext | dict[str, Any]
"""Accepted input for the ``context`` field - typed object or a plain dict."""


class TranslationConfig(BaseModel):
    """Configuration describing how translation should be performed."""

    type: TranslationType
    """Translation type."""

    target_language: str | None = Field(default=None, min_length=2, max_length=2)
    """Target language code for translation (e.g., "fr", "es", "de") (one_way)."""

    language_a: str | None = Field(default=None, min_length=2, max_length=2)
    """First language code (two_way)."""

    language_b: str | None = Field(default=None, min_length=2, max_length=2)
    """Second language code (two_way)."""

    @model_validator(mode="after")
    def validate_logic(self) -> TranslationConfig:
        if self.type == "one_way":
            if not self.target_language:
                raise ValueError("target_language is required for one_way")
            # Clean up other fields if user passed them by accident
            self.language_a = self.language_b = None

        elif self.type == "two_way":
            if not self.language_a or not self.language_b:
                raise ValueError("language_a and language_b are both required for two_way")
            # Clean up other fields if user passed them by accident
            self.target_language = None

        return self


TranslationConfigInput: TypeAlias = TranslationConfig | dict[str, Any]
"""Accepted input for the ``translation`` field - typed object or a plain dict."""


class CreateTranscriptionPayload(BaseModel):
    """Payload sent to create an asynchronous transcription job."""

    model: str = "stt-async-v4"
    """Speech-to-text model to use."""

    audio_url: str | None = None
    """URL of a publicly accessible audio file."""

    file_id: str | None = None
    """ID of a previously uploaded file (UUID)."""

    language_hints: list[str] | None = None
    """Array of expected ISO language codes to bias recognition."""

    language_hints_strict: bool | None = None
    """When true, model relies more heavily on language hints (best results with one language hint set)."""

    enable_speaker_diarization: bool | None = None
    """Enable speaker diarization to identify different speakers."""

    enable_language_identification: bool | None = None
    """Enable automatic language identification."""

    translation: TranslationConfigInput | None = None
    """Translation configuration."""

    context: StructuredContextInput | None = None
    """Additional context to improve transcription accuracy and formatting of specialized terms."""

    webhook_url: str | None = Field(default=None, max_length=256)
    """URL to receive webhook notifications when transcription is completed or fails."""

    webhook_auth_header_name: str | None = Field(default=None, max_length=256)
    """Name of the authentication header sent with webhook notifications"""

    webhook_auth_header_value: str | None = Field(default=None, max_length=256)
    """Authentication header value sent with webhook notifications."""

    client_reference_id: str | None = Field(default=None, max_length=256)
    """Optional tracking identifier."""

    @model_validator(mode="after")
    def _validate_audio_source(self) -> Self:
        if self.audio_url and self.file_id:
            raise ValueError("Only one of audio_url or file_id can be provided.")
        if not self.audio_url and not self.file_id:
            raise ValueError("Either audio_url or file_id must be provided.")
        return self


class CreateTranscriptionConfig(BaseModel):
    """Helper config used when building transcription payloads."""

    model: str | None = None
    """Speech-to-text model to use."""

    language_hints: list[str] | None = None
    """Array of expected ISO language codes to bias recognition."""

    language_hints_strict: bool | None = None
    """When true, model relies more heavily on language hints."""

    enable_speaker_diarization: bool | None = None
    """Enable speaker diarization to identify different speakers."""

    enable_language_identification: bool | None = None
    """Enable automatic language identification"""

    translation: TranslationConfigInput | None = None
    """Translation configuration"""

    context: StructuredContextInput | None = None
    """Additional context to improve transcription accuracy and formatting of specialized terms."""

    webhook_url: str | None = Field(default=None, max_length=256)
    """URL to receive webhook notifications when transcription is completed or fails."""

    webhook_auth_header_name: str | None = None
    """Name of the authentication header sent with webhook notifications"""

    webhook_auth_header_value: str | None = None
    """Authentication header value sent with webhook notifications"""

    client_reference_id: str | None = Field(default=None, max_length=256)
    """Optional tracking identifier"""


class CreateTtsPayload(BaseModel):
    """Payload sent to generate speech audio from text via REST."""

    model: str = Field(min_length=1, max_length=50)
    """Text-to-Speech model to use."""

    language: str = Field(min_length=1, max_length=50)
    """Language code for Text-to-Speech (e.g., "en")."""

    voice: str = Field(min_length=1, max_length=50)
    """Voice identifier to generate speech audio with."""

    audio_format: TtsAudioFormat
    """Requested output audio format."""

    sample_rate: TtsSampleRate | None = Field(default=None)
    """Output sample rate in Hz."""

    bitrate: TtsBitrate | None = Field(default=None)
    """Output bitrate in bits-per-second for compressed formats."""

    text: str = Field(min_length=1, max_length=5000)
    """Input text to generate into speech."""


class CreateTtsConfig(BaseModel):
    """Helper config used when building Text-to-Speech payloads."""

    model: str | None = Field(default=None, min_length=1, max_length=50)
    """Text-to-Speech model to use."""

    language: str | None = Field(default=None, min_length=1, max_length=50)
    """Language code for Text-to-Speech (e.g., "en")."""

    voice: str | None = Field(default=None, min_length=1, max_length=50)
    """Voice identifier to generate speech audio with."""

    audio_format: TtsAudioFormat | None = Field(default=None)
    """Requested output audio format."""

    sample_rate: TtsSampleRate | None = Field(default=None)
    """Output sample rate in Hz."""

    bitrate: TtsBitrate | None = Field(default=None)
    """Output bitrate in bits-per-second for compressed formats."""


class CreateTemporaryApiKeyPayload(BaseModel):
    """Payload for requesting a temporary API key (e.g., websocket)."""

    usage_type: TemporaryApiKeyUsageType
    """Intended usage of the temporary API key."""

    expires_in_seconds: int = Field(..., ge=1, le=3600)
    """Duration in seconds until the temporary API key expires"""

    client_reference_id: str | None = Field(default=None, max_length=256)
    """Optional tracking identifier string. Does not need to be unique"""

    single_use: bool | None = None
    """When true, restricts the temporary API key to a single use."""

    max_session_duration_seconds: int | None = Field(default=None, ge=1, le=18000)
    """Maximum connection duration in seconds for WebSocket and TTS HTTP streaming endpoints."""


class CreateTemporaryApiKeyResponse(BaseModel):
    """Response data for a temp API key request."""

    api_key: str
    """Created temporary API key."""

    expires_at: datetime
    """UTC timestamp indicating when generated temporary API key will expire"""


class Language(BaseModel):
    """Represents a supported language for transcription or translation."""

    code: str
    """2-letter language code (ISO format)."""

    name: str
    """Language name."""


class TranslationTarget(BaseModel):
    """Describes translation targets offered by a model."""

    target_language: str
    source_languages: list[str]
    exclude_source_languages: list[str]


class Model(BaseModel):
    """Describes a Soniox transcription model."""

    id: str
    """Unique identifier of the model."""

    aliased_model_id: str | None = None
    """If this is an alias, the id of the aliased model. None for non-alias models."""

    name: str
    """Name of the model."""

    context_version: int | None
    """Version of context supported."""

    transcription_mode: TranscriptionMode
    """Transcription mode of the model."""

    languages: list[Language]
    """List of languages supported by the model."""

    supports_language_hints_strict: bool
    """If model supports 'language_hints_strict' option."""

    supports_max_endpoint_delay: bool = False
    """If model supports 'max_endpoint_delay_ms' option."""

    translation_targets: list[TranslationTarget]
    """List of supported one-way translation targets. If list is empty, check for one_way_translation field."""

    two_way_translation_pairs: list[str]
    """List of supported two-way translation pairs. If list is empty, check for one_way_translation field."""

    one_way_translation: str | None
    """When contains string 'all_languages', any language from languages can be used"""

    two_way_translation: str | None
    """When contains string 'all_languages',' any language pair from languages can be used"""


class GetModelsResponse(BaseModel):
    """Response returned when listing available models."""

    models: list[Model]
    """List of all available models."""


class TtsVoice(BaseModel):
    """Represents a Text-to-Speech voice."""

    id: str
    """Unique identifier of the voice."""

    description: str
    """Description of the voice."""

    gender: TtsVoiceGender
    """Gender of the voice."""


class TtsModel(BaseModel):
    """Represents a Text-to-Speech model."""

    id: str
    """Unique identifier of the model."""

    aliased_model_id: str | None = None
    """If this is an alias, the id of the aliased model. None for non-alias models."""

    name: str
    """Name of the model."""

    voices: list[TtsVoice]
    """Voices supported by this model."""

    languages: list[Language] = []
    """Languages supported by this model."""


class GetTtsModelsResponse(BaseModel):
    """Response returned when listing available Text-to-Speech models."""

    models: list[TtsModel]
    """List of available Text-to-Speech models."""


class TranscriptionTranscript(BaseModel):
    """Transcript data including the full text and tokens."""

    id: str
    """Unique identifier of the transcription this transcript belongs to (UUID)."""

    text: str
    """Complete transcribed text content."""

    tokens: list[Token]
    """List of detailed token information with timestamps and metadata."""


class Transcription(BaseModel):
    """Represents a transcription job tracked by Soniox."""

    id: str
    """Unique identifier of the transcription (UUID)."""

    status: TranscriptionStatus
    """Current status of the transcription."""

    created_at: datetime
    """UTC timestamp when the transcription was created."""

    model: str
    """Speech-to-text model used."""

    audio_url: str | None = None
    """URL of the audio file being transcribed."""

    file_id: str | None = None
    """ID of the uploaded file being transcribed (UUID)."""

    filename: str
    """Name of the file being transcribed."""

    language_hints: list[str] | None = None
    """Expected languages in the audio. If not specified, languages are automatically detected."""

    enable_speaker_diarization: bool
    """When true, speakers are identified and separated in the transcription output."""

    enable_language_identification: bool
    """When true, language is detected for each part of the transcription."""

    audio_duration_ms: int | None = None
    """Duration of the audio in milliseconds. Only available after processing begins."""

    error_type: str | None = None
    """Error type if transcription failed. None for successful or in-progress transcriptions."""

    error_message: str | None = None
    """Error message if transcription failed. None for successful or in-progress transcriptions."""

    webhook_url: str | None = None
    """URL to receive webhook notifications when transcription is completed or fails."""

    webhook_auth_header_name: str | None = None
    """Name of the authentication header sent with webhook notifications."""

    webhook_auth_header_value: str | None = None
    """Authentication header value. Always returned masked."""

    webhook_status_code: int | None = None
    """HTTP status code received from your server when webhook was delivered. None if not yet sent."""

    client_reference_id: str | None = None
    """Optional tracking identifier."""


class GetTranscriptionsResponse(BaseModel):
    """Paginated response for transcription listings."""

    transcriptions: list[Transcription]
    """List of transcriptions."""

    next_page_cursor: str | None = None
    """A pagination token that references the next page of results. When None, no additional results are available."""


class GetTranscriptionsCountResponse(BaseModel):
    """Breakdown of transcription counts by scope."""

    total: int
    """Total number of transcriptions across all scopes."""

    public_api: int
    """Number of transcriptions created via Public API."""

    playground: int
    """Number of transcriptions created via the Playground."""


class GetUsageLogsPayload(BaseModel):
    """Parameters accepted by the usage logs listing endpoint."""

    start_time: str
    """Start of the time window (inclusive). Filters by request end time."""

    end_time: str
    """End of the time window (exclusive). Filters by request end time."""

    limit: int = Field(default=1000, ge=1, le=1000)
    """Maximum number of usage log entries to return."""

    sort: UsageLogsSort = "end_time_asc"
    """Sort order by end_time. Use `end_time_desc` to get the most recent entries first."""

    cursor: str | None = None
    """Pagination cursor for the next page of results."""


class UsageLogEntry(BaseModel):
    """A single usage-log entry describing one API request."""

    uuid: str
    """Unique identifier of the request."""

    request_scope: str
    """Scope of the request (api / playground)."""

    client_reference_id: str
    """Client reference ID supplied on the original request. Empty string if none."""

    model: str
    """Model identifier."""

    start_time: datetime
    """When the request started."""

    end_time: datetime
    """When the request ended."""

    input_text_tokens: int
    input_audio_tokens: int
    input_audio_duration_ms: int
    output_text_tokens: int
    output_audio_tokens: int
    output_audio_duration_ms: int

    cost_usd: str
    input_cost_usd: str
    input_text_cost_usd: str
    input_audio_cost_usd: str
    output_cost_usd: str
    output_text_cost_usd: str
    output_audio_cost_usd: str


class GetUsageLogsResponse(BaseModel):
    """Paginated response for usage-log listings."""

    usage_logs: list[UsageLogEntry]
    """Per-request usage log entries ordered by end_time."""

    next_page_cursor: str | None = None
    """Pagination cursor for the next page of results. None if no more pages."""


class ConcurrencyCurrentValues(BaseModel):
    """Live counts of concurrent sessions."""

    transcribe_concurrent: int
    """Number of concurrent realtime STT sessions currently active."""

    tts_concurrent: int
    """Number of concurrent realtime TTS sessions currently active."""


class ConcurrencyLimitValues(BaseModel):
    """Configured concurrency limits. None means no limit."""

    transcribe_concurrent: int | None
    """Maximum concurrent realtime STT sessions, or None if unlimited."""

    tts_concurrent: int | None
    """Maximum concurrent realtime TTS sessions, or None if unlimited."""


class ConcurrencyScopeValues(BaseModel):
    """Current and limit values for a single scope (project or organization)."""

    current: ConcurrencyCurrentValues
    """Live counts of active sessions."""

    limits: ConcurrencyLimitValues
    """Configured limits."""


class GetConcurrencyLimitsResponse(BaseModel):
    """Response returned when fetching concurrency limits."""

    project: ConcurrencyScopeValues
    """Project-scoped current counts and configured limits."""

    organization: ConcurrencyScopeValues
    """Organization-scoped current counts and configured limits."""
