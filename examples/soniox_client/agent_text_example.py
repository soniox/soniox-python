import threading
import time
from pathlib import Path

from soniox.client import SonioxClient
from soniox.errors import SonioxRealtimeError
from soniox.realtime import RealtimeSTTSession
from soniox.types import TOKEN_TEXT_END, RealtimeSTTConfig, RealtimeTTSConfig
from soniox.utils import throttle_audio

DEMO_FILE = Path(__file__).resolve().parents[2] / "assets" / "package_lookup.mp3"
POST_ID = "235235"  # your model would pull this out of the transcript as a tool call
USERS = {"235235": "John Döe"}  # stands in for your database
LLM_LATENCY_SEC = 0.8  # your model will not answer instantly either


def stream_caller_audio(session: RealtimeSTTSession) -> None:
    """Stream the caller's clip at the pace it was spoken: 4096 bytes of it is 510ms.

    Soniox places agent text by where it sits among the audio frames, so pace
    matters. `send_bytes` would end the session as soon as the clip ran out,
    before the agent has finished replying, so the chunks go in one at a time.
    """
    for chunk in throttle_audio(DEMO_FILE, chunk_size_bytes=4096, delay_seconds=0.51):
        session.send_byte_chunk(chunk)


def speak_agent_reply(client: SonioxClient, session: RealtimeSTTSession, text: str) -> None:
    """Say `text` out loud, feeding each piece back into Speech-to-Text."""
    config = RealtimeTTSConfig(
        stream_id="agent-reply",
        model="tts-rt-v2",
        voice="Adrian",
        language="en",
        audio_format="pcm_s16le",
        sample_rate=24000,
        return_timestamps=True,
    )
    try:
        with client.realtime.tts.connect(config=config) as tts:
            tts.send_text_chunks(text)
            for event in tts.receive_events():
                if event.timestamps:
                    spoken = "".join(event.timestamps.characters)
                    session.send_agent_text(spoken)
                    print(f"agent_text_input: {spoken!r}")
        session.send_agent_text("", end_of_segment=True)
        print("agent_text_input: end of turn")
    except SonioxRealtimeError as exc:
        print(f"agent_text_input: failed: {exc}")


def answer_caller(client: SonioxClient, session: RealtimeSTTSession, heard: str) -> None:
    """Look up the package the caller asked about and say what we found."""
    print(f"caller: {heard.strip()}")
    user = USERS[POST_ID]
    print(f"lookup: {POST_ID} -> {user}")
    time.sleep(LLM_LATENCY_SEC)
    reply = f"Hi {user}, your package is out for delivery."  # your model
    print(f"llm: {reply}")
    speak_agent_reply(client, session, reply)
    session.finish()


def main() -> None:
    client = SonioxClient()
    config = RealtimeSTTConfig(
        model="stt-rt-v6",  # a model whose Model.supports_agent_text_input is true
        audio_format="mp3",
        enable_endpoint_detection=True,
        enable_agent_text_input=True,
    )
    with client.realtime.stt.connect(config=config) as session:
        threading.Thread(
            target=stream_caller_audio, args=(session,), name="soniox-caller"
        ).start()

        heard = ""
        for event in session.receive_events():
            for token in event.tokens:
                if token.text == TOKEN_TEXT_END:  # the caller stopped talking
                    answer_caller(client, session, heard)
                    heard = ""
                elif token.is_final:
                    heard += token.text


if __name__ == "__main__":
    main()
