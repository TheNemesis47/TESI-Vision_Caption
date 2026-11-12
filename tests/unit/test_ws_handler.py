import asyncio
import base64
from types import SimpleNamespace

import pytest
from fastapi import WebSocketDisconnect

from vision_caption.core.domain.detection import BoundingBox, Detection
from vision_caption.core.domain.hand_pose import Handedness
from vision_caption.core.domain.pointing import (
    HandLandmarks,
    ImagePoint,
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
            state=SimpleNamespace(pipeline_factory=lambda _research: pipeline)
        )

    async def accept(self) -> None:
        self.accepted = True

    async def receive_json(self):
        raise WebSocketDisconnect()

    async def send_json(self, message: dict) -> None:
        self.sent_messages.append(message)


class DisconnectingBeforeConfigWebSocket:
    def __init__(self) -> None:
        self.accepted = False
        self.send_attempts = 0
        self.app = SimpleNamespace(
            state=SimpleNamespace(settings=AppSettings())
        )

    async def accept(self) -> None:
        self.accepted = True

    async def send_json(self, message: dict) -> None:
        self.send_attempts += 1
        raise WebSocketDisconnect(code=1006)


class OverlayPipeline(FakePipeline):
    async def process(
        self,
        frame,
        *,
        on_detections,
        on_pointing_overlay,
        on_stop_audio=None,
        on_mode_switch=None,
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
            (
                HandLandmarks(
                    handedness=Handedness.RIGHT,
                    landmarks=tuple(
                        ImagePoint(x=0.5, y=0.5) for _ in range(21)
                    ),
                ),
            ),
        )
        if False:
            yield


class ModeSwitchPipeline(FakePipeline):
    """Una pipeline che riconosce il gesto e chiede al telefono di cambiare."""

    async def process(
        self,
        frame,
        *,
        on_detections,
        on_pointing_overlay,
        on_stop_audio=None,
        on_mode_switch=None,
    ):
        from vision_caption.core.domain.frame import CaptionMode

        await on_mode_switch(CaptionMode.POINTING, frame.frame_id)
        if False:
            yield


