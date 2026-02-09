import asyncio
from pathlib import Path

from soniox.client import AsyncSonioxClient
from soniox.types import RealtimeSTTConfig, Token
from soniox.utils import render_tokens, throttle_audio_async

DEMO_FILE = Path(__file__).resolve().parents[2] / "assets" / "coffee_shop.mp3"


async def main() -> None:
    client = AsyncSonioxClient()
    config = RealtimeSTTConfig(model="stt-rt-v4", audio_format="mp3")
    final_tokens: list[Token] = []
    non_final_tokens: list[Token] = []
    async with client.realtime.stt.connect(config=config) as session:
        await session.send_bytes(throttle_audio_async(DEMO_FILE, delay_seconds=0.1))
        async for event in session.receive_events():
            for token in event.tokens:
                if token.is_final:
                    final_tokens.append(token)
                else:
                    non_final_tokens.append(token)

            print(render_tokens(final_tokens, non_final_tokens))
            non_final_tokens.clear()
    # The last_message memo retains the most recent event if you need to inspect it later.
    print("Captured final message:", session.last_message)


asyncio.run(main())
