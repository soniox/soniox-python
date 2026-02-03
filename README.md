# Soniox Python SDK

The SDK exposes two clients: `SonioxClient` (sync) and `AsyncSonioxClient`. Client can hit every Soniox REST endpoint or open a realtime websocket session without wiring headers, retries, or payload validation yourself. Auth, file uploads, transcription polling, webhook helpers, and realtime stream helpers all live in one typed package.

## Install

```bash
uv add soniox
export SONIOX_API_KEY=<your-key>
```

Get your API key from the [Soniox Console](https://console.soniox.com) and inject it once per shell session. Both clients read `SONIOX_API_KEY` by default, but you can override it per-client if needed.

## Quick run (rest + realtime)

1. **REST transcription**: copy this snippet or run [`examples/soniox_client/api_example.py`](https://github.com/soniox/soniox-python/blob/main/examples/soniox_client/api_example.py).

```python
from soniox import SonioxClient

client = SonioxClient()
transcription = client.transcriptions.transcribe(
    audio_url="https://soniox.com/media/examples/coffee_shop.mp3",
    client_reference_id="docs-quick-start",
)
client.transcriptions.wait(transcription.id, timeout_sec=60)
print(client.transcriptions.get_transcript(transcription.id).text[:200])
```

2. **Realtime streaming**: the realtime helpers mirror the sync rest sample—open `client.realtime.stt.connect`, call `session.send_byte_chunk` or `session.send_bytes`, then iterate `session.receive_events()` to render tokens. example:

```python
from soniox import SonioxClient
from soniox.types import RealtimeSTTConfig, Token
from soniox.utils import render_tokens, throttle_audio, start_audio_thread

DEMO_FILE = "path_to_your_audio_file"

client = SonioxClient()
config = RealtimeSTTConfig(model="stt-rt-v3", audio_format="mp3")
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

- `src/soniox/` – sdk code (clients, http namespaces, realtime/session helpers, types, utils).
- `examples/soniox_client` & `examples/async_soniox_client` – runnable rest + realtime flows for sync and async.
- `docs/` – folder where `pydoc-markdown` command generates full sdk reference markdown file.
- `assets/` – sample audio referenced by the examples.
- `tests/` – pytest narratives that describe the public behavior.

## Development

```bash
uv install --with dev
```

This pulls in `ruff`, `pyright`, `pytest`, `pydoc-markdown`, etc., so you can lint, type-check, test, and regenerate docs locally.

## Resources

- [soniox.com/docs](https://soniox.com/docs) – official Soniox documentation.
- [GitHub repo](https://github.com/soniox/soniox-python) – source, examples, and scripts.
- Support: `support@soniox.com`.
