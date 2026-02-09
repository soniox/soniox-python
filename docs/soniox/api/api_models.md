---
title: soniox.api.models
description: Description for models
keywords: annotations, TYPE_CHECKING, GetModelsResponse, parse_response, SonioxClient, ModelsAPI
---


---

## Class `ModelsAPI`

### Attributes

- **_client**: 

### `__init__`

#### Signature

```python
__init__(client: SonioxClient) -> None
```

#### Parameters

- **self** (None): 

- **client** (SonioxClient): 

#### Returns

None

### `list`

List available models.

Performs a GET request to ``/models``.

Raises:
    SonioxAPIError: When the API returns an error.

#### Signature

```python
list() -> GetModelsResponse
```

#### Parameters

- **self** (None): 

#### Returns

GetModelsResponse