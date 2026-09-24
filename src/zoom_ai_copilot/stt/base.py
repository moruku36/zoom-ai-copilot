"""Base interface for Speech-to-Text providers."""

from abc import ABC, abstractmethod
from collections.abc import Callable

import numpy as np


class SpeechToText(ABC):
    """Abstract base class for STT engines."""

    @abstractmethod
    def start(self, on_transcript: Callable[[str, bool], None]) -> None:
        """Start listening.

        on_transcript callback takes (text: str, is_final: bool).
        """

    @abstractmethod
    def stop(self) -> None:
        """Stop listening."""

    @abstractmethod
    def feed_audio(self, audio_chunk: np.ndarray) -> None:
        """Feed incoming audio PCM chunk to the STT processor."""
