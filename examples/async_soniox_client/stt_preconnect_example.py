"""
STT internal connection pool (default).

``AsyncSonioxClient()`` keeps up to 5 idle WebSocket links warm by default.
``connect(config=...)`` uses the pool transparently.

Idle pool links:
- Sit in the pool until **borrowed**; borrow removes the record immediately
- If the pool is empty at borrow time, the SDK opens a WebSocket **now**
- After borrow, the pool refills in the background up to ``pool_size``
- Send periodic STT keepalive (``{"type": "keepalive"}``) every 5 seconds
- Maximum lifetime default 10 minutes, refreshed proactively before expiry

Session links (after ``connect(config=...)``):
- Leave the idle pool permanently when a session starts
- Are **discarded (closed) when the session ends** — never reused
- The pool opens a fresh idle replacement in the background

Configure on the client:

    AsyncSonioxClient(
        stt_connection_pool_size=5,       # default
        stt_idle_max_lifetime_sec=600,      # 10 minutes
        stt_idle_refresh_before_sec=60,     # rebuild when <= 1 min left
    )

Set ``stt_connection_pool_size=0`` to disable pooling.
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator

from soniox.client import AsyncSonioxClient
from soniox.types import RealtimeSTTConfig
from soniox.utils import render_tokens

CONFIG = RealtimeSTTConfig(model="stt-rt-v4", audio_format="ogg")


async def fake_client_packets() -> AsyncIterator[bytes]:
    pages = [b"OggS-head", b"OggS-tags", b"OggS-audio-1", b"OggS-audio-2"]
    for page in pages:
        await asyncio.sleep(0.06)
        yield page


async def main() -> None:
    async with AsyncSonioxClient(
        stt_idle_max_lifetime_sec=600,
        stt_idle_refresh_before_sec=60,
    ) as client:
        await client.realtime.stt.warmup_connection_pool()

        async with client.realtime.stt.connect(config=CONFIG) as session:
            async for packet in fake_client_packets():
                await session.send_byte_chunk(packet)

            await session.finish()

            final: list = []
            non_final: list = []
            async for event in session.receive_events():
                for token in event.tokens:
                    (final if token.is_final else non_final).append(token)
                print(render_tokens(final, non_final))
                non_final.clear()
                if event.finished:
                    break


if __name__ == "__main__":
    asyncio.run(main())
