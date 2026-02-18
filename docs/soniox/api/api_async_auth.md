---
title: soniox.api.async_auth
description: Description for async_auth
keywords: annotations, TYPE_CHECKING, CreateTemporaryApiKeyPayload, CreateTemporaryApiKeyResponse, TemporaryApiKeyUsageType, parse_async_response, AsyncSonioxClient, AsyncAuthAPI
---


---

## Class `AsyncAuthAPI`

### Attributes

- **_client**: 

### `__init__`

#### Signature

```python
__init__(client: AsyncSonioxClient) -> None
```

#### Parameters

- **self** (None): 

- **client** (AsyncSonioxClient): 

#### Returns

None

### `create_temporary_api_key`

Create a temporary API key.

Performs a POST request to ``/auth/temporary-api-key``.

Raises:
    SonioxAPIError: When the API returns an error.

#### Signature

```python
create_temporary_api_key(*, usage_type: TemporaryApiKeyUsageType = 'transcribe_websocket', expires_in_seconds: int = 5 * 60, client_reference_id: str | None = None) -> CreateTemporaryApiKeyResponse
```

#### Parameters

- **self** (None): 

- **usage_type** (TemporaryApiKeyUsageType): 

- **expires_in_seconds** (int): 

- **client_reference_id** (str | None): 

#### Returns

CreateTemporaryApiKeyResponse