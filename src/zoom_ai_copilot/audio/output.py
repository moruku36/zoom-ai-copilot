"""Audio output interface and playback handler."""

import io
import logging
import threading
import wave
from abc import ABC, abstractmethod

import numpy as np

logger = logging.getLogger(__name__)


class AudioOutput(ABC):
    """Abstract base class for audio output playback."""

    @abstractmethod
    def play(self, data: bytes | np.ndarray, sample_rate: int = 24000) -> None:
        """Play audio data asynchronously."""

    @abstractmethod
    def stop(self) -> None:
        """Immediately stop any current playback."""

    @abstractmethod
    def is_playing(self) -> bool:
        """Return True if audio is actively playing."""


class SoundDeviceAudioOutput(AudioOutput):
    """Sounddevice-based audio playback implementation."""

    def __init__(self, device_id: int | None = None) -> None:
        self.device_id = device_id
        self._playing = False
        self._lock = threading.Lock()

    def play(self, data: bytes | np.ndarray, sample_rate: int = 24000) -> None:
        import sounddevice as sd

        self.stop()

        audio_array: np.ndarray
        sr = sample_rate

        if isinstance(data, bytes):
            # Check if it's a WAV container
            if data[:4] == b"RIFF":
                try:
                    with io.BytesIO(data) as bio, wave.open(bio, "rb") as wf:
                        sr = wf.getframerate()
                        n_channels = wf.getnchannels()
                        frames = wf.readframes(wf.getnframes())
                        audio_array = np.frombuffer(frames, dtype=np.int16)
                        if n_channels > 1:
                            audio_array = audio_array.reshape(-1, n_channels)
                except Exception as exc:
                    logger.warning("Failed to parse WAV header, interpreting as raw PCM: %s", exc)
                    audio_array = np.frombuffer(data, dtype=np.int16)
            else:
                audio_array = np.frombuffer(data, dtype=np.int16)
        else:
            audio_array = data

        with self._lock:
            self._playing = True

        def _play_worker() -> None:
            try:
                sd.play(audio_array, samplerate=sr, device=self.device_id, blocking=True)
            except Exception as exc:
                logger.error("Audio playback error: %s", exc)
            finally:
                with self._lock:
                    self._playing = False

        thread = threading.Thread(target=_play_worker, daemon=True)
        thread.start()

    def stop(self) -> None:
        import sounddevice as sd

        try:
            sd.stop()
        except Exception as exc:
            logger.debug("Error calling sounddevice.stop(): %s", exc)
        with self._lock:
            self._playing = False

    def is_playing(self) -> bool:
        with self._lock:
            return self._playing
