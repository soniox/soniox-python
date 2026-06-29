# Changelog

All notable changes to this project will be documented in this file.

The format is inspired by Keep a Changelog and this project follows Semantic Versioning.

## Quick Guide for Contributors

- Every PR that changes behavior must update **[Unreleased]**.
- Write from the **user’s perspective** (what changed for SDK users).
- Keep entries short (one clear sentence).
- Use the correct section: **Added**, **Changed**, **Fixed**, **Deprecated**, **Removed**, **Security**.
- Avoid internal details or commit-style messages.

**Release process (maintainers):**

- Rename **[Unreleased]** → new version + date.
- Add a fresh empty **[Unreleased]** section at the top.

### Version Categories Guide

Use the following categories when adding entries:

- **Added** - new features or capabilities.
- **Changed** - updates to existing functionality.
- **Deprecated** - features that will be removed soon.
- **Removed** - features removed in this version.
- **Fixed** - bug fixes.
- **Security** - vulnerability fixes.

---

### Writing Guidelines

- Write entries from the **user's perspective**, not implementation details.
  - ✅ "Added async file uploads"
  - ❌ "Refactored upload handler"

- Keep lines short and scannable.
- Group related changes into one bullet when possible.
- Avoid commit-message noise.
- Every released version should have a date.

---

### Versioning Notes

This project follows Semantic Versioning:

- **MAJOR** version when you make incompatible API changes.
- **MINOR** version when you add functionality in a backward-compatible manner.
- **PATCH** version when you make backward-compatible bug fixes.

Examples:

- `1.0.0` - stable API
- `1.1.0` - new features added
- `1.1.1` - bug fixes only

---

## [Unreleased]

### Added

- `speed` field on `CreateTtsConfig` and `RealtimeTTSConfig` (float 0.7–1.3, default 1.0) to control the speaking rate of generated speech. Supported on both REST and realtime.
- `return_timestamps` field on `RealtimeTTSConfig` to request character-to-audio alignment. When enabled, realtime response events carry a `timestamps` object (new `TtsTimestamps` type: parallel `characters` / `character_start_times_seconds` / `character_end_times_seconds` arrays). Realtime only — the REST endpoint streams raw audio and ignores it.
- `supports_endpoint_sensitivity`, `supports_endpoint_latency_adjustment`, and `endpoint_latency_adjustment_max_level` capability fields on the STT `Model` type, surfacing which endpoint-detection options a model accepts.
- Voices (voice-cloning) API at `client.voices` (sync and async): `list`, `list_all`, `count`, `get`, `get_or_none`, `create` (clone from a reference audio clip), `recompute` (prepare a voice for newly released models), `delete`, and `delete_if_exists`. New `Voice`, `VoiceModel`, and `VoiceModelStatus` types.
- `supports_timestamps`, `supports_speed_adjustment`, `speed_min`, and `speed_max` capability fields on the `TtsModel` type, surfacing which models support timestamps and speed adjustment and the supported speed range.

### Changed

### Deprecated

### Fixed

### Removed

---

## [2.7.0] - 24 jun 2026

### Added

- `endpoint_latency_adjustment_level` field on `RealtimeSTTConfig` (integer 0–3) to fine-tune the latency/accuracy trade-off of realtime endpoint detection.

### Changed

- TTS REST output settings (`audio_format`, `sample_rate`, `bitrate`) now live on `CreateTtsConfig`; `generate()` and `generate_to_file()` take the utterance's `text`, `voice`, `model`, and `language` directly. Each field now has a single home (no more flat-vs-config overlap). Existing flat-keyword calls keep working (see Deprecated).
- During the deprecation overlap, when a deprecated field is set both on the config and as a flat argument, the config value now takes precedence uniformly across STT and TTS (previously `client_reference_id` resolved the other way).

### Deprecated

