import asyncio
import base64
from types import SimpleNamespace

import pytest
from fastapi import WebSocketDisconnect

from vision_caption.core.domain.detection import BoundingBox, Detection
from vision_caption.core.domain.hand_pose import Handedness
from vision_caption.core.domain.pointing import (
    NormalizedPoint,
    PointingOverlay,
    PointingOverlayState,
    PointingRay,
)
from vision_caption.infrastructure.settings import AppSettings, ServerSettings
from vision_caption.infrastructure.server.ws_handler import vision_websocket


class FakePipeline:
    def __init__(self) -> None:
        self.closed = False

    async def close(self) -> None:
        self.closed = True


class DisconnectingWebSocket:
    def __init__(self, pipeline: FakePipeline) -> None:
        self.accepted = False
        self.sent_messages: list[dict] = []
        self.app = SimpleNamespace(
            state=SimpleNamespace(pipeline_factory=lambda: pipeline)
        )

    async def accept(self) -> None:
        self.accepted = True

    async def receive_json(self):
        raise WebSocketDisconnect()

    async def send_json(self, message: dict) -> None:
        self.sent_messages.append(message)


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


class DetectionPipeline(FakePipeline):
    async def process(
        self,
        frame,
        *,
        on_detections,
        on_pointing_overlay,
    ):
        await on_detections(
            [
                Detection(
                    class_name="chair",
                    confidence=0.9,
                    bbox=BoundingBox(
                        x_min=0,
                        y_min=0,
                        x_max=10,
                        y_max=10,
                    ),
                )
            ],
            frame.frame_id,
        )
        if False:
            yield


class OneFrameWebSocket:
    def __init__(
        self,
        pipeline: FakePipeline,
        *,
        settings: AppSettings | None = None,
        caption_mode: str = "POINTING",
        slow_message_type: str | None = None,
    ) -> None:
        self.accepted = False
        self.sent_messages: list[dict] = []
        self._receive_calls = 0
        self._caption_mode = caption_mode
        self._slow_message_type = slow_message_type
        self.app = SimpleNamespace(
            state=SimpleNamespace(
                pipeline_factory=lambda: pipeline,
                settings=settings or AppSettings(),
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
                "caption_mode": self._caption_mode,
                "pointing_coordinates": None,
            }
        if self._receive_calls == 2:
            raise asyncio.TimeoutError()
        raise WebSocketDisconnect()

    async def send_json(self, message: dict) -> None:
        if message["type"] == self._slow_message_type:
            await asyncio.sleep(0.05)
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
    assert [item["type"] for item in websocket.sent_messages] == [
        "stream_config",
        "pointing_overlay",
        "frame_done",
    ]
    message = websocket.sent_messages[1]
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


@pytest.mark.asyncio
async def test_websocket_advertises_flow_control_and_acks_frame() -> None:
    pipeline = OverlayPipeline()
    websocket = OneFrameWebSocket(pipeline)

    await vision_websocket(websocket)

    config = websocket.sent_messages[0]
    assert config == {
        "type": "stream_config",
        "protocol_version": 1,
        "fps": {"AUTO": 2.0, "POINTING": 10.0},
        "max_in_flight": 1,
        "max_buffered_amount_bytes": 262_144,
    }
    done = websocket.sent_messages[-1]
    assert done["type"] == "frame_done"
    assert done["frame_id"] == 42
    assert done["min_frame_interval_ms"] == 100
    assert done["processing_ms"] >= 0


@pytest.mark.asyncio
async def test_slow_detection_is_dropped_without_blocking_frame_done() -> None:
    pipeline = DetectionPipeline()
    settings = AppSettings(
        server=ServerSettings(
            websocket_optional_send_timeout_seconds=0.001,
        )
    )
    websocket = OneFrameWebSocket(
        pipeline,
        settings=settings,
        caption_mode="AUTO",
        slow_message_type="detections",
    )

    await vision_websocket(websocket)

    assert [item["type"] for item in websocket.sent_messages] == [
        "stream_config",
        "frame_done",
    ]
    assert websocket.sent_messages[-1]["min_frame_interval_ms"] == 500
