"""Audio routing manager with feedback loop prevention."""

import logging
from typing import Any

import numpy as np

from zoom_ai_copilot.audio.input import AudioInput, SoundDeviceAudioInput
from zoom_ai_copilot.audio.output import AudioOutput, SoundDeviceAudioOutput

logger = logging.getLogger(__name__)


class AudioRouter:
    """Manages audio input and output streams while preventing feedback loops."""

    def __init__(
        self,
        input_device_id: int | None = None,
        output_device_id: int | None = None,
        audio_input: AudioInput | None = None,
        audio_output: AudioOutput | None = None,
    ) -> None:
        self.input_device_id = input_device_id
        self.output_device_id = output_device_id
        self._input: AudioInput = audio_input or SoundDeviceAudioInput(device_id=input_device_id)
        self._output: AudioOutput = audio_output or SoundDeviceAudioOutput(
            device_id=output_device_id
        )
        self._validate_routing()

    def _validate_routing(self) -> None:
        """Ensure input and output are not accidentally mapped to the identical device."""
        if (
            self.input_device_id is not None
            and self.output_device_id is not None
            and self.input_device_id == self.output_device_id
        ):
            logger.warning(
                "POTENTIAL FEEDBACK LOOP: Input device (%s) and output device (%s) are identical!",
                self.input_device_id,
                self.output_device_id,
            )

    def set_input_device(self, device_id: int | None) -> None:
        """Switch audio capture input device."""
        self.input_device_id = device_id
        if self._input.is_active():
            self._input.stop()
        self._input = SoundDeviceAudioInput(device_id=device_id)
        self._validate_routing()

    def set_output_device(self, device_id: int | None) -> None:
        """Switch audio playback output device."""
        self.output_device_id = device_id
        if self._output.is_playing():
            self._output.stop()
        self._output = SoundDeviceAudioOutput(device_id=device_id)
        self._validate_routing()

    def play_audio(self, data: bytes | np.ndarray, sample_rate: int = 24000) -> None:
        """Output audio to the designated virtual output."""
        self._output.play(data=data, sample_rate=sample_rate)

    def stop_audio(self) -> None:
        """Immediately stop playback."""
        self._output.stop()

    def is_playing(self) -> bool:
        return self._output.is_playing()

    def start_input(self, callback: Any) -> None:
        self._input.start(callback=callback)

    def stop_input(self) -> None:
        self._input.stop()
