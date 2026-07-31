import json

import httpx
import pytest

from vision_caption.adapters.vlm.OpenRouterPointingCaptionGenerator import (
    OpenRouterPointingCaptionGenerator,
    build_pointing_payload,
    parse_pointing_caption,
)
from vision_caption.core.domain.hand_pose import Handedness
from vision_caption.core.domain.pointing import (
    NormalizedPoint,
    PointingEvent,
    PointingRay,
)
from vision_caption.core.ports.pointing_image_preparer_port import PointingImages


def _event() -> PointingEvent:
    return PointingEvent(
        handedness=Handedness.LEFT,
        ray=PointingRay(
            start=NormalizedPoint(x=0.4, y=0.6),
            end=NormalizedPoint(x=1.0, y=0.2),
        ),
        frame_id=12,
    )


def _images() -> PointingImages:
    return PointingImages(
        context_jpeg=b"context",
        focus_jpeg=b"focus",
        clean_jpeg=b"clean",
    )


def _caption_payload() -> dict:
    return {
        "target": "scatola",
        "description": "Una scatola blu.",
        "visible_text": "FRAGILE",
        "text_confidence": 0.9,
        "text_complete": True,
        "confidence": 0.95,
        "candidates": [],
        "alternatives": [],
        "needs_repointing": False,
        "needs_closer_view": False,
    }


def test_payload_contains_prompt_and_three_images() -> None:
    payload = build_pointing_payload(
        event=_event(),
        images=_images(),
        model_name="test-model",
        max_tokens=500,
    )
    content = payload["messages"][0]["content"]

    assert payload["response_format"] == {"type": "json_object"}
    assert sum(item["type"] == "image_url" for item in content) == 3
    assert any(
        item["type"] == "text" and "mano rilevata: LEFT" in item["text"]
        for item in content
    )


def test_parser_validates_json_and_rejects_invalid_content() -> None:
    parsed = parse_pointing_caption(
        f"```json\n{json.dumps(_caption_payload())}\n```"
    )

    assert parsed is not None
    assert parsed.target == "scatola"
    assert parse_pointing_caption("non-json") is None


@pytest.mark.asyncio
async def test_generator_returns_validated_caption() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        request_payload = json.loads(request.content)
        assert len(request_payload["messages"][0]["content"]) == 7
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "finish_reason": "stop",
                        "message": {
                            "content": json.dumps(_caption_payload())
                        },
                    }
                ]
            },
        )

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler)
    ) as client:
        generator = OpenRouterPointingCaptionGenerator(
            api_key="test-key",
            model_name="test-model",
            client=client,
        )
        caption = await generator.generate(_event(), _images())

    assert caption is not None
    assert caption.description == "Una scatola blu."
