---
title: "soniox.api.auth"
description: "Soniox Python SDK — soniox.api.auth Reference"
keywords: "AuthAPI"
---

---

## AuthAPI

<a id="authapi-constructor"></a>

### Constructor

```python
AuthAPI(client: SonioxClient)
```

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `client` | `SonioxClient` |

**Returns**

`None`

<a id="authapi-create_temporary_api_key"></a>

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