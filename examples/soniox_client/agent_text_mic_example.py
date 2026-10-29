# Needs a microphone, speakers and `pip install sounddevice`.
import queue
import threading
from collections.abc import Iterator

import sounddevice as sd

from soniox.client import SonioxClient
from soniox.realtime import RealtimeSTTSession
from soniox.types import RealtimeSTTConfig, RealtimeTTSConfig, Token
from soniox.utils import render_tokens, start_audio_thread

MODEL = "stt-rt-v6"  # a model whose Model.supports_agent_text_input is true
TTS_MODEL = "tts-rt-v2"
VOICE = "Adrian"

SAMPLE_RATE = 24000
BLOCK_SIZE = 1920  # 40ms of 16-bit mono at 24 kHz

AGENT_REPLY = "We have a flat white and a cortado today. Which one would you like?"

# The loop every voice agent has: the microphone stays open while the agent
# talks out loud. Two separate things keep the agent out of the transcript.
#
# Echo cancellation removes the agent's voice from the microphone signal. Python
# has none of its own - it belongs to the platform, so set it up there: a headset
# with hardware AEC, or on Linux `pactl load-module module-echo-cancel` and
# record from the resulting source.
#
# Agent text covers what cancellation cannot: cancellation is never perfect, and
# the user will often repeat the agent's words back ("the cortado, please").
# Telling Soniox what the agent said handles both - those words are recognized
# when the user says them, and the leaked copy is not transcribed as the user.
#
# Soniox places agent text by where it sits among the audio frames, so send each
# piece as it plays. Realtime Text-to-Speech gives the alignment for free with
# return_timestamps: every chunk arrives with the characters it covers, so the
# chunk just written to the speaker and its text belong together.


def microphone_chunks(stop: threading.Event) -> Iterator[bytes]:
    """Yield microphone audio until `stop` is set."""
    mic_queue: queue.Queue[bytes] = queue.Queue()

    def on_audio(indata, _frames, _time, _status) -> None:
        mic_queue.put(bytes(indata))

    with sd.RawInputStream(
        samplerate=SAMPLE_RATE,
        blocksize=BLOCK_SIZE,
        channels=1,
        dtype="int16",
        callback=on_audio,
    ):
        while not stop.is_set():
            try:
                yield mic_queue.get(timeout=0.1)
            except queue.Empty:
                continue


def speak(client: SonioxClient, session: RealtimeSTTSession, text: str) -> None:
    """Say `text` out loud, sending each chunk's words once they have been heard."""
    config = RealtimeTTSConfig(
        model=TTS_MODEL,
        voice=VOICE,
        language="en",
        audio_format="pcm_s16le",
        sample_rate=SAMPLE_RATE,
        return_timestamps=True,
    )
    with (
        client.realtime.tts.connect(config=config) as tts,
        sd.RawOutputStream(
            samplerate=SAMPLE_RATE, blocksize=BLOCK_SIZE, channels=1, dtype="int16"
        ) as speaker,
    ):
        tts.send_text_chunks(text)
        for event in tts.receive_events():
            chunk = event.audio_bytes()
            if chunk is None:
                continue
            # write() blocks until the speaker has taken the audio, so the text
            # goes out after it was heard rather than when it was generated.
            speaker.write(chunk)
            spoken = "".join(event.timestamps.characters) if event.timestamps else ""
            session.send_agent_text(spoken, end_of_segment=False)

    # An empty text closes the segment. Do this when the voice stops, including
    # when the user barged in - then only the text they actually heard was sent.
    session.send_agent_text("")


def main() -> None:
    client = SonioxClient()
    config = RealtimeSTTConfig(
        model=MODEL,
        audio_format="pcm_s16le",
        sample_rate=SAMPLE_RATE,
        num_channels=1,
        language_hints=["en"],
        enable_endpoint_detection=True,
        enable_agent_text_input=True,
    )
    final_tokens: list[Token] = []
    non_final_tokens: list[Token] = []
    stop = threading.Event()

    with client.realtime.stt.connect(config=config) as session:
        start_audio_thread(session, microphone_chunks(stop), name="soniox-mic")
        threading.Thread(
            target=speak, args=(client, session, AGENT_REPLY), name="soniox-agent", daemon=True
        ).start()
        print("Listening. Say the agent's words back to it, then press Ctrl+C.")
        try:
            for event in session.receive_events():
                for token in event.tokens:
                    if token.is_final:
                        final_tokens.append(token)
                    else:
                        non_final_tokens.append(token)

                print(render_tokens(final_tokens, non_final_tokens))
                non_final_tokens.clear()
        except KeyboardInterrupt:
            pass
        finally:
            stop.set()


if __name__ == "__main__":
    main()
