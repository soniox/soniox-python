---
title: soniox.types.realtime
description: Description for realtime
keywords: annotations, json, Enum, BaseModel, ConfigDict, Field, StructuredContext, TranslationConfig, Token, RealtimeEvent, RealtimeSTTConfig, RealtimeControlType
---


---

## Class `RealtimeEvent`

Event payload received from the realtime STT websocket.

### Attributes

- **model_config**: 

- **tokens**: Tokens in this result.

- **final_audio_proc_ms**: Milliseconds of audio that have been finalized.

- **total_audio_proc_ms**: Total milliseconds of audio processed.

- **finished**: Whether this is the final result (session ending).

- **error_code**: Error code if the realtime operation failed.

- **error_message**: Human-readable description of the error.

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

- **api_key**: API key for real-time sessions.

- **model**: Speech-to-text model to use.

- **audio_format**: Audio format. Use 'auto' for automatic detection of container formats.

- **num_channels**: Number of audio channels (required for raw audio formats).

- **sample_rate**: Sample rate in Hz (required for PCM formats).

- **language_hints**: Expected languages in the audio (ISO language codes).

- **language_hints_strict**: When true, recognition is strongly biased toward language hints (best results when using one language in language_hints).

- **context**: Additional context to improve transcription accuracy.

- **enable_speaker_diarization**: Enable speaker identification.

- **enable_language_identification**: Enable automatic language detection.

- **enable_endpoint_detection**: Enable endpoint detection for utterance boundaries.

- **translation**: Translation configuration.

- **client_reference_id**: Optional tracking identifier (max 256 chars).

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