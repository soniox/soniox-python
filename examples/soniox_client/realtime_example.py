from pathlib import Path

from soniox.client import SonioxClient
from soniox.types import RealtimeSTTConfig, Token
from soniox.utils import render_tokens, start_audio_thread, throttle_audio

DEMO_FILE = Path(__file__).resolve().parents[2] / "assets" / "coffee_shop.mp3"


def main() -> None:
    client = SonioxClient()
    config = RealtimeSTTConfig(model="stt-rt-v4", audio_format="mp3")
    final_tokens: list[Token] = []
    non_final_tokens: list[Token] = []
    with client.realtime.stt.connect(config=config) as session:
        start_audio_thread(session, throttle_audio(DEMO_FILE, delay_seconds=0.1))
        for event in session.receive_events():
            for token in event.tokens:
                if token.is_final:
                    final_tokens.append(token)
                else:
                    non_final_tokens.append(token)

            print(render_tokens(final_tokens, non_final_tokens))
            non_final_tokens.clear()
    # The last_message memo retains the most recent event if you need to inspect it later.
    print("Captured final message:", session.last_message)


main()
