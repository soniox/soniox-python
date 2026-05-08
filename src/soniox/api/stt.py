from __future__ import annotations

import time
from collections.abc import Generator
from pathlib import Path
from typing import TYPE_CHECKING, BinaryIO

from ..errors import SonioxNotFoundError, SonioxValidationError
from ..types import (
    CreateTranscriptionConfig,
    GetTranscriptionsCountResponse,
    GetTranscriptionsPayload,
    GetTranscriptionsResponse,
    Transcription,
    TranscriptionTranscript,
    WebhookAuthConfig,
)
from ._utils import build_create_payload, ensure_success, parse_response

if TYPE_CHECKING:
    from ..client import SonioxClient

DEFAULT_MODEL = "stt-async-v4"


class SttAPI:
    def __init__(self, client: SonioxClient) -> None:
        self._client = client

    def list(self, limit: int = 100, cursor: str | None = None) -> GetTranscriptionsResponse:
        """
        List transcriptions.

        Performs a GET request to ``/transcriptions`` with optional pagination.

        Raises:
            SonioxAPIError: When the API returns an error.
        """
        payload = GetTranscriptionsPayload(limit=limit, cursor=cursor)
        params = payload.model_dump(exclude_none=True)
        response = self._client.request("GET", "/transcriptions", params=params)
        return parse_response(response, GetTranscriptionsResponse)

    def count(self) -> GetTranscriptionsCountResponse:
        """
        Return a breakdown of transcription counts.

        Performs a GET request to ``/transcriptions/count``.

        Raises:
            SonioxAPIError: When the API returns an error.
        """
        response = self._client.request("GET", "/transcriptions/count")
        return parse_response(response, GetTranscriptionsCountResponse)

    def list_all(self, limit: int = 100) -> Generator[Transcription, None, None]:
        """
        Iterate through all transcriptions across all pages.

        Yields:
            File: The next transcription object from the API.

        Raises:
            SonioxAPIError: When the API returns an error.
        """
        cursor = None
        while True:
            response = self.list(limit=limit, cursor=cursor)

            yield from response.transcriptions

            cursor = response.next_page_cursor
            if not cursor:
                break

    def delete_all(self, limit: int = 100) -> None:
        """
        Delete all transcriptions.

        Iterates through all pages and deletes each transcription. Stops and raises on the first failed deletion.

        Raises:
            SonioxAPIError: When the API returns an error.
        """
        for transcription in self.list_all(limit=limit):
            self.delete_if_exists(transcription.id)

    def create(
        self,
        *,
        model: str = DEFAULT_MODEL,
        file_id: str | None = None,
        audio_url: str | None = None,
        client_reference_id: str | None = None,
        config: CreateTranscriptionConfig | None = None,
    ) -> Transcription:
        """
        Create a transcription.

        Performs a POST request to ``/transcriptions``.

        Raises:
            SonioxAPIError: When the API returns an error.
        """
        if file_id is not None and audio_url is not None:
            raise SonioxValidationError("Provide either file_id or audio_url, not both")
        payload = build_create_payload(
            model=model,
            file_id=file_id,
            audio_url=audio_url,
            client_reference_id=client_reference_id,
            config=config,
        )
        response = self._client.request(
            "POST", "/transcriptions", json=payload.model_dump(exclude_none=True)
        )
        return parse_response(response, Transcription)

    def get(self, transcription_id: str) -> Transcription:
        """
        Retrieve a transcription by ID.

        Performs a GET request to ``/transcriptions/{transcription_id}``.

        Raises:
            SonioxAPIError: When the API returns an error.
        """
        response = self._client.request("GET", f"/transcriptions/{transcription_id}")
        return parse_response(response, Transcription)

    def get_or_none(self, transcription_id: str) -> Transcription | None:
        """
        Retrieve a transcription by ID.

        Returns ``None`` if the transcription does not exist.

        Raises:
            SonioxAPIError: When the API returns an error.
        """
        try:
            return self.get(transcription_id)
        except SonioxNotFoundError:
            return None

    def delete(self, transcription_id: str) -> None:
        """
        Delete a transcription by ID.

        Performs a DELETE request to ``/transcriptions/{transcription_id}``.

        Raises:
            SonioxAPIError: When the API returns an error.
        """
        response = self._client.request("DELETE", f"/transcriptions/{transcription_id}")
        ensure_success(response)

    def delete_if_exists(self, transcription_id: str) -> None:
        """
        Delete a transcription by ID if it exists.

        Ignores missing transcriptions.

        Raises:
            SonioxAPIError: When the API returns an error.
        """
        try:
            self.delete(transcription_id)
        except SonioxNotFoundError:
            return

    def destroy(self, transcription_id: str) -> None:
        """
        Delete a transcription and its associated uploaded file.

        Raises:
            SonioxAPIError: When the API returns an error.
        """
        transcription = self.get(transcription_id)
        self.delete(transcription_id)
        if transcription.file_id:
            self._client.files.delete_if_exists(transcription.file_id)

    def destroy_all(self, limit: int = 100) -> None:
        """
        Delete all transcriptions and their associated files. Stops and raises on the first failed deletion.

        Raises:
            SonioxAPIError: When the API returns an error during listing.
        """
        for transcription in self.list_all(limit=limit):
            self.delete_if_exists(transcription.id)
            if transcription.file_id:
                self._client.files.delete_if_exists(transcription.file_id)

    def get_transcript(self, transcription_id: str) -> TranscriptionTranscript:
        """
        Retrieve the transcript for a transcription.

        Performs a GET request to ``/transcriptions/{transcription_id}/transcript``.

        Raises:
            SonioxAPIError: When the API returns an error.
        """
        response = self._client.request("GET", f"/transcriptions/{transcription_id}/transcript")
        return parse_response(response, TranscriptionTranscript)

    def wait(
        self,
        transcription_id: str,
        *,
        interval_sec: float = 5.0,
        timeout_sec: float | None = None,
    ) -> Transcription:
        """
        Poll a transcription until it leaves the queued or processing state.

        Raises:
            SonioxAPIError: When the API returns an error.
            TimeoutError: Waiting for the transcription to finish exceeded `timeout_sec`.
        """
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
        model: str = DEFAULT_MODEL,
        audio_url: str,
        client_reference_id: str | None = None,
        config: CreateTranscriptionConfig | None = None,
    ) -> Transcription:
        """
        Create a transcription from an audio URL.

        Raises:
            SonioxAPIError: When the API returns an error.
        """
        return self.create(
            model=model,
            audio_url=audio_url,
            client_reference_id=client_reference_id,
            config=config,
        )

    def transcribe_from_file_id(
        self,
        *,
        model: str = DEFAULT_MODEL,
        file_id: str,
        client_reference_id: str | None = None,
        config: CreateTranscriptionConfig | None = None,
    ) -> Transcription:
        """
        Create a transcription from an existing uploaded file.

        Raises:
            SonioxAPIError: When the API returns an error.
        """
        return self.create(
            model=model,
            file_id=file_id,
            client_reference_id=client_reference_id,
            config=config,
        )

    def transcribe_from_file(
        self,
        *,
        model: str = DEFAULT_MODEL,
        file: BinaryIO | bytes | Path | str,
        filename: str | None = None,
        client_reference_id: str | None = None,
        config: CreateTranscriptionConfig | None = None,
    ) -> Transcription:
        """
        Upload a file and create a transcription from it.

        Raises:
            SonioxAPIError: When the API returns an error.
        """
        uploaded = self._client.files.upload(
            file,
            filename=filename,
            client_reference_id=client_reference_id,
        )
        return self.transcribe_from_file_id(
            model=model,
            file_id=uploaded.id,
            client_reference_id=client_reference_id,
            config=config,
        )

    def transcribe(
        self,
        *,
        model: str = DEFAULT_MODEL,
        audio_url: str | None = None,
        file_id: str | None = None,
        file: BinaryIO | bytes | Path | str | None = None,
        filename: str | None = None,
        client_reference_id: str | None = None,
        config: CreateTranscriptionConfig | None = None,
    ) -> Transcription:
        """
        Create a transcription from a file, file ID, or audio URL.

        Validates mutually exclusive inputs before submission.

        Raises:
            SonioxAPIError: When the API returns an error.
            SonioxValidationError: When the payload fails validation.
        """
        if file is not None:
            if audio_url or file_id:
                raise SonioxValidationError("file cannot be combined with audio_url or file_id")
            return self.transcribe_from_file(
                model=model,
                file=file,
                filename=filename,
                client_reference_id=client_reference_id,
                config=config,
            )
        if file_id is not None:
            if audio_url:
                raise SonioxValidationError("file_id cannot be combined with audio_url")
            return self.transcribe_from_file_id(
                model=model,
                file_id=file_id,
                client_reference_id=client_reference_id,
                config=config,
            )
        if not audio_url:
            raise SonioxValidationError("Either audio_url, file_id, or file must be provided")
        return self.transcribe_from_url(
            model=model,
            audio_url=audio_url,
            client_reference_id=client_reference_id,
            config=config,
        )

    def transcribe_file_with_webhook(
        self,
        *,
        model: str = DEFAULT_MODEL,
        file: BinaryIO | bytes | Path | str,
        webhook_url: str,
        filename: str | None = None,
        client_reference_id: str | None = None,
        webhook_auth: WebhookAuthConfig | None = None,
        config: CreateTranscriptionConfig | None = None,
    ) -> Transcription:
        """
        Upload a file, configure a webhook, and start transcription.

        Raises:
            SonioxAPIError: When the API returns an error.
        """
        webhook_fields = self._client.webhooks.webhook_payload(webhook_url, auth=webhook_auth)
        uploaded = self._client.files.upload(
            file,
            filename=filename,
            client_reference_id=client_reference_id,
        )
        config_data = config.model_dump(exclude_none=True) if config else {}
        config_data.update(webhook_fields)
        webhook_config = (
            CreateTranscriptionConfig.model_validate(config_data) if config_data else None
        )
        return self.create(
            model=model,
            file_id=uploaded.id,
            client_reference_id=client_reference_id,
            config=webhook_config,
        )

    def transcribe_and_wait(
        self,
        *,
        model: str = DEFAULT_MODEL,
        audio_url: str | None = None,
        file_id: str | None = None,
        file: BinaryIO | bytes | Path | str | None = None,
        filename: str | None = None,
        client_reference_id: str | None = None,
        delete_after: bool = False,
        wait_interval_sec: float = 5.0,
        wait_timeout_sec: float | None = None,
        config: CreateTranscriptionConfig | None = None,
    ) -> Transcription:
        """
        Create a transcription and wait for completion.

        Returns a Transcription object after it is completed. Optionally deletes
        the transcription and the uploaded file after completion.

        Raises:
            SonioxAPIError: When the API returns an error.
            SonioxValidationError: When the payload fails validation.
            TimeoutError: Waiting for the transcription to finish exceeded `timeout_sec`.
        """
        transcription = self.transcribe(
            model=model,
            audio_url=audio_url,
            file_id=file_id,
            file=file,
            filename=filename,
            client_reference_id=client_reference_id,
            config=config,
        )
        transcription = self.wait(
            transcription.id,
            interval_sec=wait_interval_sec,
            timeout_sec=wait_timeout_sec,
        )

        if delete_after:
            file_id_to_delete = transcription.file_id
            self.delete(transcription.id)
            if file_id_to_delete:
                self._client.files.delete(file_id_to_delete)

        return transcription

    def transcribe_and_wait_with_tokens(
        self,
        *,
        model: str = DEFAULT_MODEL,
        audio_url: str | None = None,
        file_id: str | None = None,
        file: BinaryIO | bytes | Path | str | None = None,
        filename: str | None = None,
        client_reference_id: str | None = None,
        delete_after: bool = False,
        wait_interval_sec: float = 5.0,
        wait_timeout_sec: float | None = None,
        config: CreateTranscriptionConfig | None = None,
    ) -> TranscriptionTranscript:
        """
        Create a transcription, wait for completion, and return the transcript.

        Optionally deletes the transcription and uploaded file after completion.

        Raises:
            SonioxAPIError: When the API returns an error.
            SonioxValidationError: When the payload fails validation.
            TimeoutError: Waiting for the transcription to finish exceeded `timeout_sec`.
        """
        transcription = self.transcribe_and_wait(
            model=model,
            audio_url=audio_url,
            file_id=file_id,
            file=file,
            filename=filename,
            client_reference_id=client_reference_id,
            delete_after=False,  # handle deletion manually after fetching transcript
            wait_interval_sec=wait_interval_sec,
            wait_timeout_sec=wait_timeout_sec,
            config=config,
        )

        result = self.get_transcript(transcription.id)

        if delete_after:
            file_id_to_delete = transcription.file_id
            self.delete(transcription.id)
            if file_id_to_delete:
                self._client.files.delete(file_id_to_delete)

        return result
