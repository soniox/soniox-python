import asyncio
from collections.abc import AsyncIterator
from uuid import uuid4

from soniox.client import AsyncSonioxClient
from soniox.errors import SonioxRealtimeError
from soniox.types import RealtimeTTSConfig, TtsAudioFormat
from soniox.utils import output_file_for_audio_format

MODEL = "tts-rt-v1"
LANGUAGE = "en"
VOICE = "Maya"
AUDIO_FORMAT: TtsAudioFormat = "wav"

TEXT_CHUNKS = [
    "Welcome to Soniox real-time Text-to-Speech. ",
    "As text is streamed in, audio streams back in parallel with high accuracy, ",
    "so your application can start playing speech ",
    "within milliseconds of the first word.",
]


async def _iter_text_chunks(chunks: list[str]) -> AsyncIterator[str]:
    for chunk in chunks:
        yield chunk


async def main() -> None:
    client = AsyncSonioxClient()
    output_file = output_file_for_audio_format(AUDIO_FORMAT, "tts_realtime_async")
    config = RealtimeTTSConfig(
        stream_id=f"async-{uuid4()}",
        model=MODEL,
        language=LANGUAGE,
        voice=VOICE,
        audio_format=AUDIO_FORMAT,
    )

    audio_chunks: list[bytes] = []
    try:
        async with client.realtime.tts.connect(config=config) as connection:
            send_task = asyncio.create_task(
                connection.send_text_chunks(_iter_text_chunks(TEXT_CHUNKS), text_end=True),
                name="tts-async-sender",
            )
            try:
                async for chunk in connection.receive_audio_chunks():
                    audio_chunks.append(chunk)
            except SonioxRealtimeError as exc:
                print("Realtime TTS error (keeping partial audio):", exc)
            await asyncio.gather(send_task, return_exceptions=True)
    finally:
        output = b"".join(audio_chunks)
        if output:
            output_file.write_bytes(output)
            print(f"Wrote {len(output)} bytes to {output_file.resolve()}")
        else:
            print("No audio file was written.")
        await client.aclose()


if __name__ == "__main__":
    asyncio.run(main())
