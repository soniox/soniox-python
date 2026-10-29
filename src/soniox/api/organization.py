from __future__ import annotations

from typing import TYPE_CHECKING

from ..types import (
    ApiKeyPermission,
    CreateProjectApiKeyPayload,
    CreateProjectApiKeyResponse,
    GetOrganizationBalanceResponse,
    GetOrganizationLimitsResponse,
    GetOrganizationMonthlyUsagePayload,
    GetOrganizationMonthlyUsageResponse,
    GetOrganizationProjectsResponse,
    GetOrganizationResponse,
    GetOrganizationUsageSummaryResponse,
    GetProjectApiKeysResponse,
    GetUsageSummaryPayload,
)
from ._utils import ensure_success, parse_response

if TYPE_CHECKING:
    from ..client import SonioxClient


class OrganizationAPI:
    """Organization-wide administration.

    Every call here needs an organization API key, not a project key. It travels in
    the same ``Authorization`` header, so pass it as ``api_key`` on the client.
    """

    def __init__(self, client: SonioxClient) -> None:
        self._client = client

    def get(self) -> GetOrganizationResponse:
        """
        Get the organization the API key belongs to.

        Performs a GET request to ``/organization``.

        Raises:
            SonioxAPIError: When the API returns an error.
        """
        response = self._client.request("GET", "/organization")
        return parse_response(response, GetOrganizationResponse)

    def balance(self) -> GetOrganizationBalanceResponse:
        """
        Get the prepaid balance and payment settings.

        Performs a GET request to ``/organization/balance``.

        Raises:
            SonioxAPIError: When the API returns an error.
        """
        response = self._client.request("GET", "/organization/balance")
        return parse_response(response, GetOrganizationBalanceResponse)

    def limits(self) -> GetOrganizationLimitsResponse:
        """
        Get the monthly budget and the per-region rate and quota limits.

        Performs a GET request to ``/organization/limits``.

        Raises:
            SonioxAPIError: When the API returns an error.
        """
        response = self._client.request("GET", "/organization/limits")
        return parse_response(response, GetOrganizationLimitsResponse)

    def monthly_usage(self, month: str | None = None) -> GetOrganizationMonthlyUsageResponse:
        """
        Get one calendar month of usage, split per project.

        Performs a GET request to ``/organization/usage/monthly``.

        Args:
            month: Calendar month as ``YYYY-MM``, UTC. Defaults to the current month.

        Raises:
            SonioxAPIError: When the API returns an error.
        """
        payload = GetOrganizationMonthlyUsagePayload(month=month)
        params = payload.model_dump(exclude_none=True)
        response = self._client.request("GET", "/organization/usage/monthly", params=params)
        return parse_response(response, GetOrganizationMonthlyUsageResponse)

    def usage_summary(self, start_time: str, end_time: str) -> GetOrganizationUsageSummaryResponse:
        """
        Return daily cost and activity for the organization, per project.

        Performs a GET request to ``/organization/usage/summary``.

        Args:
            start_time: Start of the window (inclusive), ISO 8601 UTC.
            end_time: End of the window (exclusive), ISO 8601 UTC. A UTC day is included
                when the window covers any part of it, so an ``end_time`` at exactly
                midnight leaves out its own day.

        Raises:
            SonioxAPIError: When the API returns an error.
        """
        payload = GetUsageSummaryPayload(start_time=start_time, end_time=end_time)
        response = self._client.request(
            "GET", "/organization/usage/summary", params=payload.model_dump()
        )
        return parse_response(response, GetOrganizationUsageSummaryResponse)

    def projects(self) -> GetOrganizationProjectsResponse:
        """
        List every project in the organization.

        Performs a GET request to ``/organization/projects``.

        Raises:
            SonioxAPIError: When the API returns an error.
        """
        response = self._client.request("GET", "/organization/projects")
        return parse_response(response, GetOrganizationProjectsResponse)

    def list_project_api_keys(self, project_id: str) -> GetProjectApiKeysResponse:
        """
        List a project's API keys, without their secrets.

        Performs a GET request to ``/organization/projects/{project_id}/api-keys``.

        Raises:
            SonioxAPIError: When the API returns an error.
        """
        response = self._client.request("GET", f"/organization/projects/{project_id}/api-keys")
        return parse_response(response, GetProjectApiKeysResponse)

    def create_project_api_key(
        self, project_id: str, *, name: str, permissions: list[ApiKeyPermission]
    ) -> CreateProjectApiKeyResponse:
        """
        Create an API key in a project.

        Performs a POST request to ``/organization/projects/{project_id}/api-keys``.

        The response is the only place the secret appears; it is not retrievable later.

        Args:
            project_id: Project the key belongs to.
            name: Name shown for the key in the console.
            permissions: Permissions the key grants, as ``resource:level``.

        Raises:
            SonioxAPIError: When the API returns an error.
        """
        payload = CreateProjectApiKeyPayload(name=name, permissions=permissions)
        response = self._client.request(
            "POST",
            f"/organization/projects/{project_id}/api-keys",
            json=payload.model_dump(),
        )
        return parse_response(response, CreateProjectApiKeyResponse)

    def delete_project_api_key(self, project_id: str, key_id: str) -> None:
        """
        Delete a project's API key.

        Performs a DELETE request to
        ``/organization/projects/{project_id}/api-keys/{key_id}``.

        Raises:
            SonioxAPIError: When the API returns an error.
        """
        response = self._client.request(
            "DELETE", f"/organization/projects/{project_id}/api-keys/{key_id}"
        )
        ensure_success(response)
