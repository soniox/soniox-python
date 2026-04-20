# Soniox Python SDK

The SDK exposes two clients: `SonioxClient` (sync) and `AsyncSonioxClient` (async). Each client supports:
- STT over REST (`client.stt`) and realtime WebSocket (`client.realtime.stt`)
- TTS over REST (`client.tts`) and realtime WebSocket (`client.realtime.tts`)
- auth, file uploads, model listing, webhooks, and typed request/response models

## Install

```bash
pip install soniox
# or if using uv
uv add soniox
export SONIOX_API_KEY=<your-key>
```

Get your API key from the [Soniox Console](https://console.soniox.com) and inject it once per shell session. Both clients read `SONIOX_API_KEY` by default, but you can override it per-client if needed.

## Quick run (STT + TTS, REST + realtime)

1. **REST STT transcription**: copy this snippet or run [`examples/soniox_client/api_example.py`](https://github.com/soniox/soniox-python/blob/main/examples/soniox_client/api_example.py).

```python
from soniox import SonioxClient

client = SonioxClient()
transcription = client.stt.transcribe(
    audio_url="https://soniox.com/media/examples/coffee_shop.mp3",
    client_reference_id="docs-quick-start",
)
client.stt.wait(transcription.id, timeout_sec=60)
print(client.stt.get_transcript(transcription.id).text[:200])
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
    model="tts-rt-v1-preview",
    language="en",
    voice="Adrian",
    audio_format="wav",
)
print(f"Wrote {written} bytes to {output_file.resolve()}")
client.close()
```

Run the full example at [`examples/soniox_client/tts_api_example.py`](https://github.com/soniox/soniox-python/blob/main/examples/soniox_client/tts_api_example.py) or async version at [`examples/async_soniox_client/tts_api_example.py`](https://github.com/soniox/soniox-python/blob/main/examples/async_soniox_client/tts_api_example.py).

3. **Realtime STT streaming**: open `client.realtime.stt.connect`, call `session.send_byte_chunk` or `session.send_bytes`, then iterate `session.receive_events()` to render tokens:

```python
from soniox import SonioxClient
from soniox.types import RealtimeSTTConfig, Token
from soniox.utils import render_tokens, throttle_audio, start_audio_thread

DEMO_FILE = "path_to_your_audio_file"

client = SonioxClient()
config = RealtimeSTTConfig(model="stt-rt-v4", audio_format="mp3")
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
```

See [`examples/soniox_client/realtime_example.py`](https://github.com/soniox/soniox-python/blob/main/examples/soniox_client/realtime_example.py) for the full flow.

4. **Realtime TTS streaming**: send text chunks and read synthesized audio chunks from the session.

```python
from uuid import uuid4

from soniox import SonioxClient
from soniox.types import RealtimeTTSConfig

client = SonioxClient()
config = RealtimeTTSConfig(
    stream_id=f"sync-{uuid4()}",
    model="tts-rt-v1-preview",
    language="en",
    voice="Adrian",
    audio_format="wav",
)

audio_chunks: list[bytes] = []
with client.realtime.tts.connect(config=config) as session:
    session.keep_alive()
    session.send_text_chunks(
        ["Hello from realtime TTS. ", "This is the final chunk."],
        text_end=True,
    )
    for chunk in session.receive_audio_chunks():
        audio_chunks.append(chunk)

print(f"Collected {sum(len(c) for c in audio_chunks)} bytes of audio")
```

Run the full example at [`examples/soniox_client/tts_realtime_example.py`](https://github.com/soniox/soniox-python/blob/main/examples/soniox_client/tts_realtime_example.py) or async version at [`examples/async_soniox_client/tts_realtime_example.py`](https://github.com/soniox/soniox-python/blob/main/examples/async_soniox_client/tts_realtime_example.py).

## Repository layout

- `src/soniox/` – sdk code (clients, http namespaces, real-time/session helpers, types, utils).
- `examples/soniox_client` & `examples/async_soniox_client` – runnable STT and TTS examples for sync and async clients.
- `docs/` – markdown outputs (e.g., `docs/python-sdk.md`) that come from `pydoc-markdown`.
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
