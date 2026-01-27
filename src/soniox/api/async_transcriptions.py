from __future__ import annotations

from typing import TYPE_CHECKING

from ..types import (
    CreateTranscriptionPayload,
    GetTranscriptionsPayload,
    GetTranscriptionsResponse,
    Transcription,
    TranscriptionTranscript,
)
from ._helpers import parse_async_response

if TYPE_CHECKING:
    from ..client import AsyncSonioxClient


class AsyncTranscriptionsAPI:
    """Async wrappers around `/v1/transcriptions` routes."""

    def __init__(self, client: AsyncSonioxClient) -> None:
        self._client = client

    async def list_transcriptions(
        self, limit: int = 1000, cursor: str | None = None
    ) -> GetTranscriptionsResponse:
        payload = GetTranscriptionsPayload(limit=limit, cursor=cursor)
        params = payload.model_dump(exclude_none=True)
        response = await self._client.request("GET", "/transcriptions", params=params)
        return await parse_async_response(response, GetTranscriptionsResponse)

    async def create_transcription(self, payload: CreateTranscriptionPayload) -> Transcription:
        response = await self._client.request(
            "POST", "/transcriptions", json=payload.model_dump(exclude_none=True)
        )
        return await parse_async_response(response, Transcription)

    async def get_transcription(self, transcription_id: str) -> Transcription:
        response = await self._client.request("GET", f"/transcriptions/{transcription_id}")
        return await parse_async_response(response, Transcription)

    async def delete_transcription(self, transcription_id: str) -> None:
        response = await self._client.request("DELETE", f"/transcriptions/{transcription_id}")
        response.raise_for_status()

    async def get_transcription_transcript(self, transcription_id: str) -> TranscriptionTranscript:
        response = await self._client.request(
            "GET", f"/transcriptions/{transcription_id}/transcript"
        )
        return await parse_async_response(response, TranscriptionTranscript)
