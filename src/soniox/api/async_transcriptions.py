from __future__ import annotations

from typing import TYPE_CHECKING

from ..types import (
    CreateTranscriptionPayload,
    GetTranscriptionsPayload,
    GetTranscriptionsResponse,
    Transcription,
    TranscriptionTranscript,
)
from ._utils import ensure_success, parse_async_response

if TYPE_CHECKING:
    from ..client import AsyncSonioxClient


class AsyncTranscriptionsAPI:
    def __init__(self, client: AsyncSonioxClient) -> None:
        self._client = client

    async def list(self, limit: int = 1000, cursor: str | None = None) -> GetTranscriptionsResponse:
        payload = GetTranscriptionsPayload(limit=limit, cursor=cursor)
        params = payload.model_dump(exclude_none=True)
        response = await self._client.request("GET", "/transcriptions", params=params)
        return await parse_async_response(response, GetTranscriptionsResponse)

    async def create(self, payload: CreateTranscriptionPayload) -> Transcription:
        response = await self._client.request(
            "POST", "/transcriptions", json=payload.model_dump(exclude_none=True)
        )
        return await parse_async_response(response, Transcription)

    async def get(self, transcription_id: str) -> Transcription:
        response = await self._client.request("GET", f"/transcriptions/{transcription_id}")
        return await parse_async_response(response, Transcription)

    async def delete(self, transcription_id: str) -> None:
        response = await self._client.request("DELETE", f"/transcriptions/{transcription_id}")
        ensure_success(response)

    async def destroy(self) -> None:
        "Delete transcript and its underlying uploaded file (if any)"
        raise NotImplementedError()

    async def get_transcript(self, transcription_id: str) -> TranscriptionTranscript:
        response = await self._client.request(
            "GET", f"/transcriptions/{transcription_id}/transcript"
        )
        return await parse_async_response(response, TranscriptionTranscript)

    async def wait(self) -> None:
        "Pool until transcript is complete (blocking)"
        raise NotImplementedError()

    async def transcribe_from_url(self) -> None:
        raise NotImplementedError()

    async def transcribe_from_file_id(self) -> None:
        raise NotImplementedError()

    async def transcribe_from_file(self) -> None:
        raise NotImplementedError()

    async def transcribe(self) -> None:
        raise NotImplementedError()
