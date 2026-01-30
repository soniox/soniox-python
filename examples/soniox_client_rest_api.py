import soniox
from soniox.types.api import CreateTranscriptionPayload, File

client = soniox.SonioxClient()

f1 = client.files.upload("assets/coffee_shop.mp3")
f2 = client.files.upload("assets/coffee_shop.mp3")


def create_payload(file: File):
    return CreateTranscriptionPayload(
        file_id=file.id,
        language_hints=["en"],
    )


t1 = client.transcriptions.create(file_id=f1.id)

t2 = client.transcriptions.transcribe_and_wait(file_id=f2.id)
t3 = client.transcriptions.transcribe_and_wait(file="assets/coffee_shop.mp3")

client.transcriptions.get(t1.id)
client.transcriptions.get_transcript(t1.id)

client.files.delete(f1.id)
client.files.delete(f2.id)
if t3.file_id is not None:
    client.files.delete(t3.file_id)
client.transcriptions.delete(t1.id)
client.transcriptions.delete(t2.id)
client.transcriptions.delete(t3.id)
