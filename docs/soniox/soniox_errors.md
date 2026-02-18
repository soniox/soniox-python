---
title: soniox.errors
description: Description for errors
keywords: annotations, httpx, ValidationError, ApiError, SonioxError, SonioxValidationError, SonioxAPIError, SonioxAuthenticationError, SonioxInvalidRequestError, SonioxNotFoundError, SonioxConflictError, SonioxRateLimitError, SonioxServerError, InvalidWebhookSignatureError, SonioxRealtimeError
---


---

## Class `SonioxError`

Base exception for the SDK.

### Attributes

- **response**: 

### `__init__`

#### Signature

```python
__init__(message: str, *, response: httpx.Response | None = None) -> None
```

#### Parameters

- **self** (None): 

- **message** (str): 

- **response** (httpx.Response | None): 

#### Returns

None

---

## Class `SonioxValidationError`

Raised when Pydantic input validation fails on the client side.

### Attributes

- **errors**: 

### `__init__`

#### Signature

```python
__init__(message: str, *, errors: ValidationError | None = None) -> None
```

#### Parameters

- **self** (None): 

- **message** (str): 

- **errors** (ValidationError | None): 

#### Returns

None

---

## Class `SonioxAPIError`

Raised when the Soniox API replies with a non-2xx payload.

### Attributes

- **api_error**: 

- **status_code**: 

- **request_id**: 

### `__init__`

#### Signature

```python
__init__(message: str, *, api_error: ApiError | None = None, response: httpx.Response | None = None) -> None
```

#### Parameters

- **self** (None): 

- **message** (str): 

- **api_error** (ApiError | None): 

- **response** (httpx.Response | None): 

#### Returns

None

### `__str__`

#### Signature

```python
__str__() -> str
```

#### Parameters

- **self** (None): 

#### Returns

str

### `from_response`

Parse an `httpx.Response` into a richer SDK error.

#### Signature

```python
from_response(response: httpx.Response) -> SonioxAPIError
```

#### Parameters

- **cls** (None): 

- **response** (httpx.Response): 

#### Returns

SonioxAPIError

### `_map_status_to_exception`

#### Signature

```python
_map_status_to_exception(status_code: int) -> type[SonioxAPIError]
```

#### Parameters

- **cls** (None): 

- **status_code** (int): 

#### Returns

type[SonioxAPIError]

---

## Class `SonioxAuthenticationError`

Authentication failures (`401`/`403`).

---

## Class `SonioxInvalidRequestError`

Invalid request payloads (`400`).

---

## Class `SonioxNotFoundError`

Resource not found.

---

## Class `SonioxConflictError`

Conflict or invalid state (e.g., delete while processing).

---

## Class `SonioxRateLimitError`

Rate limit (429).

---

## Class `SonioxServerError`

5xx responses.

---

## Class `InvalidWebhookSignatureError`

Raised when a webhook signature cannot be validated.

---

## Class `SonioxRealtimeError`

Errors raised by realtime workflows.