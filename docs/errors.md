---
title: "Errors"
description: "Soniox Python SDK - Errors Reference"
keywords: "SonioxError, SonioxAPIError, SonioxInvalidRequestError, SonioxAuthenticationError, SonioxPermissionDeniedError, SonioxNotFoundError, SonioxConflictError, SonioxRateLimitError, SonioxServerError, SonioxValidationError, SonioxRealtimeError, InvalidWebhookSignatureError"
---

---

Import errors from `soniox.errors`. Every exception subclasses `SonioxError`, and HTTP API failures subclass `SonioxAPIError`, which carries `status_code`, `request_id` and the parsed `api_error` (including its `error_type`).

---

## SonioxError

Subclass of `Exception`.

Base exception for the SDK.

<a id="sonioxerror-constructor"></a>

### Constructor

```python
SonioxError(message: str, *, response: httpx.Response | None = None)
```

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `message` | `str` | Description of what went wrong. |
| `response` | `httpx.Response \| None` | HTTP response that caused the error, if any. |

**Returns**

`None`

<a id="sonioxerror-properties"></a>

### Properties

| Property | Type | Description |
| ------ | ------ | ------ |
| `response` | `httpx.Response \| None` | HTTP response that caused the error, if any. |

---

## SonioxAPIError

Subclass of `SonioxError`.

Raised when the Soniox API replies with a non-2xx payload.

<a id="sonioxapierror-constructor"></a>

### Constructor

```python
SonioxAPIError(message: str, *, api_error: ApiError | None = None, response: httpx.Response | None = None)
```

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `message` | `str` | Description of what went wrong. |
| `api_error` | `ApiError \| None` | Parsed error body; its ``error_type`` identifies the error. |
| `response` | `httpx.Response \| None` | HTTP response that caused the error. |

**Returns**

`None`

<a id="sonioxapierror-properties"></a>

### Properties

| Property | Type | Description |
| ------ | ------ | ------ |
| `api_error` | `ApiError \| None` | Structured representation of a non-2xx API response payload. |
| `status_code` | `int \| None` | HTTP status code. |
| `request_id` | `str \| None` | Unique identifier for the request, useful for troubleshooting. |

<a id="sonioxapierror-from_response"></a>

### from_response()

```python
from_response(response: httpx.Response) -> SonioxAPIError
```

Parse an `httpx.Response` into the matching SDK error.

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `response` | `httpx.Response` | Non-2xx HTTP response from the Soniox API. |

**Returns**

`SonioxAPIError`

---

## SonioxInvalidRequestError

Subclass of `SonioxAPIError`.

Invalid request payloads (`400`).

---

## SonioxAuthenticationError

Subclass of `SonioxAPIError`.

Authentication failures (`401`/`403`).

---

## SonioxPermissionDeniedError

Subclass of `SonioxAPIError`.

The API key is valid but lacks the permission for this call (`403` with
``error_type`` ``permission_denied``). Other `403` errors, such as an expired
temporary API key session, raise `SonioxAuthenticationError`. REST calls only;
over WebSocket a permission error arrives as a realtime error event.

See [API key permissions](https://soniox.com/docs/guides/api-key-permissions).

---

## SonioxNotFoundError

Subclass of `SonioxAPIError`.

Resource not found (`404`).

---

## SonioxConflictError

Subclass of `SonioxAPIError`.

Conflict or invalid state, e.g. deleting while processing (`409`).

---

## SonioxRateLimitError

Subclass of `SonioxAPIError`.

Rate limit or usage limit exceeded (`429`).

---

## SonioxServerError

Subclass of `SonioxAPIError`.

Server errors (`5xx`).

---

## SonioxValidationError

Subclass of `SonioxError`.

Raised when Pydantic input validation fails on the client side.

<a id="sonioxvalidationerror-constructor"></a>

### Constructor

```python
SonioxValidationError(message: str, *, errors: ValidationError | None = None)
```

**Parameters**

| Parameter | Type | Description |
| ------ | ------ | ------ |
| `message` | `str` | Description of what went wrong. |
| `errors` | `ValidationError \| None` | The underlying Pydantic validation error, if any. |

**Returns**

`None`

<a id="sonioxvalidationerror-properties"></a>

### Properties

| Property | Type | Description |
| ------ | ------ | ------ |
| `errors` | `ValidationError \| None` | The underlying Pydantic validation error, if any. |

---

## SonioxRealtimeError

Subclass of `SonioxError`.

Errors raised by realtime workflows.

---

## InvalidWebhookSignatureError

Subclass of `SonioxError`.

Raised when a webhook signature cannot be validated.