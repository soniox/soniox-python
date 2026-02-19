---
title: "soniox.types.webhooks"
description: "Configuration for webhook authentication headers."
keywords: "WebhookAuthConfig, WebhookEvent"
---

---

## WebhookAuthConfig

Configuration for webhook authentication headers.

<a id="webhookauthconfig-properties"></a>

### Properties

| Property | Type |
| ------ | ------ |
| `name` | `str` |
| `value` | `str` |

---

## WebhookEvent

Basic webhook event metadata.

<a id="webhookevent-properties"></a>

### Properties

| Property | Type |
| ------ | ------ |
| `id` | `str` |
| `status` | `Literal['completed', 'error']` |