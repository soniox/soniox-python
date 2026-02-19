---
title: "soniox"
description: "Asynchronous Soniox REST client exposing HTTP and realtime helpers."
keywords: "AsyncSonioxClient, SonioxClient"
---

---

## AsyncSonioxClient

Asynchronous Soniox REST client exposing HTTP and realtime helpers.

<a id="asyncsonioxclient-constructor"></a>

### Constructor

```python
AsyncSonioxClient(api_key: str | None = None, api_base_url: str | None = None, websocket_base_url: str | None = None, timeout_sec: float | None = None, webhook_secret: str | None = None, webhook_signature_header: str | None = None, **client_kwargs: Any)
```

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `api_key` | `str \| None` |
| `api_base_url` | `str \| None` |
| `websocket_base_url` | `str \| None` |
| `timeout_sec` | `float \| None` |
| `webhook_secret` | `str \| None` |
| `webhook_signature_header` | `str \| None` |
| `client_kwargs` | `Any` |

**Returns**

`None`

<a id="asyncsonioxclient-properties"></a>

### Properties

| Property | Type |
| ------ | ------ |
| `files` | `AsyncFilesAPI` |
| `stt` | `AsyncSttAPI` |
| `models` | `AsyncModelsAPI` |
| `auth` | `AsyncAuthAPI` |
| `webhooks` | `AsyncSonioxWebhooksAPI` |
| `realtime` | `AsyncRealtimeAPI` |

<a id="asyncsonioxclient-request"></a>

### request()

```python
request(method: str, path: str, *, params: Mapping[str, Any] | None = None, json: Any | None = None, data: Mapping[str, Any] | None = None, files: Mapping[str, Any] | None = None) -> httpx.Response
```

Perform a request against the configured Soniox REST endpoint.

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `method` | `str` |
| `path` | `str` |
| `params` | `Mapping[str, Any] \| None` |
| `json` | `Any \| None` |
| `data` | `Mapping[str, Any] \| None` |
| `files` | `Mapping[str, Any] \| None` |

**Returns**

`httpx.Response`

***

<a id="asyncsonioxclient-aclose"></a>

### aclose()

```python
aclose() -> None
```

Close any outstanding async HTTP connections.

**Returns**

`None`

---

## SonioxClient

Synchronous Soniox REST client exposing API namespaces via httpx.

<a id="sonioxclient-constructor"></a>

### Constructor

```python
SonioxClient(*, api_key: str | None = None, api_base_url: str | None = None, websocket_base_url: str | None = None, timeout_sec: float | None = None, webhook_secret: str | None = None, webhook_signature_header: str | None = None, **client_kwargs: Any)
```

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `api_key` | `str \| None` |
| `api_base_url` | `str \| None` |
| `websocket_base_url` | `str \| None` |
| `timeout_sec` | `float \| None` |
| `webhook_secret` | `str \| None` |
| `webhook_signature_header` | `str \| None` |
| `client_kwargs` | `Any` |

**Returns**

`None`

<a id="sonioxclient-properties"></a>

### Properties

| Property | Type |
| ------ | ------ |
| `files` | `FilesAPI` |
| `stt` | `SttAPI` |
| `models` | `ModelsAPI` |
| `auth` | `AuthAPI` |
| `webhooks` | `SonioxWebhooksAPI` |
| `realtime` | `RealtimeAPI` |

<a id="sonioxclient-request"></a>

### request()

```python
request(method: str, path: str, *, params: Mapping[str, Any] | None = None, json: Any | None = None, data: Mapping[str, Any] | None = None, files: Mapping[str, Any] | None = None) -> httpx.Response
```

Perform a request against the configured Soniox REST endpoint.

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `method` | `str` |
| `path` | `str` |
| `params` | `Mapping[str, Any] \| None` |
| `json` | `Any \| None` |
| `data` | `Mapping[str, Any] \| None` |
| `files` | `Mapping[str, Any] \| None` |

**Returns**

`httpx.Response`

***

<a id="sonioxclient-close"></a>

### close()

```python
close() -> None
```

Close the underlying HTTP transport.

**Returns**

`None`