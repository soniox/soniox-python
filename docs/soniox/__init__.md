---
title: soniox
description: Description for soniox
keywords: AsyncSonioxClient, SonioxClient, __all__, errors, utils, client, types, api, realtime
---


---

## Class `AsyncSonioxClient`

Asynchronous Soniox REST client exposing HTTP and realtime helpers.

### Attributes

- **_http_client**: 

- **files**: 

- **transcriptions**: 

- **models**: 

- **auth**: 

- **webhooks**: 

- **realtime**: 

### `__init__`

#### Signature

```python
__init__(api_key: str | None = None, api_base_url: str | None = None, websocket_base_url: str | None = None, timeout_sec: float | None = None, webhook_secret: str | None = None, webhook_signature_header: str | None = None, **client_kwargs: Any) -> None
```

#### Parameters

- **self** (None): 

- **api_key** (str | None): 

- **api_base_url** (str | None): 

- **websocket_base_url** (str | None): 

- **timeout_sec** (float | None): 

- **webhook_secret** (str | None): 

- **webhook_signature_header** (str | None): 

- **client_kwargs** (Any): 

#### Returns

None

### `request`

Perform a request against the configured Soniox REST endpoint.

#### Signature

```python
request(method: str, path: str, *, params: Mapping[str, Any] | None = None, json: Any | None = None, data: Mapping[str, Any] | None = None, files: Mapping[str, Any] | None = None) -> httpx.Response
```

#### Parameters

- **self** (None): 

- **method** (str): 

- **path** (str): 

- **params** (Mapping[str, Any] | None): 

- **json** (Any | None): 

- **data** (Mapping[str, Any] | None): 

- **files** (Mapping[str, Any] | None): 

#### Returns

httpx.Response

### `aclose`

Close any outstanding async HTTP connections.

#### Signature

```python
aclose() -> None
```

#### Parameters

- **self** (None): 

#### Returns

None

### `__aenter__`

#### Signature

```python
__aenter__() -> AsyncSonioxClient
```

#### Parameters

- **self** (None): 

#### Returns

AsyncSonioxClient

### `__aexit__`

#### Signature

```python
__aexit__(_exc_type: type[BaseException] | None, _exc_value: BaseException | None, _traceback: TracebackType | None) -> None
```

#### Parameters

- **self** (None): 

- **_exc_type** (type[BaseException] | None): 

- **_exc_value** (BaseException | None): 

- **_traceback** (TracebackType | None): 

#### Returns

None

---

## Class `SonioxClient`

Synchronous Soniox REST client exposing API namespaces via httpx.

### Attributes

- **_http_client**: 

- **files**: 

- **transcriptions**: 

- **models**: 

- **auth**: 

- **webhooks**: 

- **realtime**: 

### `__init__`

#### Signature

```python
__init__(*, api_key: str | None = None, api_base_url: str | None = None, websocket_base_url: str | None = None, timeout_sec: float | None = None, webhook_secret: str | None = None, webhook_signature_header: str | None = None, **client_kwargs: Any) -> None
```

#### Parameters

- **self** (None): 

- **api_key** (str | None): 

- **api_base_url** (str | None): 

- **websocket_base_url** (str | None): 

- **timeout_sec** (float | None): 

- **webhook_secret** (str | None): 

- **webhook_signature_header** (str | None): 

- **client_kwargs** (Any): 

#### Returns

None

### `request`

Perform a request against the configured Soniox REST endpoint.

#### Signature

```python
request(method: str, path: str, *, params: Mapping[str, Any] | None = None, json: Any | None = None, data: Mapping[str, Any] | None = None, files: Mapping[str, Any] | None = None) -> httpx.Response
```

#### Parameters

- **self** (None): 

- **method** (str): 

- **path** (str): 

- **params** (Mapping[str, Any] | None): 

- **json** (Any | None): 

- **data** (Mapping[str, Any] | None): 

- **files** (Mapping[str, Any] | None): 

#### Returns

httpx.Response

### `close`

Close the underlying HTTP transport.

#### Signature

```python
close() -> None
```

#### Parameters

- **self** (None): 

#### Returns

None

### `__enter__`

#### Signature

```python
__enter__() -> SonioxClient
```

#### Parameters

- **self** (None): 

#### Returns

SonioxClient

### `__exit__`

#### Signature

```python
__exit__(_exc_type: type[BaseException] | None, _exc_value: BaseException | None, _traceback: TracebackType | None) -> None
```

#### Parameters

- **self** (None): 

- **_exc_type** (type[BaseException] | None): 

- **_exc_value** (BaseException | None): 

- **_traceback** (TracebackType | None): 

#### Returns

None