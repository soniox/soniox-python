# Soniox Python SDK

This documentation is the static companion to the SDK’s README. The left-hand sidebar contains
the generated API reference, while this landing page highlights the main workflows you can build with Soniox.

## Quick starts

### REST transcription (sync)

```python
from soniox.client import SonioxClient

client = SonioxClient()
transcription = client.transcriptions.create(file_id="existing-file-id")
client.transcriptions.wait(transcription.id, timeout_sec=30)
print(client.transcriptions.get_transcript(transcription.id).text)
```

### Realtime stream (sync)

```python
from soniox.client import SonioxClient
from soniox.types import RealtimeSttConfig
from soniox.utils import stream_audio

config = RealtimeSttConfig(model="stt-rt-v1", audio_format="mp3")
client = SonioxClient()
with client.realtime.stt.connect(config=config) as session:
    session.send_bytes(stream_audio("assets/audio_dialog.mp3"))
    for event in session.receive_events():
        print(event.tokens[:5])
```

The `examples/` directory includes working scripts if you want async variants or longer demos.
