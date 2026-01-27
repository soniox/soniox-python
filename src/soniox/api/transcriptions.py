from __future__ import annotations

from typing import TYPE_CHECKING

from ..types import (
    CreateTranscriptionPayload,
    GetTranscriptionsPayload,
    GetTranscriptionsResponse,
    Transcription,
    TranscriptionTranscript,
)
from ._helpers import parse_response

if TYPE_CHECKING:
    from ..client import SonioxClient


class TranscriptionsAPI:
    def __init__(self, client: SonioxClient) -> None:
        self._client = client

    def list_transcriptions(
        self, limit: int = 1000, cursor: str | None = None
    ) -> GetTranscriptionsResponse:
        payload = GetTranscriptionsPayload(limit=limit, cursor=cursor)
        params = payload.model_dump(exclude_none=True)
        response = self._client.request("GET", "/transcriptions", params=params)
        return parse_response(response, GetTranscriptionsResponse)

    def create_transcription(self, payload: CreateTranscriptionPayload) -> Transcription:
        response = self._client.request(
            "POST", "/transcriptions", json=payload.model_dump(exclude_none=True)
        )
        return parse_response(response, Transcription)

    def get_transcription(self, transcription_id: str) -> Transcription:
        response = self._client.request("GET", f"/transcriptions/{transcription_id}")
        return parse_response(response, Transcription)

    def delete_transcription(self, transcription_id: str) -> None:
        response = self._client.request("DELETE", f"/transcriptions/{transcription_id}")
        response.raise_for_status()

    def get_transcription_transcript(self, transcription_id: str) -> TranscriptionTranscript:
        response = self._client.request("GET", f"/transcriptions/{transcription_id}/transcript")
        return parse_response(response, TranscriptionTranscript)
