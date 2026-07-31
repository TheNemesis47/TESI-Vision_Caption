import asyncio
import base64
from types import SimpleNamespace

import pytest
from fastapi import WebSocketDisconnect

from vision_caption.core.domain.hand_pose import Handedness
from vision_caption.core.domain.pointing import (
    NormalizedPoint,
    PointingOverlay,
    PointingOverlayState,
    PointingRay,
)
from vision_caption.infrastructure.settings import AppSettings
from vision_caption.infrastructure.server.ws_handler import vision_websocket


class FakePipeline:
    def __init__(self) -> None:
        self.closed = False

    async def close(self) -> None:
        self.closed = True


class DisconnectingWebSocket:
    def __init__(self, pipeline: FakePipeline) -> None:
        self.accepted = False
        self.app = SimpleNamespace(
            state=SimpleNamespace(pipeline_factory=lambda: pipeline)
        )

    async def accept(self) -> None:
        self.accepted = True

    async def receive_json(self):
        raise WebSocketDisconnect()


class OverlayPipeline(FakePipeline):
    async def process(
        self,
        frame,
        *,
        on_detections,
        on_pointing_overlay,
    ):
        await on_pointing_overlay(
            (
                PointingOverlay(
                    handedness=Handedness.RIGHT,
                    ray=PointingRay(
                        start=NormalizedPoint(x=0.25, y=0.5),
                        end=NormalizedPoint(x=1.0, y=0.25),
                    ),
                    state=PointingOverlayState.ACTIVE,
                    confirmation_progress=1.0,
                ),
            ),
            frame.frame_id,
        )
        if False:
            yield


class OneFrameWebSocket:
    def __init__(self, pipeline: OverlayPipeline) -> None:
        self.accepted = False
        self.sent_messages: list[dict] = []
        self._receive_calls = 0
        self.app = SimpleNamespace(
            state=SimpleNamespace(
                pipeline_factory=lambda: pipeline,
                settings=AppSettings(),
            )
        )

    async def accept(self) -> None:
        self.accepted = True

    async def receive_json(self):
        self._receive_calls += 1
        if self._receive_calls == 1:
            return {
                "frame_id": 42,
                "image": base64.b64encode(b"jpeg").decode("ascii"),
                "caption_mode": "POINTING",
                "pointing_coordinates": None,
            }
        if self._receive_calls == 2:
            raise asyncio.TimeoutError()
        raise WebSocketDisconnect()

    async def send_json(self, message: dict) -> None:
        self.sent_messages.append(message)


@pytest.mark.asyncio
async def test_websocket_disconnect_closes_session_pipeline() -> None:
    pipeline = FakePipeline()
    websocket = DisconnectingWebSocket(pipeline)

    await vision_websocket(websocket)

    assert websocket.accepted
    assert pipeline.closed


@pytest.mark.asyncio
async def test_websocket_sends_normalized_pointing_overlay_message() -> None:
    pipeline = OverlayPipeline()
    websocket = OneFrameWebSocket(pipeline)

    await vision_websocket(websocket)

    assert websocket.accepted
    assert pipeline.closed
    assert len(websocket.sent_messages) == 1
    message = websocket.sent_messages[0]
    assert message["type"] == "pointing_overlay"
    assert message["frame_id"] == 42
    assert message["overlays"] == [
        {
            "handedness": "RIGHT",
            "ray": {
                "start": {"x": 0.25, "y": 0.5},
                "end": {"x": 1.0, "y": 0.25},
            },
            "state": "ACTIVE",
            "confirmation_progress": 1.0,
        }
    ]
    assert message["corridor"]["coordinate_space"] == "normalized"
    assert message["corridor"]["width_reference"] == "short_side"
    assert message["corridor"]["color"] == "#FFFF00"
