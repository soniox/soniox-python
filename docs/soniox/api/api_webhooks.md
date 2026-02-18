---
title: soniox.api.webhooks
description: Description for webhooks
keywords: annotations, json, os, InvalidWebhookSignatureError, Headers, WebhookAuthConfig, WebhookEvent, SONIOX_API_WEBHOOK_HEADER_ENV, SONIOX_API_WEBHOOK_SECRET_ENV, DEFAULT_WEBHOOK_HEADER, _get_header_value, _resolve_webhook_auth, SonioxWebhooksAPI
---


---

### `_get_header_value`

#### Signature

```python
_get_header_value(headers: Headers, name: str) -> str | None
```

#### Parameters

- **headers** (Headers): 

- **name** (str): 

#### Returns

str | None

---

### `_resolve_webhook_auth`

#### Signature

```python
_resolve_webhook_auth(header: str | None, secret: str | None) -> WebhookAuthConfig | None
```

#### Parameters

- **header** (str | None): 

- **secret** (str | None): 

#### Returns

WebhookAuthConfig | None

---

## Class `SonioxWebhooksAPI`

### Attributes

- **_webhook_secret**: 

- **_webhook_header**: 

### `__init__`

#### Signature

```python
__init__(*, webhook_secret: str | None = None, webhook_header: str | None = None) -> None
```

#### Parameters

- **self** (None): 

- **webhook_secret** (str | None): 

- **webhook_header** (str | None): 

#### Returns

None

### `verify_signature`

Verify a webhook signature from headers.

Raises:
    InvalidWebhookSignatureError: When the webhook signature cannot be validated.

#### Signature

```python
verify_signature(headers: Headers, *, auth: WebhookAuthConfig | None = None) -> None
```

#### Parameters

- **self** (None): 

- **headers** (Headers): 

- **auth** (WebhookAuthConfig | None): 

#### Returns

None

### `unwrap`

Validate and parse a webhook payload.

Returns a WebhookEvent.

Raises:
    InvalidWebhookSignatureError: When the webhook signature cannot be validated.

#### Signature

```python
unwrap(payload: str | bytes, headers: Headers, *, auth: WebhookAuthConfig | None = None) -> WebhookEvent
```

#### Parameters

- **self** (None): 

- **payload** (str | bytes): 

- **headers** (Headers): 

- **auth** (WebhookAuthConfig | None): 

#### Returns

WebhookEvent

### `webhook_payload`

Return fields for webhook configuration when creating a transcription.

#### Signature

```python
webhook_payload(webhook_url: str, *, auth: WebhookAuthConfig | None = None) -> dict[str, str]
```

#### Parameters

- **self** (None): 

- **webhook_url** (str): 

- **auth** (WebhookAuthConfig | None): 

#### Returns

dict[str, str]