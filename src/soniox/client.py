from __future__ import annotations

import os
from collections.abc import Mapping
from functools import cached_property
from types import TracebackType
from typing import TYPE_CHECKING, Any

import httpx

from soniox.errors import SonioxValidationError

if TYPE_CHECKING:
    from .api.async_auth import AsyncAuthAPI
    from .api.async_files import AsyncFilesAPI
    from .api.async_models import AsyncModelsAPI
    from .api.async_stt import AsyncSttAPI
    from .api.async_webhooks import AsyncSonioxWebhooksAPI
    from .api.auth import AuthAPI
    from .api.files import FilesAPI
    from .api.models import ModelsAPI
    from .api.stt import SttAPI
    from .api.webhooks import SonioxWebhooksAPI
    from .realtime import AsyncRealtimeAPI, RealtimeAPI

_DEFAULT_API_BASE_URL = "https://api.soniox.com/v1"
_DEFAULT_WEBSOCKET_BASE_URL = "wss://stt-rt.soniox.com/transcribe-websocket"
_DEFAULT_TIMEOUT_SEC = 30.0


class _BaseSonioxClient:
    """Shared configuration holder for sync and async Soniox clients."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        api_base_url: str | None = None,
        websocket_base_url: str | None = None,
        timeout_sec: float | None = None,
        webhook_secret: str | None = None,
        webhook_signature_header: str | None = None,
    ) -> None:
        api_key = api_key or os.environ.get("SONIOX_API_KEY")
        if not api_key:
            raise SonioxValidationError("Please provide api_key")
        self.api_key = api_key
        self.api_base_url = api_base_url or _DEFAULT_API_BASE_URL
        self.websocket_base_url = websocket_base_url or _DEFAULT_WEBSOCKET_BASE_URL
        self.timeout_sec = timeout_sec if timeout_sec is not None else _DEFAULT_TIMEOUT_SEC
        self.webhook_secret = webhook_secret
        self.webhook_signature_header = webhook_signature_header

    def _default_headers(self) -> Mapping[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
        }


class SonioxClient(_BaseSonioxClient):
    """Synchronous Soniox REST client exposing API namespaces via httpx."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        api_base_url: str | None = None,
        websocket_base_url: str | None = None,
        timeout_sec: float | None = None,
        webhook_secret: str | None = None,
        webhook_signature_header: str | None = None,
        **client_kwargs: Any,
    ) -> None:
        super().__init__(
            api_key=api_key,
            api_base_url=api_base_url,
            websocket_base_url=websocket_base_url,
            timeout_sec=timeout_sec,
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
    ) -> httpx.Response:
        """Perform a request against the configured Soniox REST endpoint."""
        return self._http_client.request(
            method,
            path,
            params=params,
            json=json,
            data=data,
            files=files,
        )

    @cached_property
    def files(self) -> FilesAPI:
        from .api.files import FilesAPI

        return FilesAPI(self)

    @cached_property
    def stt(self) -> SttAPI:
        from .api.stt import SttAPI

        return SttAPI(self)

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

    def close(self) -> None:
        """Close the underlying HTTP transport."""
        self._http_client.close()

    def __enter__(self) -> SonioxClient:
        return self

    def __exit__(
        self,
        _exc_type: type[BaseException] | None,
        _exc_value: BaseException | None,
        _traceback: TracebackType | None,
    ) -> None:
        _ = (_exc_type, _exc_value, _traceback)  # To make linter happy.
        self.close()


class AsyncSonioxClient(_BaseSonioxClient):
    """Asynchronous Soniox REST client exposing HTTP and realtime helpers."""

    def __init__(
        self,
        api_key: str | None = None,
        api_base_url: str | None = None,
        websocket_base_url: str | None = None,
        timeout_sec: float | None = None,
        webhook_secret: str | None = None,
        webhook_signature_header: str | None = None,
        **client_kwargs: Any,
    ) -> None:
        super().__init__(
            api_key=api_key,
            api_base_url=api_base_url,
            websocket_base_url=websocket_base_url,
            timeout_sec=timeout_sec,
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
    ) -> httpx.Response:
        """Perform a request against the configured Soniox REST endpoint."""
        return await self._http_client.request(
            method,
            path,
            params=params,
            json=json,
            data=data,
            files=files,
        )

    @cached_property
    def files(self) -> AsyncFilesAPI:
        from .api.async_files import AsyncFilesAPI

        return AsyncFilesAPI(self)

    @cached_property
    def stt(self) -> AsyncSttAPI:
        from .api.async_stt import AsyncSttAPI

        return AsyncSttAPI(self)

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

    async def aclose(self) -> None:
        """Close any outstanding async HTTP connections."""
        await self._http_client.aclose()

    async def __aenter__(self) -> AsyncSonioxClient:
        return self

    async def __aexit__(
        self,
        _exc_type: type[BaseException] | None,
        _exc_value: BaseException | None,
        _traceback: TracebackType | None,
    ) -> None:
        _ = (_exc_type, _exc_value, _traceback)  # To make linter happy.
        await self.aclose()
