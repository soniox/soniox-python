import threading
import time
from collections.abc import Iterator
from uuid import uuid4

from soniox.client import SonioxClient
from soniox.types import RealtimeTTSConfig, TtsAudioFormat
from soniox.utils import output_file_for_audio_format, start_text_thread

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


def iter_text_chunks(chunks: list[str], *, delay_seconds: float = 0.0) -> Iterator[str]:
    for chunk in chunks:
        yield chunk
        if delay_seconds:
            time.sleep(delay_seconds)


def collect_stream_audio(
    stream,
    audio_by_stream: dict[str, bytes],
    key: str,
    errors: list[BaseException],
    lock: threading.Lock,
) -> None:
    chunks: list[bytes] = []
    try:
        for chunk in stream.receive_audio_chunks():
            chunks.append(chunk)
    except BaseException as exc:
        with lock:
            errors.append(exc)
    finally:
        audio_by_stream[key] = b"".join(chunks)


def write_outputs(audio_by_stream: dict[str, bytes]) -> None:
    for key, audio in sorted(audio_by_stream.items()):
        output_path = output_file_for_audio_format(
            AUDIO_FORMAT,
            f"tts_realtime_sync_multiplexed_{key}",
        )
        if audio:
            output_path.write_bytes(audio)
            print(f"Wrote stream {key.upper()} ({len(audio)} bytes) to {output_path.resolve()}")
        else:
            print(f"No audio file was written for stream {key.upper()}.")


def main() -> None:
    client = SonioxClient()

    configs = {
        key: RealtimeTTSConfig(
            stream_id=f"sync-{key}-{uuid4()}",
            model=MODEL,
            language=spec["language"],
            voice=spec["voice"],
            audio_format=AUDIO_FORMAT,
        )
        for key, spec in STREAM_SPECS.items()
    }

    errors: list[BaseException] = []
    errors_lock = threading.Lock()
    audio_by_stream: dict[str, bytes] = {}

    try:
        with client.realtime.tts.connect_multi_stream() as connection:
            streams = {key: connection.open_stream(config=configs[key]) for key in sorted(configs)}

            receiver_threads = [
                threading.Thread(
                    target=collect_stream_audio,
                    args=(stream, audio_by_stream, key, errors, errors_lock),
                    daemon=True,
                    name=f"tts-sync-recv-{key}",
                )
                for key, stream in streams.items()
            ]
            for thread in receiver_threads:
                thread.start()

            sender_threads = [
                start_text_thread(
                    stream,
                    iter_text_chunks(STREAM_SPECS[key]["chunks"], delay_seconds=0.5),
                    text_end=True,
                    name=f"tts-sync-send-{key}",
                )
                for key, stream in streams.items()
            ]

            for thread in sender_threads:
                thread.join()
            for thread in receiver_threads:
                thread.join()

            with errors_lock:
                for exc in errors:
                    print("Realtime multiplexed TTS error (keeping partial audio):", exc)
    finally:
        write_outputs(audio_by_stream)
        client.close()


if __name__ == "__main__":
    main()
