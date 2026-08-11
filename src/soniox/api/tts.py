from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, BinaryIO

from ..types import CreateTtsConfig, TtsAudioFormat, TtsBitrate, TtsSampleRate
from ._utils import build_tts_payload, ensure_success

if TYPE_CHECKING:
    from ..client import SonioxClient


DEFAULT_MODEL = "tts-rt-v2"
DEFAULT_VOICE = "Adrian"


class TtsAPI:
    def __init__(self, client: SonioxClient) -> None:
        self._client = client

    def generate(
        self,
        *,
        text: str,
        voice: str,
        model: str = DEFAULT_MODEL,
        config: CreateTtsConfig | None = None,
        language: str | None = None,
        audio_format: TtsAudioFormat | None = None,
        sample_rate: TtsSampleRate | None = None,
        bitrate: TtsBitrate | None = None,
    ) -> bytes:
        """
        Generate speech audio from text and return raw audio bytes.

        Performs a POST request to the Text-to-Speech REST endpoint.

        ``audio_format``/``sample_rate``/``bitrate`` are deprecated; set them on
        ``CreateTtsConfig`` instead. Pass ``language`` explicitly — relying on the default
        ("en") is deprecated and ``language`` will be required in the next major release.

        Raises:
            SonioxAPIError: When the API returns an error.
        """
        payload = build_tts_payload(
            text=text,
            voice=voice,
            model=model,
            config=config,
            language=language,
            audio_format=audio_format,
            sample_rate=sample_rate,
            bitrate=bitrate,
        )
        response = self._client.request(
            "POST",
            f"{self._client.tts_api_base_url}/tts",
            json=payload.model_dump(exclude_none=True),
        )
        ensure_success(response)
        return response.content

    def generate_to_file(
        self,
        output: BinaryIO | Path | str,
        *,
        text: str,
        voice: str = DEFAULT_VOICE,
        model: str = DEFAULT_MODEL,
        config: CreateTtsConfig | None = None,
        language: str | None = None,
        audio_format: TtsAudioFormat | None = None,
        sample_rate: TtsSampleRate | None = None,
        bitrate: TtsBitrate | None = None,
    ) -> int:
        """
        Generate speech audio from text and write the audio bytes to a file output.

        ``audio_format``/``sample_rate``/``bitrate`` are deprecated; set them on
        ``CreateTtsConfig`` instead. Pass ``language`` explicitly — relying on the default
        ("en") is deprecated and ``language`` will be required in the next major release.

        Returns:
            Number of bytes written.
        """
        audio = self.generate(
            text=text,
            voice=voice,
            model=model,
            config=config,
            language=language,
            audio_format=audio_format,
            sample_rate=sample_rate,
            bitrate=bitrate,
        )
        if isinstance(output, Path | str):
            path = Path(output)
            path.write_bytes(audio)
            return len(audio)

        return output.write(audio)
