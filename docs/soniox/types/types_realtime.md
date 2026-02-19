---
title: "soniox.types.realtime"
description: "Event payload received from the realtime STT websocket."
keywords: "RealtimeControlType, RealtimeEvent, RealtimeSTTConfig"
---

---

## RealtimeEvent

Event payload received from the realtime STT websocket.

<a id="realtimeevent-properties"></a>

### Properties

| Property | Type |
| ------ | ------ |
| `model_config` | `-` |
| `tokens` | `list[Token]` |
| `final_audio_proc_ms` | `int \| None` |
| `total_audio_proc_ms` | `int \| None` |
| `finished` | `bool` |
| `error_code` | `int \| None` |
| `error_message` | `str \| None` |

<a id="realtimeevent-validate_event"></a>

### validate_event()

```python
validate_event(raw: str | bytes) -> RealtimeEvent
```

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `raw` | `str \| bytes` |

**Returns**

`RealtimeEvent`

---

## RealtimeSTTConfig

Configuration for initiating a realtime transcription session.

<a id="realtimesttconfig-properties"></a>

### Properties

| Property | Type |
| ------ | ------ |
| `api_key` | `str \| None` |
| `model` | `str` |
| `audio_format` | `str` |
| `num_channels` | `int \| None` |
| `sample_rate` | `int \| None` |
| `language_hints` | `list[str] \| None` |
| `language_hints_strict` | `bool \| None` |
| `context` | `StructuredContext \| None` |
| `enable_speaker_diarization` | `bool \| None` |
| `enable_language_identification` | `bool \| None` |
| `enable_endpoint_detection` | `bool \| None` |
| `translation` | `TranslationConfig \| None` |
| `client_reference_id` | `str \| None` |

<a id="realtimesttconfig-build_payload"></a>

### build_payload()

```python
build_payload(api_key: str) -> RealtimeSTTConfig
```

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `api_key` | `str` |

**Returns**

`RealtimeSTTConfig`

---

## RealtimeControlType

Control messages that can be sent over a realtime session.

<a id="realtimecontroltype-properties"></a>

### Properties

| Property | Type |
| ------ | ------ |
| `FINISH` | `-` |
| `KEEP_ALIVE` | `-` |
| `FINALIZE` | `-` |