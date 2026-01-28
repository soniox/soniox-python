from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator
from typing_extensions import Self

TranscriptionStatus = Literal["queued", "processing", "completed", "error"]
TranscriptionMode = Literal["real_time", "async"]
TranslationType = Literal["one_way", "two_way"]
TemporaryApiKeyUsageType = Literal["transcribe_websocket"]


class ApiErrorValidationError(BaseModel):
    error_type: str
    location: str
    message: str


class ApiError(BaseModel):
    status_code: int
    error_type: str
    message: str
    validation_errors: list[ApiErrorValidationError]
    request_id: str


class GetFilesPayload(BaseModel):
    limit: int = Field(default=1000, ge=1, le=1000)
    cursor: str | None = None


class File(BaseModel):
    id: str
    filename: str
    size: int
    created_at: datetime
    client_reference_id: str | None = None


class GetFilesResponse(BaseModel):
    files: list[File]
    next_page_cursor: str | None = None


class UploadFilePayload(BaseModel):
    client_reference_id: str | None = Field(default=None, max_length=256)


class GetTranscriptionsPayload(BaseModel):
    limit: int = Field(default=1000, ge=1, le=1000)
    cursor: str | None = None


class StructuredContextGeneralItem(BaseModel):
    key: str
    value: str


class StructuredContextTranslationTerm(BaseModel):
    source: str
    target: str


class StructuredContext(BaseModel):
    general: list[StructuredContextGeneralItem] | None = None
    text: str | None = None
    terms: list[str] | None = None
    translation_terms: list[StructuredContextTranslationTerm] | None = None


class TranslationConfig(BaseModel):
    type: TranslationType
    target_language: str | None = None
    language_a: str | None = None
    language_b: str | None = None


class CreateTranscriptionPayload(BaseModel):
    model: str
    audio_url: str | None = None
    file_id: str | None = None
    language_hints: list[str] | None = None
    language_hints_strict: bool | None = None
    enable_speaker_diarization: bool | None = None
    enable_language_identification: bool | None = None
    translation: TranslationConfig | None = None
    context: StructuredContext | str | None = None
    webhook_url: str | None = None
    webhook_auth_header_name: str | None = None
    webhook_auth_header_value: str | None = None
    client_reference_id: str | None = Field(default=None, max_length=256)

    @model_validator(mode="after")
    def _validate_audio_source(self) -> Self:
        if self.audio_url and self.file_id:
            raise ValueError("Only one of audio_url or file_id can be provided.")
        if not self.audio_url and not self.file_id:
            raise ValueError("Either audio_url or file_id must be provided.")
        return self


class CreateTemporaryApiKeyPayload(BaseModel):
    usage_type: TemporaryApiKeyUsageType
    expires_in_seconds: int = Field(..., ge=1, le=3600)
    client_reference_id: str | None = Field(default=None, max_length=256)


class CreateTemporaryApiKeyResponse(BaseModel):
    api_key: str
    expires_at: datetime


class Language(BaseModel):
    code: str
    name: str


class TranslationTarget(BaseModel):
    target_language: str
    source_languages: list[str]
    exclude_source_languages: list[str]


class Model(BaseModel):
    id: str
    aliased_model_id: str | None
    name: str
    context_version: int | None
    transcription_mode: TranscriptionMode
    languages: list[Language]
    supports_language_hints_strict: bool
    translation_targets: list[TranslationTarget]
    two_way_translation_pairs: list[str]
    one_way_translation: str | None
    two_way_translation: str | None


class GetModelsResponse(BaseModel):
    models: list[Model]


class TranscriptionTranscriptToken(BaseModel):
    text: str
    start_ms: int
    end_ms: int
    confidence: float


class TranscriptionTranscript(BaseModel):
    id: str
    text: str
    tokens: list[TranscriptionTranscriptToken]


class Transcription(BaseModel):
    id: str
    status: TranscriptionStatus
    created_at: datetime
    model: str
    audio_url: str | None = None
    file_id: str | None = None
    filename: str
    language_hints: list[str] | None = None
    enable_speaker_diarization: bool
    enable_language_identification: bool
    audio_duration_ms: int | None = None
    error_type: str | None = None
    error_message: str | None = None
    webhook_url: str | None = None
    webhook_auth_header_name: str | None = None
    webhook_auth_header_value: str | None = None
    webhook_status_code: int | None = None
    client_reference_id: str | None = None


class GetTranscriptionsResponse(BaseModel):
    transcriptions: list[Transcription]
    next_page_cursor: str | None = None
