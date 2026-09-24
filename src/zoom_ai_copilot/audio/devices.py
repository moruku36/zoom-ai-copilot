"""Audio device discovery and querying utilities."""

import logging
from typing import Any

import sounddevice as sd

from zoom_ai_copilot.models import AudioDeviceInfo

logger = logging.getLogger(__name__)


def list_audio_devices() -> list[AudioDeviceInfo]:
    """Query and return all available audio devices on the host.

    Handles PortAudio errors gracefully when no audio hardware is present.
    """
    try:
        devices: list[dict[str, Any]] = list(sd.query_devices())
    except Exception as exc:
        logger.warning("Failed to query sound devices via PortAudio: %s", exc)
        return []

    result: list[AudioDeviceInfo] = []
    for idx, dev in enumerate(devices):
        max_in = int(dev.get("max_input_channels", 0))
        max_out = int(dev.get("max_output_channels", 0))
        info = AudioDeviceInfo(
            id=idx,
            name=str(dev.get("name", f"Device #{idx}")),
            max_input_channels=max_in,
            max_output_channels=max_out,
            default_samplerate=float(dev.get("default_samplerate", 44100.0)),
            is_input=max_in > 0,
            is_output=max_out > 0,
        )
        result.append(info)

    return result


def get_input_devices() -> list[AudioDeviceInfo]:
    """Return all devices with at least one input channel."""
    return [d for d in list_audio_devices() if d.is_input]


def get_output_devices() -> list[AudioDeviceInfo]:
    """Return all devices with at least one output channel."""
    return [d for d in list_audio_devices() if d.is_output]


def get_default_devices() -> tuple[AudioDeviceInfo | None, AudioDeviceInfo | None]:
    """Return (default_input_device, default_output_device)."""
    try:
        default_in, default_out = sd.default.device
        devices = list_audio_devices()

        in_dev = next((d for d in devices if d.id == default_in), None)
        out_dev = next((d for d in devices if d.id == default_out), None)
        return in_dev, out_dev
    except Exception as exc:
        logger.warning("Failed to determine default audio devices: %s", exc)
        return None, None
