import os

import soniox
from soniox.types.api import CreateTranscriptionPayload, File
from soniox.types.common import Token
from soniox.types.realtime import RealtimeEvent, RealtimeSttConfig
from soniox.utils import render_tokens, start_audio_thread, throttle_audio

webhook_url = "https://unborne-katharyn-subconformably.ngrok-free.dev/webhook"
webhook_secret = "my_super_secret_123"

api_key = os.environ["SONIOX_API_KEY"]
bad_client = soniox.SonioxClient(api_key="bad_key")
sync_client = soniox.SonioxClient(webhook_secret=webhook_secret)
async_client = soniox.AsyncSonioxClient(webhook_secret=webhook_secret)

rt_config = RealtimeSttConfig(model="stt-rt-v3", language_hints=["en"])

f1 = sync_client.files.upload("assets/coffee_shop.mp3")
f2 = sync_client.files.upload("assets/coffee_shop.mp3")


def create_payload(file: File):
    return CreateTranscriptionPayload(
        model="stt-async-v3",
        file_id=file.id,
        language_hints=["en"],
    )


t1 = sync_client.transcriptions.create(file_id=f1.id)
t2 = sync_client.transcriptions.create(file_id=f2.id)


def stt_rt_1():
    final_tokens: list[Token] = []
    non_final_tokens: list[Token] = []
    with sync_client.realtime.stt.connect(config=rt_config) as session:
        start_audio_thread(session, throttle_audio("assets/coffee_shop.mp3", delay_seconds=0.1))
        for event in session.receive_events():
            for token in event.tokens:
                if token.is_final:
                    final_tokens.append(token)
                else:
                    non_final_tokens.append(token)

            print(render_tokens(final_tokens, non_final_tokens))
            non_final_tokens.clear()


def stt_rt_2():
    def handler(event: RealtimeEvent):
        if event.finished:
            print(f"event: {event}")

    with sync_client.realtime.stt.connect(config=rt_config) as session:
        start_audio_thread(session, throttle_audio("assets/coffee_shop.mp3", delay_seconds=0.1))
        session.on_open(lambda payload: print("OPEN1", payload.session))
        session.on_open(lambda payload: print("OPEN2", payload.type))
        session.on_close(lambda payload: print("close", payload.session))
        session.on_error(lambda payload: print("error", payload.error))
        session.on_message(lambda payload: print("message token count", len(payload.event.tokens)))
        session.handle_events(handler)


def stt_rt_3():
    def handler(event: RealtimeEvent):
        if event.finished:
            print("final transcript ready", event)

    with sync_client.realtime.stt.connect(config=rt_config) as session:
        start_audio_thread(session, throttle_audio("assets/coffee_shop.mp3", delay_seconds=0.2))
        session.on_open(lambda payload: print("on_open helper ->", payload))
        session.on_close(lambda payload: print("on_close helper ->", payload))
        session.on_message(lambda payload: print("on_message helper ->", len(payload.event.tokens)))
        session.on_error(lambda payload: print("on_error helper ->", payload.error))
        session.on_finished(lambda payload: print("on_finished helper ->", payload.event))

        session.handle_events(handler)
