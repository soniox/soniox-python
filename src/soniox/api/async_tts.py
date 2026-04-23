from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, BinaryIO

from ..types import CreateTtsConfig, CreateTtsPayload, TtsAudioFormat, TtsBitrate, TtsSampleRate
from ._utils import ensure_success

if TYPE_CHECKING:
    from ..client import AsyncSonioxClient


DEFAULT_MODEL = "tts-rt-v1-preview"
DEFAULT_VOICE = "Adrian"
DEFAULT_LANGUAGE = "en"
DEFAULT_AUDIO_FORMAT: TtsAudioFormat = "wav"


class AsyncTtsAPI:
    def __init__(self, client: AsyncSonioxClient) -> None:
        self._client = client

    async def generate(
        self,
        *,
        text: str,
        voice: str,
        model: str = DEFAULT_MODEL,
        language: str = DEFAULT_LANGUAGE,
        audio_format: TtsAudioFormat = DEFAULT_AUDIO_FORMAT,
        sample_rate: TtsSampleRate | None = None,
        bitrate: TtsBitrate | None = None,
        config: CreateTtsConfig | None = None,
    ) -> bytes:
        """
        Generate speech audio from text and return raw audio bytes.

        Performs a POST request to the TTS REST endpoint.

        Raises:
            SonioxAPIError: When the API returns an error.
        """
        config_data = config.model_dump(exclude_none=True) if config else {}
        payload_data: dict[str, object | None] = {
            "model": model,
            "language": language,
            "voice": voice,
            "audio_format": audio_format,
            "sample_rate": sample_rate,
            "bitrate": bitrate,
            "text": text,
        }
        payload_data.update(config_data)
        payload = CreateTtsPayload.model_validate(payload_data)
        response = await self._client.request(
            "POST",
            f"{self._client.tts_api_base_url}/tts",
            json=payload.model_dump(exclude_none=True),
        )
        ensure_success(response)
        return response.content

    async def generate_to_file(
        self,
        output: BinaryIO | Path | str,
        *,
        text: str,
        voice: str = DEFAULT_VOICE,
        model: str = DEFAULT_MODEL,
        language: str = DEFAULT_LANGUAGE,
        audio_format: TtsAudioFormat = DEFAULT_AUDIO_FORMAT,
        sample_rate: TtsSampleRate | None = None,
        bitrate: TtsBitrate | None = None,
        config: CreateTtsConfig | None = None,
    ) -> int:
        """
        Generate speech audio from text and write the audio bytes to a file-like output.

        Returns:
            Number of bytes written.
        """
        audio = await self.generate(
            text=text,
            voice=voice,
            model=model,
            language=language,
            audio_format=audio_format,
            sample_rate=sample_rate,
            bitrate=bitrate,
            config=config,
        )
        if isinstance(output, Path | str):
            path = Path(output)
            path.write_bytes(audio)
            return len(audio)

        written = output.write(audio)
        return written if written is not None else len(audio)
