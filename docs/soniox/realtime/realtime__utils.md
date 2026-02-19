---
title: "soniox.realtime._utils"
description: "Background thread that periodically invokes a callback until stopped."
keywords: "KeepaliveTask, KeepaliveThread"
---

---

## KeepaliveThread

Background thread that periodically invokes a callback until stopped.

<a id="keepalivethread-constructor"></a>

### Constructor

```python
KeepaliveThread(callback: Callable[[], None], interval: float)
```

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `callback` | `Callable[[], None]` |
| `interval` | `float` |

**Returns**

`None`

<a id="keepalivethread-start"></a>

### start()

```python
start() -> None
```

Start the background thread.

**Returns**

`None`

***

<a id="keepalivethread-stop"></a>

### stop()

```python
stop() -> None
```

Signal the thread to stop and block until it exits.

**Returns**

`None`

---

## KeepaliveTask

Async background task that periodically invokes a callback until stopped.

<a id="keepalivetask-constructor"></a>

### Constructor

```python
KeepaliveTask(callback: Callable[[], Awaitable[None]], interval: float)
```

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `callback` | `Callable[[], Awaitable[None]]` |
| `interval` | `float` |

**Returns**

`None`

<a id="keepalivetask-start"></a>

### start()

```python
start() -> None
```

Schedule the background task on the running event loop.

**Returns**

`None`

***

<a id="keepalivetask-stop"></a>

### stop()

```python
stop() -> None
```

Signal the task to stop and wait for it to finish.

**Returns**

`None`