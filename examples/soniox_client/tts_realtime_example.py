import time
from collections.abc import Iterator
from uuid import uuid4

from soniox.client import SonioxClient
from soniox.errors import SonioxRealtimeError
from soniox.types import RealtimeTTSConfig, TtsAudioFormat
from soniox.utils import output_file_for_audio_format, start_text_thread

MODEL = "tts-rt-v1-preview"
LANGUAGE = "en"
VOICE = "Adrian"
AUDIO_FORMAT: TtsAudioFormat = "wav"

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
                for chunk in connection.receive_audio_chunks():
                    audio_chunks.append(chunk)
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
