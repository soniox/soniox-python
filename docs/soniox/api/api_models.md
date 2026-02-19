---
title: "soniox.api.models"
description: "Soniox Python SDK — soniox.api.models Reference"
keywords: "ModelsAPI"
---

---

## ModelsAPI

<a id="modelsapi-constructor"></a>

### Constructor

```python
ModelsAPI(client: SonioxClient)
```

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `client` | `SonioxClient` |

**Returns**

`None`

<a id="modelsapi-list"></a>

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