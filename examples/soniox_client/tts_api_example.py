from soniox.client import SonioxClient
from soniox.errors import SonioxAPIError
from soniox.types import TtsAudioFormat
from soniox.utils import output_file_for_audio_format

MODEL = "tts-rt-v1"
LANGUAGE = "en"
VOICE = "Adrian"
AUDIO_FORMAT: TtsAudioFormat = "wav"


def main() -> None:
    client = SonioxClient()
    output_file = output_file_for_audio_format(AUDIO_FORMAT, "tts_sync")
    try:
        written = client.tts.generate_to_file(
            output_file,
            text=(
                "Soniox Text-to-Speech turns written text into natural, expressive audio "
                "with high accuracy. It is designed for conversational agents, narration, "
                "and accessible experiences, with low latency and high-quality voices."
            ),
            model=MODEL,
            language=LANGUAGE,
            voice=VOICE,
            audio_format=AUDIO_FORMAT,
        )
        print(f"Wrote {written} bytes to {output_file.resolve()}")
    except SonioxAPIError as exc:
        print("Soniox API error:", exc)
        if exc.request_id:
            print("  request_id:", exc.request_id)
    finally:
        client.close()


if __name__ == "__main__":
    main()
