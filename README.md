# Soniox Python SDK

The SDK exposes two clients: `SonioxClient` (sync) and `AsyncSonioxClient`. Client can hit every Soniox REST endpoint or open a real-time websocket session, so you can focus on building features instead of dealing with boilerplate.
Auth, file uploads, transcription polling, webhook helpers, and real-time stream helpers all live in one typed package.

## Install

```bash
pip install soniox
# or if using uv
uv add soniox
export SONIOX_API_KEY=<your-key>
```

Get your API key from the [Soniox Console](https://console.soniox.com) and inject it once per shell session. Both clients read `SONIOX_API_KEY` by default, but you can override it per-client if needed.

## Quick run (rest + real-time)

1. **REST transcription**: copy this snippet or run [`examples/soniox_client/api_example.py`](https://github.com/soniox/soniox-python/blob/main/examples/soniox_client/api_example.py).

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

2. **Real-time streaming**: the real-time helpers mirror the sync rest sample—open `client.realtime.stt.connect`, call `session.send_byte_chunk` or `session.send_bytes`, then iterate `session.receive_events()` to render tokens. example:

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

see [`examples/soniox_client/realtime_example.py`](https://github.com/soniox/soniox-python/blob/main/examples/soniox_client/realtime_example.py) for the full flow.

## Repository layout

- `src/soniox/` – sdk code (clients, http namespaces, real-time/session helpers, types, utils).
- `examples/soniox_client` & `examples/async_soniox_client` – runnable rest + real-time flows for sync and async.
- `docs/` – markdown outputs (e.g., `docs/python-sdk.md`) that come from `pydoc-markdown`.
- `assets/` – sample audio referenced by the examples.
- `tests/` – pytest narratives that describe the public behavior.

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
