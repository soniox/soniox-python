---
title: "soniox.api.async_auth"
description: "Soniox Python SDK — soniox.api.async_auth Reference"
keywords: "AsyncAuthAPI"
---

---

## AsyncAuthAPI

<a id="asyncauthapi-constructor"></a>

### Constructor

```python
AsyncAuthAPI(client: AsyncSonioxClient)
```

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `client` | `AsyncSonioxClient` |

**Returns**

`None`

<a id="asyncauthapi-create_temporary_api_key"></a>

### create_temporary_api_key()

```python
create_temporary_api_key(*, usage_type: TemporaryApiKeyUsageType = 'transcribe_websocket', expires_in_seconds: int = 5 * 60, client_reference_id: str | None = None) -> CreateTemporaryApiKeyResponse
```

Create a temporary API key.

Performs a POST request to ``/auth/temporary-api-key``.

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `usage_type` | `TemporaryApiKeyUsageType` |
| `expires_in_seconds` | `int` |
| `client_reference_id` | `str \| None` |

**Returns**

`CreateTemporaryApiKeyResponse`

**Raises**

- `SonioxAPIError` When the API returns an error.