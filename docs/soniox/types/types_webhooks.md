---
title: soniox.types.webhooks
description: Description for webhooks
keywords: annotations, Mapping, Literal, TypeAlias, BaseModel, Field, WebhookAuthConfig, WebhookEvent, Headers
---


---

## Class `WebhookAuthConfig`

Configuration for webhook authentication headers.

### Attributes

- **name**: Expected header name (case-insensitive comparison).

- **value**: Expected header value (exact match).

---

## Class `WebhookEvent`

Basic webhook event metadata.

### Attributes

- **id**: Transcription ID (UUID).

- **status**: Transcription result status.