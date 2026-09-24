"""Audio capture interface and stream handler."""

import logging
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


class AudioInput(ABC):
    """Abstract base class for audio input capture."""

    @abstractmethod
    def start(self, callback: Callable[[np.ndarray], None]) -> None:
        """Start capturing audio stream."""

    @abstractmethod
    def stop(self) -> None:
        """Stop capturing audio stream."""

    @abstractmethod
    def is_active(self) -> bool:
        """Return True if currently capturing."""


class SoundDeviceAudioInput(AudioInput):
    """Sounddevice-based real audio capture stream."""

    def __init__(
        self,
        device_id: int | None = None,
        sample_rate: int = 16000,
        channels: int = 1,
    ) -> None:
        self.device_id = device_id
        self.sample_rate = sample_rate
        self.channels = channels
        self._stream: Any = None
        self._callback: Callable[[np.ndarray], None] | None = None

    def start(self, callback: Callable[[np.ndarray], None]) -> None:
        import sounddevice as sd

        if self._stream is not None and self._stream.active:
            return

        self._callback = callback

        def _sd_callback(indata: np.ndarray, frames: int, time_info: Any, status: Any) -> None:
            if status:
                logger.debug("SoundDevice input status: %s", status)
            if self._callback is not None:
                self._callback(indata.copy())

        try:
            self._stream = sd.InputStream(
                device=self.device_id,
                channels=self.channels,
                samplerate=self.sample_rate,
                callback=_sd_callback,
            )
            self._stream.start()
        except Exception as exc:
            logger.error("Failed to start sounddevice InputStream: %s", exc)
            self._stream = None

    def stop(self) -> None:
        if self._stream is not None:
            try:
                self._stream.stop()
                self._stream.close()
            except Exception as exc:
                logger.warning("Error stopping InputStream: %s", exc)
            finally:
                self._stream = None
                self._callback = None

    def is_active(self) -> bool:
        return self._stream is not None and getattr(self._stream, "active", False)
