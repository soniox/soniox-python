import time
from pathlib import Path

from soniox.client import SonioxClient
from soniox.types import RealtimeSTTConfig, Token
from soniox.utils import render_tokens, start_audio_thread, throttle_audio

DEMO_FILE = Path(__file__).resolve().parents[2] / "assets" / "coffee_shop.mp3"
MODEL = "stt-rt-v6"  # a model whose Model.supports_agent_text_input is true

# What the agent says while the user's audio keeps streaming. In a real agent
# this is your Text-to-Speech output, sent as it plays rather than when it was
# generated: Soniox places agent text by its position among the audio frames,
# so text sent early lands in the wrong place. Our own realtime Text-to-Speech
# gives you the alignment for free - each event's `timestamps.characters` are
# the characters of that audio chunk, so sending them as you hand the chunk to
# the speaker is both correctly timed and the text that was really spoken.
AGENT_REPLY = ["We have a flat white", " and a cortado today."]
SPEAKING_PACE_SEC = 0.6


def main() -> None:
    client = SonioxClient()
    config = RealtimeSTTConfig(model=MODEL, audio_format="mp3", enable_agent_text_input=True)
    final_tokens: list[Token] = []
    non_final_tokens: list[Token] = []
    with client.realtime.stt.connect(config=config) as session:
        start_audio_thread(session, throttle_audio(DEMO_FILE, delay_seconds=0.1))

        for part in AGENT_REPLY:
            # end_of_segment=False while the reply is still being spoken.
            session.send_agent_text(part, end_of_segment=False)
            time.sleep(SPEAKING_PACE_SEC)
        # An empty text closes the segment. Do this when the voice stops, including
        # when the user barged in - then only the text they actually heard was sent.
        session.send_agent_text("")

        for event in session.receive_events():
            for token in event.tokens:
                if token.is_final:
                    final_tokens.append(token)
                else:
                    non_final_tokens.append(token)

            print(render_tokens(final_tokens, non_final_tokens))
            non_final_tokens.clear()


if __name__ == "__main__":
    main()
