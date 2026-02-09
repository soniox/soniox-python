---
title: soniox.api.async_models
description: Description for async_models
keywords: annotations, TYPE_CHECKING, GetModelsResponse, parse_async_response, AsyncSonioxClient, AsyncModelsAPI
---


---

## Class `AsyncModelsAPI`

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