from __future__ import annotations

import asyncio
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any, BinaryIO

from ..errors import SonioxValidationError
from ..errors import SonioxNotFoundError
from ..types import (
    CreateTranscriptionPayload,
    GetTranscriptionsPayload,
    GetTranscriptionsResponse,
    Transcription,
    TranscriptionTranscript,
    WebhookAuthConfig,
)
from ._utils import ensure_success, parse_async_response

if TYPE_CHECKING:
    from ..client import AsyncSonioxClient


class AsyncTranscriptionsAPI:
    def __init__(self, client: AsyncSonioxClient) -> None:
        self._client = client

    async def list(
        self,
        limit: int = 1000,
        cursor: str | None = None,
    ) -> GetTranscriptionsResponse:
        payload = GetTranscriptionsPayload(limit=limit, cursor=cursor)
        params = payload.model_dump(exclude_none=True)
        response = await self._client.request("GET", "/transcriptions", params=params)
        return await parse_async_response(response, GetTranscriptionsResponse)

    async def delete_all(self, *, limit: int = 1000) -> None:
        cursor: str | None = None
        while True:
            page = await self.list(limit=limit, cursor=cursor)
            for transcription in page.transcriptions:
                await self.delete(transcription.id)
            if not page.next_page_cursor:
                break
            cursor = page.next_page_cursor

    async def create(self, payload: CreateTranscriptionPayload) -> Transcription:
        response = await self._client.request(
            "POST", "/transcriptions", json=payload.model_dump(exclude_none=True)
        )
        return await parse_async_response(response, Transcription)

    async def get(self, transcription_id: str) -> Transcription:
        response = await self._client.request("GET", f"/transcriptions/{transcription_id}")
        return await parse_async_response(response, Transcription)

    async def get_or_none(self, transcription_id: str) -> Transcription | None:
        try:
            return await self.get(transcription_id)
        except SonioxNotFoundError:
            return None

    async def delete(self, transcription_id: str) -> None:
        response = await self._client.request("DELETE", f"/transcriptions/{transcription_id}")
        ensure_success(response)

    async def delete_if_exists(self, transcription_id: str) -> None:
        try:
            await self.delete(transcription_id)
        except SonioxNotFoundError:
            return

    async def destroy(self, transcription_id: str) -> None:
        transcription = await self.get(transcription_id)
        await self.delete(transcription_id)
        if transcription.file_id:
            await self._client.files.delete(transcription.file_id)

    async def get_transcript(self, transcription_id: str) -> TranscriptionTranscript:
        response = await self._client.request(
            "GET", f"/transcriptions/{transcription_id}/transcript"
        )
        return await parse_async_response(response, TranscriptionTranscript)

    async def wait(
        self,
        transcription_id: str,
        *,
        interval_sec: float = 5.0,
        timeout_sec: float | None = None,
    ) -> Transcription:
        deadline = time.monotonic() + timeout_sec if timeout_sec is not None else None
        while True:
            transcription = await self.get(transcription_id)
            if transcription.status not in ("queued", "processing"):
                return transcription
            if deadline is not None and time.monotonic() >= deadline:
                raise TimeoutError(f"Timed out waiting for transcription {transcription_id}")
            await asyncio.sleep(interval_sec)

    async def transcribe_from_url(
        self,
        *,
        model: str,
        audio_url: str,
        **payload_kwargs: Any,
    ) -> Transcription:
        payload = CreateTranscriptionPayload(
            model=model,
            audio_url=audio_url,
            **payload_kwargs,
        )
        return await self.create(payload)

    async def transcribe_from_file_id(
        self,
        *,
        model: str,
        file_id: str,
        **payload_kwargs: Any,
    ) -> Transcription:
        payload = CreateTranscriptionPayload(
            model=model,
            file_id=file_id,
            **payload_kwargs,
        )
        return await self.create(payload)

    async def transcribe_from_file(
        self,
        *,
        model: str,
        file: BinaryIO | bytes | Path,
        filename: str | None = None,
        client_reference_id: str | None = None,
        **payload_kwargs: Any,
    ) -> Transcription:
        uploaded = await self._client.files.upload(
            file,
            filename=filename,
            client_reference_id=client_reference_id,
        )
        return await self.transcribe_from_file_id(
            model=model,
            file_id=uploaded.id,
            client_reference_id=client_reference_id,
            **payload_kwargs,
        )

    async def transcribe(
        self,
        *,
        model: str,
        audio_url: str | None = None,
        file_id: str | None = None,
        file: BinaryIO | bytes | Path | None = None,
        filename: str | None = None,
        client_reference_id: str | None = None,
        **payload_kwargs: Any,
    ) -> Transcription:
        if file is not None:
            if audio_url or file_id:
                raise SonioxValidationError("file cannot be combined with audio_url or file_id")
            return await self.transcribe_from_file(
                model=model,
                file=file,
                filename=filename,
                client_reference_id=client_reference_id,
                **payload_kwargs,
            )
        if file_id is not None:
            if audio_url:
                raise SonioxValidationError("file_id cannot be combined with audio_url")
            return await self.transcribe_from_file_id(
                model=model,
                file_id=file_id,
                **payload_kwargs,
            )
        if not audio_url:
            raise SonioxValidationError("Either audio_url, file_id, or file must be provided")
        return await self.transcribe_from_url(
            model=model,
            audio_url=audio_url,
            **payload_kwargs,
        )

    async def transcribe_file_with_webhook(
        self,
        *,
        model: str,
        file: BinaryIO | bytes | Path,
        webhook_url: str,
        filename: str | None = None,
        client_reference_id: str | None = None,
        webhook_auth: WebhookAuthConfig | None = None,
        **payload_kwargs: Any,
    ) -> Transcription:
        webhook_fields = self._client.webhooks.webhook_payload(webhook_url, auth=webhook_auth)
        uploaded = await self._client.files.upload(
            file,
            filename=filename,
            client_reference_id=client_reference_id,
        )
        payload_data = {**payload_kwargs, **webhook_fields}
        payload = CreateTranscriptionPayload(
            model=model,
            file_id=uploaded.id,
            client_reference_id=client_reference_id,
            **payload_data,
        )
        return await self.create(payload)

    async def transcribe_and_wait(
        self,
        *,
        model: str,
        audio_url: str | None = None,
        file_id: str | None = None,
        file: BinaryIO | bytes | Path | None = None,
        filename: str | None = None,
        client_reference_id: str | None = None,
        wait: bool = True,
        delete_after: bool = False,
        wait_interval_sec: float = 5.0,
        wait_timeout_sec: float | None = None,
        **payload_kwargs: Any,
    ) -> Transcription:
        if delete_after and not wait:
            raise SonioxValidationError("delete_after requires wait=True")

        transcription = await self.transcribe(
            model=model,
            audio_url=audio_url,
            file_id=file_id,
            file=file,
            filename=filename,
            client_reference_id=client_reference_id,
            **payload_kwargs,
        )
        if wait:
            transcription = await self.wait(
                transcription.id,
                interval_sec=wait_interval_sec,
                timeout_sec=wait_timeout_sec,
            )
        if delete_after:
            file_id_to_delete = transcription.file_id
            await self.delete(transcription.id)
            if file_id_to_delete:
                await self._client.files.delete(file_id_to_delete)
        return transcription
