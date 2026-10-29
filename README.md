# Soniox Python SDK

The SDK exposes two clients: `SonioxClient` (sync) and `AsyncSonioxClient` (async). Each client supports:

- STT over REST (`client.stt`) and realtime WebSocket (`client.realtime.stt`)
- TTS over REST (`client.tts`) and realtime WebSocket (`client.realtime.tts`)
- voice cloning (`client.voices`) - clone a voice from a reference clip and use it in TTS
- usage and cost (`client.usage`, `client.usage_logs`) - daily spend per model, and per-request logs
- organization administration (`client.organization`) - balance, limits, usage across projects, and project API keys
- auth, file uploads, model listing, webhooks, and typed request/response models


## Install

```bash
pip install soniox
# or if using uv
uv add soniox
export SONIOX_API_KEY=<your-key>
```

Get your API key from the [Soniox Console](https://console.soniox.com) and inject it once per shell session. Both clients read `SONIOX_API_KEY` by default, but you can override it per-client if needed.

> **Avoid Python 3.13.6** - it has a regression in `ssl` that hangs realtime STT/TTS (CPython issue [#137583](https://github.com/python/cpython/issues/137583)). Use any other 3.10-3.13.x.

## Quick run (STT + TTS, REST + realtime)

1. **REST STT transcription**: transcribe a local file end-to-end in one call. Full example: [`examples/soniox_client/api_example.py`](https://github.com/soniox/soniox-python/blob/main/examples/soniox_client/api_example.py).

```python
from soniox import SonioxClient

client = SonioxClient()
transcript = client.stt.transcribe_and_wait_with_tokens(
    file="path/to/audio.mp3",                # local file
    # audio_url="https://example.com/audio.mp3",  # or remote URL
    delete_after=True,                        # auto-cleanup file + transcription
)
print(transcript.text)
client.close()
```

2. **REST TTS generation**: convert text to an audio file.

```python
from soniox import SonioxClient
from soniox.utils import output_file_for_audio_format

client = SonioxClient()
output_file = output_file_for_audio_format("wav", "tts_sync_output")
written = client.tts.generate_to_file(
    output_file,
    text="Hello from Soniox Python SDK Text-to-Speech.",
    model="tts-rt-v2",
    language="en",
    voice="Adrian",
    audio_format="wav",
)
print(f"Wrote {written} bytes to {output_file.resolve()}")
client.close()
```

Run the full example at [`examples/soniox_client/tts_api_example.py`](https://github.com/soniox/soniox-python/blob/main/examples/soniox_client/tts_api_example.py) or async version at [`examples/async_soniox_client/tts_api_example.py`](https://github.com/soniox/soniox-python/blob/main/examples/async_soniox_client/tts_api_example.py).

The `voice` above is a built-in (shared) voice name. To browse a model's shared voices, filtered by gender, age, accent, use case or style:

```python
for v in client.voices.list_all_shared("tts-rt-v2", gender="female", style=["calm"]):
    print(v.id, v.accent, v.description)
```

Use `client.voices.list_shared(...)` for a single page with an explicit `cursor`.

You can also **clone a voice** from a reference audio clip and pass the returned voice id as `voice`:

```python
voice = client.voices.create("reference.wav", name="my-cloned-voice")
# Cloning runs asynchronously; poll client.voices.get(voice.id) until a model
# reports status "ready", then synthesize with voice=voice.id.
```

See the [voice cloning guide](https://soniox.com/docs/tts/concepts/voice-cloning) for details.

Output settings that are not identity - `speed`, `reduce_silence`, sample rate, bitrate - go on `CreateTtsConfig`:

```python
from soniox.types import CreateTtsConfig

client.tts.generate(
    text="Hello.",
    voice="Adrian",
    model="tts-rt-v2",
    language="en",
    config=CreateTtsConfig(speed=1.1, reduce_silence=True),
)
```

`reduce_silence` shortens the pauses between words and is only accepted by models whose
`supports_silence_reduction` is `true` in `client.tts_models.list()`.

3. **Realtime STT streaming**: open `client.realtime.stt.connect`, call `session.send_byte_chunk` or `session.send_bytes`, then iterate `session.receive_events()` to render tokens:

```python
from soniox import SonioxClient
from soniox.types import RealtimeSTTConfig, Token
from soniox.utils import render_tokens, throttle_audio, start_audio_thread

DEMO_FILE = "path_to_your_audio_file"

client = SonioxClient()
config = RealtimeSTTConfig(model="stt-rt-v5", audio_format="mp3")
final_tokens: list[Token] = []
non_final_tokens: list[Token] = []

def realtime():
    with client.realtime.stt.connect(config=config) as session:
        start_audio_thread(session, throttle_audio(DEMO_FILE, delay_seconds=0.1))
        for event in session.receive_events():
            for token in event.tokens:
                if token.is_final:
                    final_tokens.append(token)
                else:
                    non_final_tokens.append(token)
            print(render_tokens(final_tokens, non_final_tokens))
            non_final_tokens.clear()

realtime()
client.close()
```

See [`examples/soniox_client/realtime_example.py`](https://github.com/soniox/soniox-python/blob/main/examples/soniox_client/realtime_example.py) for the full flow.

In a **voice agent**, tell Soniox what your agent is saying so those same words are recognized
when the user says them back, and so the agent's own voice bleeding into the microphone is not
transcribed as the user. Set `enable_agent_text_input` on the config - the model must report
`supports_agent_text_input` in `client.models.list()` - and send the text with
`session.send_agent_text()`:

```python
config = RealtimeSTTConfig(
    model="stt-rt-v6",
    audio_format="pcm_s16le",
    sample_rate=24000,
    num_channels=1,
    enable_agent_text_input=True,
)

tts_config = RealtimeTTSConfig(
    model="tts-rt-v2",
    voice="Adrian",
    language="en",
    audio_format="pcm_s16le",
    sample_rate=24000,
    return_timestamps=True,
)

with (
    client.realtime.stt.connect(config=config) as session,
    client.realtime.tts.connect(config=tts_config) as tts,
    sd.RawOutputStream(samplerate=24000, channels=1, dtype="int16") as speaker,
):
    # Microphone audio goes in with session.send_byte_chunk(chunk) on its own thread.
    tts.send_text_chunks("We have a flat white and a cortado today.")
    for event in tts.receive_events():
        chunk = event.audio_bytes()
        if chunk is None:
            continue
        speaker.write(chunk)                       # blocks until the audio is taken
        spoken = "".join(event.timestamps.characters) if event.timestamps else ""
        session.send_agent_text(spoken, end_of_segment=False)

    session.send_agent_text("")                    # closes the segment
```

Soniox places the text by **where it sits among the audio frames**, so send each piece as it
plays, not when it was generated - sending the whole reply up front puts it in the wrong place.
Realtime TTS gives you the alignment for free with `return_timestamps`: each event's
`timestamps.characters` are the characters of that audio chunk, so the chunk you just handed to
the speaker and its text belong together. An empty text closes the segment, which is also how
you handle a barge-in - stop writing audio, close the segment, and only the words the user
actually heard were sent.

Echo cancellation is the other half and it is not the SDK's: it belongs to the platform. Use a
headset with hardware AEC, or on Linux `pactl load-module module-echo-cancel` and record from
the source it creates. Agent text covers what cancellation cannot - it is never perfect, and the
user will often repeat the agent's words back.

Run the full example at [`examples/soniox_client/agent_text_example.py`](https://github.com/soniox/soniox-python/blob/main/examples/soniox_client/agent_text_example.py) or async version at [`examples/async_soniox_client/agent_text_example.py`](https://github.com/soniox/soniox-python/blob/main/examples/async_soniox_client/agent_text_example.py). For the real loop - a live microphone, realtime TTS on the speakers and the agent's text timed to playback - see [`examples/soniox_client/agent_text_mic_example.py`](https://github.com/soniox/soniox-python/blob/main/examples/soniox_client/agent_text_mic_example.py) (needs `pip install sounddevice`).

4. **Realtime TTS streaming**: send text chunks and write audio to a file as it arrives.

```python
from uuid import uuid4

from soniox import SonioxClient
from soniox.types import RealtimeTTSConfig
from soniox.utils import output_file_for_audio_format

client = SonioxClient()
config = RealtimeTTSConfig(
    stream_id=f"sync-{uuid4()}",
    model="tts-rt-v2",
    language="en",
    voice="Adrian",
    audio_format="wav",
)

output_file = output_file_for_audio_format("wav", "tts_realtime_output")
bytes_written = 0
with client.realtime.tts.connect(config=config) as session, output_file.open("wb") as f:
    session.send_text_chunks(
        ["Hello from realtime TTS. ", "This is the final chunk."],
        text_end=True,
    )
    for chunk in session.receive_audio_chunks():
        f.write(chunk)
        bytes_written += len(chunk)

print(f"Wrote {bytes_written} bytes to {output_file.resolve()}")
```

Run the full example at [`examples/soniox_client/tts_realtime_example.py`](https://github.com/soniox/soniox-python/blob/main/examples/soniox_client/tts_realtime_example.py) or async version at [`examples/async_soniox_client/tts_realtime_example.py`](https://github.com/soniox/soniox-python/blob/main/examples/async_soniox_client/tts_realtime_example.py).

## Usage and cost

`client.usage.summary()` returns daily cost and activity for the project, rolled up per model
and across all models. `start_time` is inclusive, `end_time` exclusive, both ISO 8601 UTC, and
the window may span at most 366 days.

```python
summary = client.usage.summary(
    start_time="2026-04-01T00:00:00Z",
    end_time="2026-05-01T00:00:00Z",
)
print(summary.total.total_cost_usd)
for entry in summary.models:
    print(entry.model, entry.total_cost_usd)
```

Each entry carries a `days` list plus per-day lists (`cost_usd`, `num_requests`, ...) aligned to
it by index. For per-request records instead, use `client.usage_logs.list()` / `list_all()`.

`client.concurrency_limits` covers concurrency: `get()` for current counts and configured limits,
`history()` for past peaks aggregated per minute (`60`), hour (`3600`), or day (`86400`).

```python
history = client.concurrency_limits.history(
    "2026-04-28T09:00:00Z",
    "2026-04-28T10:00:00Z",
    period_sec=60,
    kind="tts",
)
peak = max(entry.sample_max for entry in history.entries)
```

## Organization administration

`client.organization` covers the whole organization rather than one project, so every call
needs an **organization API key**. It goes in the same `Authorization` header, so pass it as
`api_key`; a project key gets a `SonioxPermissionDeniedError`.

```python
client = SonioxClient(api_key=organization_api_key)

balance = client.organization.balance()
print(balance.available_balance_usd, balance.balance_exhausted)

monthly = client.organization.monthly_usage("2026-04")      # defaults to this month
for project in monthly.projects:
    print(project.name, project.usage_usd)
```

`usage_summary(start_time, end_time)` returns the same per-day entries as
`client.usage.summary()`, split per project instead of per model. `get()`, `limits()` and
`projects()` cover identity, per-region quotas and the project list. Amounts are decimal
strings everywhere, never floats.

API keys of a project are managed with `list_project_api_keys()`,
`create_project_api_key()` and `delete_project_api_key()`. The create call is the only place
the secret appears - it is in `key` on the response and is not retrievable afterwards.

```python
created = client.organization.create_project_api_key(
    project_id,
    name="ci",
    permissions=["stt_async:write", "files:write"],
)
print(created.key)  # store it now; you cannot read it back
```

Run the full example at [`examples/soniox_client/organization_example.py`](https://github.com/soniox/soniox-python/blob/main/examples/soniox_client/organization_example.py) or async version at [`examples/async_soniox_client/organization_example.py`](https://github.com/soniox/soniox-python/blob/main/examples/async_soniox_client/organization_example.py).

## Repository layout

- `src/soniox/` – sdk code (clients, http namespaces, real-time/session helpers, types, utils).
- `examples/soniox_client` & `examples/async_soniox_client` – runnable STT and TTS examples for sync and async clients.
- `docs/` – markdown reference (`async_client.md`, `realtime_client.md`, `types.md`, `utils.md`, `errors.md`) generated by `scripts/generate_docs.py`.
- `assets/` – sample audio referenced by the examples.

## Development

```bash
uv install --with dev
```

This pulls in `ruff`, `pyright`, `pytest`, etc., so you can lint, type-check, test, and regenerate docs locally.

## Docs

```bash
source .venv/bin/activate
python3 scripts/generate_docs.py
```

Docs are output to `/docs` directory.

## Resources

- [soniox.com/docs](https://soniox.com/docs/stt/SDKs/python-SDK) – official Soniox documentation.
- [GitHub repo](https://github.com/soniox/soniox-python) – source, examples, and scripts.
- [PyPI](https://pypi.org/project/soniox/)
- Support: `support@soniox.com`.