class DetectionPipeline(FakePipeline):
    async def process(
        self,
        frame,
        *,
        on_detections,
        on_pointing_overlay,
        on_stop_audio=None,
        on_mode_switch=None,
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
                pipeline_factory=lambda _research: pipeline,
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
async def test_disconnect_before_stream_config_is_handled() -> None:
    websocket = DisconnectingBeforeConfigWebSocket()

    await vision_websocket(websocket)

    assert websocket.accepted
    assert websocket.send_attempts == 1


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
    assert message["hands"] == [
        {
            "handedness": "RIGHT",
            "landmarks": [{"x": 0.5, "y": 0.5}] * 21,
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
        "modes": [],
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


@pytest.mark.asyncio
async def test_websocket_tells_the_phone_to_change_mode_after_the_gesture() -> None:
    pipeline = ModeSwitchPipeline()
    websocket = OneFrameWebSocket(pipeline)

    await vision_websocket(websocket)

    switch = next(
        item for item in websocket.sent_messages if item["type"] == "mode_switch"
    )
    assert switch["mode"] == "POINTING"
    assert switch["frame_id"] == 42
    # Il telefono deve anche sapere a che ritmo mandare i frame della nuova
    # modalità: POINTING vuole dieci al secondo, AUTO due.
    assert switch["min_frame_interval_ms"] == 100


# --------------------------------------------------------------- preferenze


class PreferencePipeline(FakePipeline):
    """Una pipeline che ricorda cosa le è stato chiesto di cambiare."""

    def __init__(self) -> None:
        super().__init__()
        self.applied: list[object] = []

    def apply_preferences(self, preferences):
        self.applied.append(preferences)
        return {
            key: value
            for key, value in (
                ("max_words", preferences.max_words),
                ("min_interval_seconds", preferences.min_interval_seconds),
            )
            if value is not None
        }

    async def process(self, frame, **_kwargs):
        if False:
            yield None


class PreferenceWebSocket:
    """Due fotogrammi con le stesse preferenze, poi la chiusura."""

    def __init__(
        self,
        pipeline: FakePipeline,
        preferences: dict | None,
        *,
        modes: list[dict] | None = None,
        second_preferences: dict | None = None,
        factory=None,
    ) -> None:
        self.accepted = False
        self.sent_messages: list[dict] = []
        self._calls = 0
        self._preferences = preferences
        self._second = second_preferences if second_preferences is not None else preferences
        self.app = SimpleNamespace(
            state=SimpleNamespace(
                pipeline_factory=factory or (lambda _research, context=None: pipeline),
                settings=AppSettings(),
                available_modes=modes if modes is not None else [],
            )
        )

    async def accept(self) -> None:
        self.accepted = True

    def _frame(self, frame_id: int, preferences: dict | None) -> dict:
        frame = {
            "frame_id": frame_id,
            "image": base64.b64encode(b"jpeg").decode("ascii"),
            "caption_mode": "AUTO",
            "pointing_coordinates": None,
        }
        if preferences is not None:
            frame["preferences"] = preferences
        return frame

    async def receive_json(self):
        self._calls += 1
        if self._calls == 1:
            return self._frame(1, self._preferences)
        if self._calls == 2:
            raise asyncio.TimeoutError()
        if self._calls == 3:
            return self._frame(2, self._second)
        if self._calls == 4:
            raise asyncio.TimeoutError()
        raise WebSocketDisconnect()

    async def send_json(self, message: dict) -> None:
        self.sent_messages.append(message)


@pytest.mark.asyncio
async def test_le_modalita_del_server_arrivano_al_telefono() -> None:
    modes = [{"id": "lesson", "label": "Lezione"}]
    websocket = PreferenceWebSocket(PreferencePipeline(), None, modes=modes)

    await vision_websocket(websocket)

    # Un elenco scritto a mano nel client sarebbe vecchio il giorno dopo.
    assert websocket.sent_messages[0]["modes"] == modes


@pytest.mark.asyncio
async def test_le_preferenze_del_fotogramma_arrivano_alla_pipeline() -> None:
    pipeline = PreferencePipeline()
    websocket = PreferenceWebSocket(
        pipeline, {"max_words": 25, "min_interval_seconds": 20}
    )

    await vision_websocket(websocket)

    assert [
        (item.max_words, item.min_interval_seconds) for item in pipeline.applied
    ] == [(25, 20.0)]


@pytest.mark.asyncio
async def test_le_stesse_preferenze_su_ogni_fotogramma_non_rifanno_il_lavoro() -> None:
    # Viaggiano su ogni fotogramma per sopravvivere allo svuotamento della
    # coda: applicarle due volte al secondo sarebbe spreco.
    pipeline = PreferencePipeline()
    websocket = PreferenceWebSocket(pipeline, {"max_words": 25})

    await vision_websocket(websocket)

    assert len(pipeline.applied) == 1


@pytest.mark.asyncio
async def test_una_preferenza_cambiata_a_sessione_aperta_vale_subito() -> None:
    pipeline = PreferencePipeline()
    websocket = PreferenceWebSocket(
        pipeline,
        {"max_words": 25},
        second_preferences={"max_words": 90},
    )

    await vision_websocket(websocket)

    assert [item.max_words for item in pipeline.applied] == [25, 90]


@pytest.mark.asyncio
async def test_cambiare_modalita_rifa_la_pipeline_invece_di_mutarla() -> None:
    prima = PreferencePipeline()
    dopo = PreferencePipeline()
    costruite: list[str | None] = []

    def factory(_research, context=None):
        costruite.append(context)
        return dopo if context == "museum" else prima

    websocket = PreferenceWebSocket(
        prima,
        None,
        modes=[{"id": "museum", "label": "Museo"}],
        second_preferences={"mode": "museum"},
        factory=factory,
    )

    await vision_websocket(websocket)

    # Una modalità diversa è un altro mondo: la memoria di ciò che era stato
    # descritto con le regole di prima non deve sopravvivere.
    assert costruite == [None, "museum"]


@pytest.mark.asyncio
async def test_una_modalita_che_il_server_non_ha_viene_ignorata() -> None:
    pipeline = PreferencePipeline()
    costruite: list[str | None] = []

    def factory(_research, context=None):
        costruite.append(context)
        return pipeline

    websocket = PreferenceWebSocket(
        pipeline,
        {"mode": "pescheria"},
        modes=[{"id": "lesson", "label": "Lezione"}],
        factory=factory,
    )

    await vision_websocket(websocket)

    # Il telefono può avere un elenco più vecchio: la sessione continua.
    assert costruite == [None]
