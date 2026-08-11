import time
from collections.abc import Iterator
from uuid import uuid4

from soniox.client import SonioxClient
from soniox.errors import SonioxRealtimeError
from soniox.types import RealtimeTTSConfig, TtsAudioFormat
from soniox.utils import output_file_for_audio_format, start_text_thread

MODEL = "tts-rt-v2"
LANGUAGE = "en"
VOICE = "Adrian"  # a built-in voice name, or a cloned voice id from client.voices.create()
AUDIO_FORMAT: TtsAudioFormat = "wav"
SPEED = 1.1  # speaking rate, 0.7-1.3 (1.0 is normal speed)

TEXT_CHUNKS = [
    "Welcome to Soniox real-time Text-to-Speech. ",
    "As text is streamed in, audio streams back in parallel with high accuracy, ",
    "so your application can start playing speech ",
    "within milliseconds of the first word.",
]


def iter_text_chunks(chunks: list[str], *, delay_seconds: float = 0.0) -> Iterator[str]:
    for chunk in chunks:
        yield chunk
        if delay_seconds:
            time.sleep(delay_seconds)


def main() -> None:
    client = SonioxClient()
    output_file = output_file_for_audio_format(AUDIO_FORMAT, "tts_realtime_sync")
    config = RealtimeTTSConfig(
        stream_id=f"sync-{uuid4()}",
        model=MODEL,
        language=LANGUAGE,
        voice=VOICE,
        audio_format=AUDIO_FORMAT,
        speed=SPEED,
        return_timestamps=True,  # ask for character-to-audio timestamps on each event
    )

    audio_chunks: list[bytes] = []
    try:
        with client.realtime.tts.connect(config=config) as connection:
            sender = start_text_thread(
                connection,
                iter_text_chunks(TEXT_CHUNKS, delay_seconds=0.1),
                text_end=True,
                name="tts-sync-sender",
            )
            try:
                # Iterate events (not just audio chunks) so we can read timestamps too.
                for event in connection.receive_events():
                    chunk = event.audio_bytes()
                    if chunk:
                        audio_chunks.append(chunk)
                    if event.timestamps:
                        spoken = "".join(event.timestamps.characters)
                        print(f"timestamps for {spoken!r}")
            except SonioxRealtimeError as exc:
                print("Realtime TTS error (keeping partial audio):", exc)
            sender.join()
    finally:
        output = b"".join(audio_chunks)
        if output:
            output_file.write_bytes(output)
            print(f"Wrote {len(output)} bytes to {output_file.resolve()}")
        else:
            print("No audio file was written.")
        client.close()


if __name__ == "__main__":
    main()
