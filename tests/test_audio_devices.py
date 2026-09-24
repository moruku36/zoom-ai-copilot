"""Tests for audio device discovery and routing."""

from unittest.mock import patch

from zoom_ai_copilot.audio.devices import (
    get_input_devices,
    get_output_devices,
    list_audio_devices,
)
from zoom_ai_copilot.audio.router import AudioRouter


def test_list_audio_devices_fallback_on_error():
    """Verify list_audio_devices returns empty list on PortAudio exception."""
    with patch("sounddevice.query_devices", side_effect=Exception("PortAudio device error")):
        devices = list_audio_devices()
        assert devices == []


def test_device_filtering():
    """Verify input and output device filtering."""
    fake_devices = [
        {
            "name": "Built-in Mic",
            "max_input_channels": 2,
            "max_output_channels": 0,
            "default_samplerate": 48000.0,
        },
        {
            "name": "Built-in Speaker",
            "max_input_channels": 0,
            "max_output_channels": 2,
            "default_samplerate": 48000.0,
        },
        {
            "name": "Loopback Audio",
            "max_input_channels": 2,
            "max_output_channels": 2,
            "default_samplerate": 48000.0,
        },
    ]

    with patch("sounddevice.query_devices", return_value=fake_devices):
        inputs = get_input_devices()
        outputs = get_output_devices()

        assert len(inputs) == 2
        assert len(outputs) == 2
        assert inputs[0].name == "Built-in Mic"
        assert outputs[0].name == "Built-in Speaker"


def test_audio_router_feedback_warning(caplog):
    """Verify router warns when input and output devices are identical."""
    import logging

    with caplog.at_level(logging.WARNING):
        _ = AudioRouter(input_device_id=1, output_device_id=1)
        assert "POTENTIAL FEEDBACK LOOP" in caplog.text


def test_audio_router_device_switching():
    """Verify router switches devices without crashing."""
    router = AudioRouter(input_device_id=0, output_device_id=1)
    router.set_input_device(2)
    assert router.input_device_id == 2
    router.set_output_device(3)
    assert router.output_device_id == 3
