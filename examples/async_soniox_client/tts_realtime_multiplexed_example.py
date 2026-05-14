import asyncio
from collections.abc import AsyncIterator
from uuid import uuid4

from soniox.client import AsyncSonioxClient
from soniox.types import RealtimeTTSConfig, TtsAudioFormat
from soniox.utils import output_file_for_audio_format

MODEL = "tts-rt-v1"
AUDIO_FORMAT: TtsAudioFormat = "wav"

STREAM_SPECS = {
    "a": {
        "language": "en",
        "voice": "Adrian",
        "chunks": [
            "Welcome to Soniox real-time Text-to-Speech. ",
            "This stream demonstrates English speech generation. ",
            "Thank you for listening.",
        ],
    },
    "b": {
        "language": "sl",
        "voice": "Maya",
        "chunks": [
            "Dobrodošli v sistem Soniox za pretvorbo besedila v govor v realnem času. ",
            "Ta tok prikazuje generiranje slovenskega govora. ",
            "Hvala za poslušanje.",
        ],
    },
    "c": {
        "language": "es",
        "voice": "Daniel",
        "chunks": [
            "Bienvenido a Soniox texto a voz en tiempo real. ",
            "Este flujo demuestra la generación de voz en español. ",
            "Gracias por escuchar.",
        ],
    },
}


async def iter_text_chunks(
    chunks: list[str],
    *,
    delay_seconds: float = 0.0,
) -> AsyncIterator[str]:
    for chunk in chunks:
        yield chunk
        if delay_seconds:
            await asyncio.sleep(delay_seconds)


async def collect_stream_audio(stream) -> tuple[bytes, BaseException | None]:
    audio_chunks: list[bytes] = []
    try:
        async for chunk in stream.receive_audio_chunks():
            audio_chunks.append(chunk)
    except BaseException as exc:
        return b"".join(audio_chunks), exc
    return b"".join(audio_chunks), None


def write_outputs(audio_by_stream: dict[str, bytes]) -> None:
    for key, audio in sorted(audio_by_stream.items()):
        output_path = output_file_for_audio_format(
            AUDIO_FORMAT,
            f"tts_realtime_async_multiplexed_{key}",
        )
        if audio:
            output_path.write_bytes(audio)
            print(
                f"Wrote stream {key.upper()} ({len(audio)} bytes) to {output_path.resolve()}"
            )
        else:
            print(f"No audio file was written for stream {key.upper()}.")


async def main() -> None:
    client = AsyncSonioxClient()

    configs = {
        key: RealtimeTTSConfig(
            stream_id=f"async-{key}-{uuid4()}",
            model=MODEL,
            language=spec["language"],
            voice=spec["voice"],
            audio_format=AUDIO_FORMAT,
        )
        for key, spec in STREAM_SPECS.items()
    }

    audio_by_stream: dict[str, bytes] = {}
    errors: list[BaseException] = []

    try:
        async with client.realtime.tts.connect_multi_stream() as connection:
            streams = {
                key: await connection.open_stream(config=configs[key])
                for key in sorted(configs)
            }

            receiver_tasks = [
                asyncio.create_task(
                    collect_stream_audio(stream),
                    name=f"tts-async-recv-{key}",
                )
                for key, stream in streams.items()
            ]

            sender_tasks = [
                asyncio.create_task(
                    stream.send_text_chunks(
                        iter_text_chunks(STREAM_SPECS[key]["chunks"], delay_seconds=0.5),
                        text_end=True,
                    ),
                    name=f"tts-async-send-{key}",
                )
                for key, stream in streams.items()
            ]

            sender_results = await asyncio.gather(*sender_tasks, return_exceptions=True)
            for result in sender_results:
                if isinstance(result, BaseException):
                    errors.append(result)

            receiver_results = await asyncio.gather(
                *receiver_tasks, return_exceptions=True
            )
            for key, result in zip(streams.keys(), receiver_results, strict=True):
                if isinstance(result, BaseException):
                    errors.append(result)
                else:
                    audio, err = result
                    audio_by_stream[key] = audio
                    if err is not None:
                        errors.append(err)

            for exc in errors:
                print("Realtime multiplexed TTS error (keeping partial audio):", exc)
    finally:
        write_outputs(audio_by_stream)
        await client.aclose()


if __name__ == "__main__":
    asyncio.run(main())