- Passing `audio_format`, `sample_rate`, or `bitrate` as keyword arguments to TTS `generate()` / `generate_to_file()` is deprecated; set them on `CreateTtsConfig` instead. The keyword arguments still work but emit a `DeprecationWarning` and will be removed in a future major release.
- Setting `model`, `voice`, or `language` on `CreateTtsConfig` is deprecated; pass them directly to `generate()` / `generate_to_file()` (they describe the utterance, not output encoding).
- Relying on the default TTS `language` (`"en"`) is deprecated; pass `language` explicitly to `generate()` / `generate_to_file()`. It will become a required argument in the next major release.
- Setting `model` or `client_reference_id` on `CreateTranscriptionConfig` is deprecated; pass them directly to the transcription `create*` calls.

### Removed

- The internal module constants `DEFAULT_LANGUAGE` and `DEFAULT_AUDIO_FORMAT` in `soniox.api.tts` / `soniox.api.async_tts`. The defaults (`"en"` / `"wav"`) are now applied inside payload construction. Behavior is unchanged.

---

## [2.6.0] - 15 jun 2026

### Added

- `endpoint_sensitivity` field on `RealtimeSTTConfig`: adjusts how likely the model is to emit a speech endpoint. Allowed values are between -1.0 and 1.0; the default is 0.0. Introduced in the Soniox v5 model.

---

## [2.5.0] - 12 jun 2026

### Added

