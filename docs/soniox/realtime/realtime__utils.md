---
title: soniox.realtime._utils
description: Description for _utils
keywords: annotations, asyncio, threading, Awaitable, Callable, KEEP_ALIVE_INTERVAL_SEC, KeepaliveThread, KeepaliveTask
---


---

## Class `KeepaliveThread`

Background thread that periodically invokes a callback until stopped.

### Attributes

- **_callback**: 

- **_interval**: 

- **_stop_event**: 

- **_thread**: 

### `__init__`

Args:
    callback:
        Callable invoked on each tick. If it raises, the loop exits.
    interval:
        Seconds between ticks.

#### Signature

```python
__init__(callback: Callable[[], None], interval: float) -> None
```

#### Parameters

- **self** (None): 

- **callback** (Callable[[], None]): 

- **interval** (float): 

#### Returns

None

### `start`

Start the background thread.

#### Signature

```python
start() -> None
```

#### Parameters

- **self** (None): 

#### Returns

None

### `stop`

Signal the thread to stop and block until it exits.

#### Signature

```python
stop() -> None
```

#### Parameters

- **self** (None): 

#### Returns

None

### `_loop`

#### Signature

```python
_loop() -> None
```

#### Parameters

- **self** (None): 

#### Returns

None

---

## Class `KeepaliveTask`

Async background task that periodically invokes a callback until stopped.

### Attributes

- **_callback**: 

- **_interval**: 

- **_stop_event**: 

- **_task**: 

### `__init__`

Args:
    callback:
        Coroutine function invoked on each tick. If it raises, the loop exits.
    interval:
        Seconds between ticks.

#### Signature

```python
__init__(callback: Callable[[], Awaitable[None]], interval: float) -> None
```

#### Parameters

- **self** (None): 

- **callback** (Callable[[], Awaitable[None]]): 

- **interval** (float): 

#### Returns

None

### `start`

Schedule the background task on the running event loop.

#### Signature

```python
start() -> None
```

#### Parameters

- **self** (None): 

#### Returns

None

### `stop`

Signal the task to stop and wait for it to finish.

#### Signature

```python
stop() -> None
```

#### Parameters

- **self** (None): 

#### Returns

None

### `_loop`

#### Signature

```python
_loop() -> None
```

#### Parameters

- **self** (None): 

#### Returns

None