from __future__ import annotations

from typing import TYPE_CHECKING

from ..types import (
    CreateTranscriptionPayload,
    GetTranscriptionsPayload,
    GetTranscriptionsResponse,
    Transcription,
    TranscriptionTranscript,
)
from ._utils import ensure_success, parse_response

if TYPE_CHECKING:
    from ..client import SonioxClient


class TranscriptionsAPI:
    def __init__(self, client: SonioxClient) -> None:
        self._client = client

    def list(self, limit: int = 1000, cursor: str | None = None) -> GetTranscriptionsResponse:
        payload = GetTranscriptionsPayload(limit=limit, cursor=cursor)
        params = payload.model_dump(exclude_none=True)
        response = self._client.request("GET", "/transcriptions", params=params)
        return parse_response(response, GetTranscriptionsResponse)

    def create(self, payload: CreateTranscriptionPayload) -> Transcription:
        response = self._client.request(
            "POST", "/transcriptions", json=payload.model_dump(exclude_none=True)
        )
        return parse_response(response, Transcription)

    def get(self, transcription_id: str) -> Transcription:
        response = self._client.request("GET", f"/transcriptions/{transcription_id}")
        return parse_response(response, Transcription)

    def delete(self, transcription_id: str) -> None:
        response = self._client.request("DELETE", f"/transcriptions/{transcription_id}")
        ensure_success(response)

    def destroy(self) -> None:
        "Delete transcript and its underlying uploaded file (if any)"
        raise NotImplementedError()

    def get_transcript(self, transcription_id: str) -> TranscriptionTranscript:
        response = self._client.request("GET", f"/transcriptions/{transcription_id}/transcript")
        return parse_response(response, TranscriptionTranscript)

    def wait(self) -> None:
        "Pool until transcript is complete (blocking)"
        raise NotImplementedError()

    def transcribe_from_url(self) -> None:
        raise NotImplementedError()

    def transcribe_from_file_id(self) -> None:
        raise NotImplementedError()

    def transcribe_from_file(self) -> None:
        raise NotImplementedError()

    def transcribe(self) -> None:
        raise NotImplementedError()
