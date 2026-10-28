import io
import json
import wave

import httpx
import pytest

from vision_caption.adapters.tts import FishSpeechSynthesizer as module
from vision_caption.adapters.tts.FishSpeechSynthesizer import (
    FishSpeechSynthesizer,
)
from vision_caption.core.domain.audio import AudioFormat


def _wav(seconds: float, rate: int = 44_100) -> bytes:
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(rate)
        audio.writeframes(b"\x00\x00" * int(seconds * rate))
    return buffer.getvalue()


@pytest.mark.asyncio
async def test_sends_the_text_with_a_fixed_voice_and_measures_the_audio(
    monkeypatch,
) -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, content=_wav(1.5))

    real_client = httpx.AsyncClient
    monkeypatch.setattr(
        module.httpx,
        "AsyncClient",
        lambda: real_client(transport=httpx.MockTransport(handler)),
    )
    synthesizer = FishSpeechSynthesizer("http://fish:8080/", seed=7)

    audio = await synthesizer.synthesize("Una sedia davanti a te.")

    (request,) = requests
    assert str(request.url) == "http://fish:8080/v1/tts"
    body = json.loads(request.content)
    assert body["text"] == "Una sedia davanti a te."
    assert body["format"] == "wav"
    assert body["seed"] == 7
    assert body["reference_id"] is None
    assert audio.audio_format == AudioFormat.WAV
    assert audio.audio_duration == pytest.approx(1.5)
