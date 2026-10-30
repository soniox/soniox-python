import asyncio
from pathlib import Path

from soniox.client import AsyncSonioxClient
from soniox.errors import SonioxRealtimeError
from soniox.realtime.async_stt import AsyncRealtimeSTTSession
from soniox.types import TOKEN_TEXT_END, RealtimeSTTConfig, RealtimeTTSConfig
from soniox.utils import throttle_audio_async

DEMO_FILE = Path(__file__).resolve().parents[2] / "assets" / "package_lookup.mp3"
POST_ID = "235235"  # your model would pull this out of the transcript as a tool call
USERS = {"235235": "John Döe"}  # stands in for your database
LLM_LATENCY_SEC = 0.8  # your model will not answer instantly either


async def stream_caller_audio(session: AsyncRealtimeSTTSession) -> None:
    """Stream the caller's clip at the pace it was spoken: 4096 bytes of it is 510ms.

    Soniox places agent text by where it sits among the audio frames, so pace
    matters. `send_bytes` would end the session as soon as the clip ran out,
    before the agent has finished replying, so the chunks go in one at a time.
    """
    async for chunk in throttle_audio_async(DEMO_FILE, chunk_size_bytes=4096, delay_seconds=0.51):
        await session.send_byte_chunk(chunk)


async def speak_agent_reply(
    client: AsyncSonioxClient, session: AsyncRealtimeSTTSession, text: str
) -> None:
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
        async with client.realtime.tts.connect(config=config) as tts:
            await tts.send_text_chunks(text)
            async for event in tts.receive_events():
                if event.timestamps:
                    spoken = "".join(event.timestamps.characters)
                    await session.send_agent_text(spoken)
                    print(f"agent_text_input: {spoken!r}")
        await session.send_agent_text("", end_of_segment=True)
        print("agent_text_input: end of turn")
    except SonioxRealtimeError as exc:
        print(f"agent_text_input: failed: {exc}")


async def answer_caller(
    client: AsyncSonioxClient, session: AsyncRealtimeSTTSession, heard: str
) -> None:
    """Look up the package the caller asked about and say what we found."""
    print(f"caller: {heard.strip()}")
    user = USERS[POST_ID]
    print(f"lookup: {POST_ID} -> {user}")
    await asyncio.sleep(LLM_LATENCY_SEC)
    reply = f"Hi {user}, your package is out for delivery."  # your model
    print(f"llm: {reply}")
    await speak_agent_reply(client, session, reply)
    await session.finish()


async def main() -> None:
    client = AsyncSonioxClient()
    config = RealtimeSTTConfig(
        model="stt-rt-v6",  # a model whose Model.supports_agent_text_input is true
        audio_format="mp3",
        enable_endpoint_detection=True,
        enable_agent_text_input=True,
    )
    async with client.realtime.stt.connect(config=config) as session:
        asyncio.create_task(stream_caller_audio(session))

        heard = ""
        async for event in session.receive_events():
            for token in event.tokens:
                if token.text == TOKEN_TEXT_END:  # the caller stopped talking
                    await answer_caller(client, session, heard)
                    heard = ""
                elif token.is_final:
                    heard += token.text


asyncio.run(main())
