from __future__ import annotations

import time
from pathlib import Path
from typing import TYPE_CHECKING, Any, BinaryIO

from ..errors import SonioxValidationError
from ..types import (
    CreateTranscriptionPayload,
    GetTranscriptionsPayload,
    GetTranscriptionsResponse,
    Transcription,
    TranscriptionTranscript,
    WebhookAuthConfig,
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

    def delete_all(self, *, limit: int = 1000) -> None:
        cursor: str | None = None
        while True:
            page = self.list(limit=limit, cursor=cursor)
            for transcription in page.transcriptions:
                self.delete(transcription.id)
            if not page.next_page_cursor:
                break
            cursor = page.next_page_cursor

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

    def destroy(self, transcription_id: str) -> None:
        """Delete transcription and the uploaded file that kicked it off."""
        transcription = self.get(transcription_id)
        self.delete(transcription_id)
        if transcription.file_id:
            self._client.files.delete(transcription.file_id)

    def get_transcript(self, transcription_id: str) -> TranscriptionTranscript:
        response = self._client.request("GET", f"/transcriptions/{transcription_id}/transcript")
        return parse_response(response, TranscriptionTranscript)

    def wait(
        self,
        transcription_id: str,
        *,
        interval_sec: float = 5.0,
        timeout_sec: float | None = None,
    ) -> Transcription:
        """Poll a transcription until it transitions out of processing state."""
        deadline = time.monotonic() + timeout_sec if timeout_sec is not None else None
        while True:
            transcription = self.get(transcription_id)
            if transcription.status not in ("queued", "processing"):
                return transcription
            if deadline is not None and time.monotonic() >= deadline:
                raise TimeoutError(f"Timed out waiting for transcription {transcription_id}")
            time.sleep(interval_sec)

    def transcribe_from_url(
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
        return self.create(payload)

    def transcribe_from_file_id(
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
        return self.create(payload)

    def transcribe_from_file(
        self,
        *,
        model: str,
        file: BinaryIO | bytes | Path,
        filename: str | None = None,
        client_reference_id: str | None = None,
        **payload_kwargs: Any,
    ) -> Transcription:
        uploaded = self._client.files.upload(
            file,
            filename=filename,
            client_reference_id=client_reference_id,
        )
        return self.transcribe_from_file_id(
            model=model,
            file_id=uploaded.id,
            client_reference_id=client_reference_id,
            **payload_kwargs,
        )

    def transcribe(
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
            return self.transcribe_from_file(
                model=model,
                file=file,
                filename=filename,
                client_reference_id=client_reference_id,
                **payload_kwargs,
            )
        if file_id is not None:
            if audio_url:
                raise SonioxValidationError("file_id cannot be combined with audio_url")
            return self.transcribe_from_file_id(
                model=model,
                file_id=file_id,
                **payload_kwargs,
            )
        if not audio_url:
            raise SonioxValidationError("Either audio_url, file_id, or file must be provided")
        return self.transcribe_from_url(
            model=model,
            audio_url=audio_url,
            **payload_kwargs,
        )

    def transcribe_file_with_webhook(
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
        """Upload a file, configure the webhook, and start transcription."""
        webhook_fields = self._client.webhooks.webhook_payload(webhook_url, auth=webhook_auth)
        uploaded = self._client.files.upload(
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
        return self.create(payload)

    def transcribe_and_wait(
        self,
        *,
        model: str,
        audio_url: str | None = None,
        file_id: str | None = None,
        file: BinaryIO | bytes | Path | None = None,
        filename: str | None = None,
        client_reference_id: str | None = None,
        wait: bool = True,
        wait_interval_sec: float = 5.0,
        wait_timeout_sec: float | None = None,
        **payload_kwargs: Any,
    ) -> Transcription:
        transcription = self.transcribe(
            model=model,
            audio_url=audio_url,
            file_id=file_id,
            file=file,
            filename=filename,
            client_reference_id=client_reference_id,
            **payload_kwargs,
        )
        if wait:
            return self.wait(
                transcription.id,
                interval_sec=wait_interval_sec,
                timeout_sec=wait_timeout_sec,
            )
        return transcription
