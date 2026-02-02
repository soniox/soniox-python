# Soniox Python SDK

Soniox is a speech-to-text service with production-ready REST and realtime APIs. This SDK
wraps both synchronous and asynchronous HTTP drivers plus a realtime session helper so you can
unify uploads, transcriptions, realtime streams, and webhook validation in one typed library.

## Quick start

1. **Prepare your environment**

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -e .[dev]
   export SONIOX_API_KEY=<your-key>
   ```

2. **Run the sync REST example**

   ```bash
   python examples/soniox_client/api_example.py
   ```

   It uploads `assets/coffee_shop.mp3`, polls until the transcription is ready, prints a snippet,
   and cleans up the temporary upload/transcription.

3. **Explore the realtime demo**

   ```bash
   python examples/soniox_client/realtime_example.py
   ```

   Use this as a reference for streaming audio toward Soniox and handling `RealtimeEvent` bundles.

Both examples illustrate handling `SonioxAPIError`/`SonioxNotFoundError`, making them excellent
starting points for production code paths.

## REST transcription sample

```python
from soniox.client import SonioxClient

client = SonioxClient()
upload = client.files.upload("assets/coffee_shop.mp3", client_reference_id="doc")
transcription = client.transcriptions.create(file_id=upload.id)
client.transcriptions.wait(transcription.id, timeout_sec=60)
print(client.transcriptions.get_transcript(transcription.id).text)
client.close()
```

This snippet mirrors what `examples/soniox_client/api_example.py` automates, including cleanup
via `client.transcriptions.delete` and `client.files.delete`.

## Realtime transcription + LLM streaming

```python
from soniox.client import SonioxClient
from soniox.types import RealtimeSttConfig

client = SonioxClient()
config = RealtimeSttConfig(model="stt-rt-v3", audio_format="mp3", language_hints=["en"])

with client.realtime.stt.connect(config=config) as session:
    session.send_bytes(open("assets/coffee_shop.mp3", "rb").read())
    for event in session.receive_events():
        final_tokens = [token.text for token in event.tokens if token.is_final]
        if final_tokens:
            # send final_tokens to your LLM pipeline instead of raw audio
            streaming_prompt = " ".join(final_tokens)
            # replace the following line with your LLM call
            print("LLM input chunk:", streaming_prompt)
```

Use `soniox.utils.render_tokens` in place of the print statement when you need human-readable
feedback before forwarding tokens. The realtime session yields `RealtimeEvent` objects so you can
drop non-final tokens until the first chunk of final text is available for your LLM.

## Development experience

### Environment best practices

- Keep `.venv` in the repo root and activate it before running commands.
- Install extras: `pip install -e .[dev]` gives you `ruff`, `pyright`, and `mkdocs`.
- Set `SONIOX_API_KEY` once per shell session; the SDK reads it by default but lets you override
  per-client via args.

### Documentation & helpers

- `mkdocs serve` builds `docs/` locally; the sidebar mirrors the API reference generated in
  `generated-docs/`.
- `preload.py` shows small snippets for syncing files, creating transcriptions, and attaching
  real-time sessions—handy when iterating in REPLs.
- `assets/` contains sample audio to exercise the examples without uploading your own files.

## Resources

- API docs: `docs/` (landing page + generated API sections in `docs/api`)
- Examples: `examples/soniox_client` (sync) and `examples/async_soniox_client`
- Realtime utils: `soniox.utils` includes `render_tokens`, `start_audio_thread`, and `throttle_audio`
- Asset samples: `assets/*.mp3`

If you need help, email `support@soniox.com` or consult the upstream README and API docs hosted
at the URLs in `pyproject.toml`.
