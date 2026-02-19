---
title: "soniox.errors"
description: "Base exception for the SDK."
keywords: "InvalidWebhookSignatureError, SonioxAPIError, SonioxAuthenticationError, SonioxConflictError, SonioxError, SonioxInvalidRequestError, SonioxNotFoundError, SonioxRateLimitError, SonioxRealtimeError, SonioxServerError, SonioxValidationError"
---

---

## SonioxError

Base exception for the SDK.

<a id="sonioxerror-constructor"></a>

### Constructor

```python
SonioxError(message: str, *, response: httpx.Response | None = None)
```

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `message` | `str` |
| `response` | `httpx.Response \| None` |

**Returns**

`None`

<a id="sonioxerror-properties"></a>

### Properties

| Property | Type |
| ------ | ------ |
| `response` | `-` |

---

## SonioxValidationError

Raised when Pydantic input validation fails on the client side.

<a id="sonioxvalidationerror-constructor"></a>

### Constructor

```python
SonioxValidationError(message: str, *, errors: ValidationError | None = None)
```

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `message` | `str` |
| `errors` | `ValidationError \| None` |

**Returns**

`None`

<a id="sonioxvalidationerror-properties"></a>

### Properties

| Property | Type |
| ------ | ------ |
| `errors` | `-` |

---

## SonioxAPIError

Raised when the Soniox API replies with a non-2xx payload.

<a id="sonioxapierror-constructor"></a>

### Constructor

```python
SonioxAPIError(message: str, *, api_error: ApiError | None = None, response: httpx.Response | None = None)
```

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `message` | `str` |
| `api_error` | `ApiError \| None` |
| `response` | `httpx.Response \| None` |

**Returns**

`None`

<a id="sonioxapierror-properties"></a>

### Properties

| Property | Type |
| ------ | ------ |
| `api_error` | `ApiError \| None` |
| `status_code` | `int \| None` |
| `request_id` | `str \| None` |

<a id="sonioxapierror-from_response"></a>

### from_response()

```python
from_response(response: httpx.Response) -> SonioxAPIError
```

Parse an `httpx.Response` into a richer SDK error.

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `response` | `httpx.Response` |

**Returns**

`SonioxAPIError`

---

## SonioxAuthenticationError

Authentication failures (`401`/`403`).

---

## SonioxInvalidRequestError

Invalid request payloads (`400`).

---

## SonioxNotFoundError

Resource not found.

---

## SonioxConflictError

Conflict or invalid state (e.g., delete while processing).

---

## SonioxRateLimitError

Rate limit (429).

---

## SonioxServerError

5xx responses.

---

## InvalidWebhookSignatureError

Raised when a webhook signature cannot be validated.

---

## SonioxRealtimeError

Errors raised by realtime workflows.