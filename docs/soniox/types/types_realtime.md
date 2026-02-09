---
title: soniox.types.realtime
description: Description for realtime
keywords: annotations, json, Enum, Literal, BaseModel, ConfigDict, Field, StructuredContext, TranslationConfig, Token, RealtimeEvent, RealtimeSTTConfig, RealtimeControlType, EventType, RealtimeSessionOpenPayload, RealtimeSessionClosePayload, RealtimeSessionFinishedPayload, RealtimeSessionErrorPayload, RealtimeSessionEventPayload
---


---

## Class `RealtimeEvent`

Event payload received from the realtime STT websocket.

### Attributes

- **model_config**: 

- **tokens**: 

- **final_audio_proc_ms**: 

- **total_audio_proc_ms**: 

- **finished**: 

- **error_code**: 

- **error_message**: 

### `validate_event`

#### Signature

```python
validate_event(raw: str | bytes) -> RealtimeEvent
```

#### Parameters

- **cls** (None): 

- **raw** (str | bytes): 

#### Returns

RealtimeEvent

---

## Class `RealtimeSTTConfig`

Configuration for initiating a realtime transcription session.

### Attributes

- **api_key**: 

- **model**: 

- **audio_format**: 

- **num_channels**: 

- **sample_rate**: 

- **language_hints**: 

- **language_hints_strict**: 

- **context**: 

- **enable_speaker_diarization**: 

- **enable_language_identification**: 

- **enable_endpoint_detection**: 

- **translation**: 

- **client_reference_id**: 

### `build_payload`

#### Signature

```python
build_payload(api_key: str) -> RealtimeSTTConfig
```

#### Parameters

- **self** (None): 

- **api_key** (str): 

#### Returns

RealtimeSTTConfig

---

## Class `RealtimeControlType`

Control messages that can be sent over a realtime session.

### Attributes

- **FINISH**: 

- **KEEP_ALIVE**: 

- **FINALIZE**: 

---

## Class `RealtimeSessionOpenPayload`

Event emitted when a realtime websocket session opens.

### Attributes

- **type**: 

- **model_config**: 

---

## Class `RealtimeSessionClosePayload`

Event emitted when a realtime websocket session closes.

### Attributes

- **type**: 

- **model_config**: 

---

## Class `RealtimeSessionFinishedPayload`

Event emitted when a realtime session finishes processing.

### Attributes

- **type**: 

- **event**: 

- **model_config**: 

---

## Class `RealtimeSessionErrorPayload`

Event emitted when a realtime session reports an error.

### Attributes

- **type**: 

- **error**: 

- **event**: 

- **model_config**: 