- `LanguageCode` type alias (`Annotated[str, Field(min_length=2, max_length=2)]`) representing an ISO 639-1 two-letter code. Now used by `TranslationConfig.target_language`, `language_a`, `language_b`, and by the `language_hints` lists on `CreateTranscriptionPayload`, `CreateTranscriptionConfig`, and `RealtimeSTTConfig`.
- `SupportedLanguage` model (renamed from `Language`) describing a `{code, name}` language entry returned by `client.models.list()`.
- `translate*` methods on the async and sync STT clients (`translate`, `translate_from_url`, `translate_from_file_id`, `translate_from_file`, `translate_and_wait`, `translate_and_wait_with_tokens`). Pass `to=` for one-way translation (optionally with `source=` as a strict language hint) or `between=("en", "fr")` for two-way; exactly one of `to` or `between` is required.
- `connect_timeout_sec` parameter on the realtime `connect()` and `connect_multi_stream()` methods (STT and TTS, sync and async): maximum seconds to wait for the WebSocket handshake. Defaults to 10 seconds; must be greater than zero. ([#4](https://github.com/soniox/soniox-python/pull/4) by [@imcooder](https://github.com/imcooder))

### Changed

- Reorganized reference docs: `async_client.md` now documents only the async surface (the sync `SonioxClient` is a line-by-line mirror, called out in a preamble); `realtime_client.md` continues to cover both sync and async realtime clients.
- Expanded the `output_file_for_audio_format` docstring with a proper `Args` block.
- `language_hints` fields now validate each entry as a two-letter code; previously any string was accepted client-side.
- Realtime WebSocket connection failures now raise `SonioxRealtimeError` (with message `"Connection timed out"` when the handshake times out) instead of propagating raw `websockets` exceptions. ([#4](https://github.com/soniox/soniox-python/pull/4) by [@imcooder](https://github.com/imcooder))
- Default model for asynchronous transcriptions is now `stt-async-v5` (was `stt-async-v4`).

### Deprecated

- `Language` is a deprecated alias for `SupportedLanguage`. Update imports to `from soniox.types import SupportedLanguage`.

### Fixed

- Removed Sphinx `:meth:` directive leaks from realtime STT client docstrings; they were rendering as raw text in the generated markdown reference.
- `AsyncRealtimeTTSClient.connect_multi_stream()` now validates that an API key is available, matching the sync `RealtimeTTSClient.connect_multi_stream()`; previously it silently constructed a connection with an empty key.

---

## [2.4.0] - 13 may 2026

### Added

- `client.files.count()` and `client.stt.count()` endpoints (and async variants) returning the total count of files and transcriptions.
- `client.usage_logs.list()` and `list_all()` (and async variants) for retrieving per-request usage logs over a time window.
- `client.concurrency_limits.get()` (and async variant) returning current and configured concurrency limits for realtime STT and TTS, scoped to project and organization.
- `TtsVoice.description` and `TtsVoice.gender` (`"male" | "female" | "neutral"`) fields, exposing richer voice metadata from the server. Enables programmatic voice filtering.
- `RealtimeSTTAudioFormat`, `RealtimeSTTHeaderFormat`, `RealtimeSTTRawFormat` literal types covering the 30 audio formats accepted by realtime STT.
- `py.typed` marker (PEP 561): downstream type-checkers now consume the SDK's inline type annotations.
- `StructuredContext.general` and `StructuredContext.translation_terms` now accept a plain dict in addition to the typed item lists.
- `finalize: bool = True` keyword-only parameter on realtime STT `pause()` (sync and async). When `False`, pause without emitting a finalize.
- `TtsModel.languages` field listing the languages supported by the model. Defaults to an empty list for backward compatibility with direct construction.
- `Language` type exported from `soniox.types` (previously only reachable via `soniox.types.api`).
- `ApiError.more_info` field - optional URL pointing to documentation for resolving an error.
- `Model.supports_max_endpoint_delay` flag indicating whether a model supports the `max_endpoint_delay_ms` option.
- Internal test suite (pytest + respx + polyfactory) covering REST, realtime websocket, schema drift, and sync/async parity. Not shipped to users; runnable via `just test`.

### Changed

- `RealtimeSTTConfig.audio_format` is now typed as a Literal union instead of bare `str`. Passing an unrecognized value raises at validation time instead of failing on the wire.
- Raw realtime STT audio formats (`pcm_*`, `mulaw`, `alaw`) now require `sample_rate` and `num_channels` on `RealtimeSTTConfig`. Previously these were silently accepted client-side and rejected by the server.

---

## [2.3.2] - 4 may 2026

### Added

- `single_use` and `max_session_duration_seconds` parameters on `client.auth.create_temporary_api_key()` (and the async variant).
- `tts_rt` value for `TemporaryApiKeyUsageType`, allowing temporary API keys to be scoped to realtime TTS.

---

## [2.3.1] - 29 apr 2026

### Changed

- Default TTS model is now `tts-rt-v1` (previously `tts-rt-v1-preview`).

---

## [2.3.0] - 22 apr 2026

### Added

- Text-to-Speech (TTS) support, available on both `SonioxClient` and `AsyncSonioxClient`.
- REST TTS API via `client.tts`: `generate()` returns audio bytes, `generate_to_file()` writes audio to a path or file-like object. Configurable `voice`, `model`, `language`, `audio_format`, `sample_rate`, and `bitrate`.
- TTS model listing via `client.tts_models.list()`.
- Realtime TTS over websocket via `client.realtime.tts.connect(...)`: stream text in with `send_text_chunk` / `send_text_chunks` / `finish`, receive audio with `receive_audio_chunks` or raw events with `receive_events`, plus `cancel`, `pause`, `resume`, and `keep_alive`.
- Multiplexed realtime TTS via `client.realtime.tts.connect_multi_stream()`: run multiple concurrent TTS streams over a single websocket connection using `open_stream`.
- New TTS examples for sync and async clients (REST, realtime, and multiplexed realtime).
- `tts_api_base_url` and `tts_websocket_base_url` client options for overriding TTS endpoints.

---

## [2.2.0] - 25 feb 2026

### Added

- max_endpoint_delay_ms parameter (v4 model only)
- fin (<fin>) and end (<end>) constants
- validation for TranslationConfig

### Changed

- Improved docs generating script

---

## [2.1.0] - 18 feb 2026

### Added

- pause and resume methods
- destroy_all method (removes all transcriptions and all files)
- send_bytes accepts finish parameter

### Changed

- renamed client.transcriptions to 'client.stt'
- removed send\_ prefix from methods (i.e. send_keep_alive -> keep_alive)

### Removed

- keep alive helpers (use pause, resume, or manually send keepalive message)

---

## [2.0.0] - 3 feb 2026

### Added

- Initial public release of the Python SDK.
- Core client implementation (sync and async).
- Full support for REST API and websocket API

### Removed

- Old Soniox Python SDK (versions 1._._)
