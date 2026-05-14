"""
Pytest fixtures for the Soniox SDK test suite.

This file only holds fixtures - pytest magic-loads it by filename. For
constants and plain helpers, see :mod:`tests.helpers`.
"""

from __future__ import annotations

import pytest

from soniox.client import AsyncSonioxClient, SonioxClient

from .helpers import API_KEY


@pytest.fixture
def client():
    with SonioxClient(api_key=API_KEY) as c:
        yield c


@pytest.fixture
async def async_client():
    async with AsyncSonioxClient(api_key=API_KEY) as c:
        yield c
