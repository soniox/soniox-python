---
title: "soniox.api.async_models"
description: "Soniox Python SDK — soniox.api.async_models Reference"
keywords: "AsyncModelsAPI"
---

---

## AsyncModelsAPI

<a id="asyncmodelsapi-constructor"></a>

### Constructor

```python
AsyncModelsAPI(client: AsyncSonioxClient)
```

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `client` | `AsyncSonioxClient` |

**Returns**

`None`

<a id="asyncmodelsapi-list"></a>

### list()

```python
list() -> GetModelsResponse
```

List available models.

Performs a GET request to ``/models``.

**Returns**

`GetModelsResponse`

**Raises**

- `SonioxAPIError` When the API returns an error.