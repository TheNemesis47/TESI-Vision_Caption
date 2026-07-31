from vision_caption.core.services.pointing.pointing_event_gate import (
    PointingEventGate,
)


def test_event_gate_applies_cooldown_and_can_be_reset() -> None:
    gate = PointingEventGate(cooldown_seconds=3.0)

    assert gate.allow(10.0)
    assert not gate.allow(12.9)
    assert gate.allow(13.0)

    gate.reset()
    assert gate.allow(13.1)
