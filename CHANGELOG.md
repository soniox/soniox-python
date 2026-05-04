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

- **Added** — new features or capabilities.
- **Changed** — updates to existing functionality.
- **Deprecated** — features that will be removed soon.
- **Removed** — features removed in this version.
- **Fixed** — bug fixes.
- **Security** — vulnerability fixes.

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

- `1.0.0` — stable API
- `1.1.0` — new features added
- `1.1.1` — bug fixes only

---

## [Unreleased]

### Added

-

### Changed

-

### Fixed

-

### Removed

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
