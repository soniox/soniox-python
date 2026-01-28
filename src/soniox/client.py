from __future__ import annotations

from collections.abc import Mapping
from functools import cached_property
from typing import TYPE_CHECKING, Any

import httpx

if TYPE_CHECKING:
    from .api.async_auth import AsyncAuthAPI
    from .api.async_files import AsyncFilesAPI
    from .api.async_models import AsyncModelsAPI
    from .api.async_transcriptions import AsyncTranscriptionsAPI
    from .api.async_webhooks import AsyncSonioxWebhooksAPI
    from .api.auth import AuthAPI
    from .api.files import FilesAPI
    from .api.models import ModelsAPI
    from .api.transcriptions import TranscriptionsAPI
    from .api.webhooks import SonioxWebhooksAPI
    from .realtime import AsyncRealtimeAPI, RealtimeAPI


class _BaseSonioxClient:
    def __init__(
        self,
        api_key: str,
        api_base_url: str,
        websocket_base_url: str,
        timeout_sec: float,
        webhook_secret: str | None = None,
        webhook_signature_header: str | None = None,
    ) -> None:
        self.api_key = api_key
        self.api_base_url = api_base_url
        self.websocket_base_url = websocket_base_url
        self.timeout_sec = timeout_sec
        self.webhook_secret = webhook_secret
        self.webhook_signature_header = webhook_signature_header

    def _default_headers(self) -> Mapping[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }


class SonioxClient(_BaseSonioxClient):
    def __init__(
        self,
        api_key: str,
        api_base_url: str = "https://api.soniox.com/v1",
        websocket_base_url: str = "wss://stt-rt.soniox.com/transcribe-websocket",
        timeout_sec: float = 30.0,
        webhook_secret: str | None = None,
        webhook_signature_header: str | None = None,
        **client_kwargs: Any,
    ) -> None:
        super().__init__(
            api_key,
            api_base_url,
            websocket_base_url,
            timeout_sec,
            webhook_secret=webhook_secret,
            webhook_signature_header=webhook_signature_header,
        )
        self._http_client = httpx.Client(
            base_url=self.api_base_url,
            headers=self._default_headers(),
            timeout=self.timeout_sec,
            **client_kwargs,
        )

    def request(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        json: Any | None = None,
        data: Mapping[str, Any] | None = None,
        files: Mapping[str, Any] | None = None,
        timeout_sec: float = 30.0,
    ) -> httpx.Response:
        return self._http_client.request(
            method,
            path,
            params=params,
            json=json,
            data=data,
            files=files,
            timeout=timeout_sec,
        )

    @cached_property
    def files(self) -> FilesAPI:
        from .api.files import FilesAPI

        return FilesAPI(self)

    @cached_property
    def transcriptions(self) -> TranscriptionsAPI:
        from .api.transcriptions import TranscriptionsAPI

        return TranscriptionsAPI(self)

    @cached_property
    def models(self) -> ModelsAPI:
        from .api.models import ModelsAPI

        return ModelsAPI(self)

    @cached_property
    def auth(self) -> AuthAPI:
        from .api.auth import AuthAPI

        return AuthAPI(self)

    @cached_property
    def webhooks(self) -> SonioxWebhooksAPI:
        from .api.webhooks import SonioxWebhooksAPI

        return SonioxWebhooksAPI(
            webhook_secret=self.webhook_secret,
            webhook_header=self.webhook_signature_header,
        )

    @cached_property
    def realtime(self) -> RealtimeAPI:
        from .realtime import RealtimeAPI

        return RealtimeAPI(self)


class AsyncSonioxClient(_BaseSonioxClient):
    def __init__(
        self,
        api_key: str,
        api_base_url: str = "https://api.soniox.com/v1",
        websocket_base_url: str = "wss://stt-rt.soniox.com/transcribe-websocket",
        timeout_sec: float = 30.0,
        webhook_secret: str | None = None,
        webhook_signature_header: str | None = None,
        **client_kwargs: Any,
    ) -> None:
        super().__init__(
            api_key,
            api_base_url,
            websocket_base_url,
            timeout_sec,
            webhook_secret=webhook_secret,
            webhook_signature_header=webhook_signature_header,
        )
        self._http_client = httpx.AsyncClient(
            base_url=self.api_base_url,
            headers=self._default_headers(),
            timeout=self.timeout_sec,
            **client_kwargs,
        )

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        json: Any | None = None,
        data: Mapping[str, Any] | None = None,
        files: Mapping[str, Any] | None = None,
        timeout: float | httpx.Timeout | None = None,
    ) -> httpx.Response:
        return await self._http_client.request(
            method,
            path,
            params=params,
            json=json,
            data=data,
            files=files,
            timeout=timeout,
        )

    @cached_property
    def files(self) -> AsyncFilesAPI:
        from .api.async_files import AsyncFilesAPI

        return AsyncFilesAPI(self)

    @cached_property
    def transcriptions(self) -> AsyncTranscriptionsAPI:
        from .api.async_transcriptions import AsyncTranscriptionsAPI

        return AsyncTranscriptionsAPI(self)

    @cached_property
    def models(self) -> AsyncModelsAPI:
        from .api.async_models import AsyncModelsAPI

        return AsyncModelsAPI(self)

    @cached_property
    def auth(self) -> AsyncAuthAPI:
        from .api.async_auth import AsyncAuthAPI

        return AsyncAuthAPI(self)

    @cached_property
    def webhooks(self) -> AsyncSonioxWebhooksAPI:
        from .api.async_webhooks import AsyncSonioxWebhooksAPI

        return AsyncSonioxWebhooksAPI(
            webhook_secret=self.webhook_secret,
            webhook_header=self.webhook_signature_header,
        )

    @cached_property
    def realtime(self) -> AsyncRealtimeAPI:
        from .realtime import AsyncRealtimeAPI

        return AsyncRealtimeAPI(self)
