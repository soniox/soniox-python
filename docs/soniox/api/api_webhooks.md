---
title: "soniox.api.webhooks"
description: "Soniox Python SDK — soniox.api.webhooks Reference"
keywords: "SonioxWebhooksAPI"
---

---

## SonioxWebhooksAPI

<a id="sonioxwebhooksapi-constructor"></a>

### Constructor

```python
SonioxWebhooksAPI(*, webhook_secret: str | None = None, webhook_header: str | None = None)
```

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `webhook_secret` | `str \| None` |
| `webhook_header` | `str \| None` |

**Returns**

`None`

<a id="sonioxwebhooksapi-verify_signature"></a>

### verify_signature()

```python
verify_signature(headers: Headers, *, auth: WebhookAuthConfig | None = None) -> None
```

Verify a webhook signature from headers.

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `headers` | `Headers` |
| `auth` | `WebhookAuthConfig \| None` |

**Returns**

`None`

**Raises**

- `InvalidWebhookSignatureError` When the webhook signature cannot be validated.

***

<a id="sonioxwebhooksapi-unwrap"></a>

### unwrap()

```python
unwrap(payload: str | bytes, headers: Headers, *, auth: WebhookAuthConfig | None = None) -> WebhookEvent
```

Validate and parse a webhook payload.

Returns a WebhookEvent.

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `payload` | `str \| bytes` |
| `headers` | `Headers` |
| `auth` | `WebhookAuthConfig \| None` |

**Returns**

`WebhookEvent`

**Raises**

- `InvalidWebhookSignatureError` When the webhook signature cannot be validated.

***

<a id="sonioxwebhooksapi-webhook_payload"></a>

### webhook_payload()

```python
webhook_payload(webhook_url: str, *, auth: WebhookAuthConfig | None = None) -> dict[str, str]
```

Return fields for webhook configuration when creating a transcription.

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `webhook_url` | `str` |
| `auth` | `WebhookAuthConfig \| None` |

**Returns**

`dict[str, str]`