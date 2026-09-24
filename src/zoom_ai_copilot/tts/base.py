"""Base interface for Text-to-Speech synthesis."""

from abc import ABC, abstractmethod


class TextToSpeech(ABC):
    """Abstract base class for TTS engines."""

    @abstractmethod
    async def synthesize(self, text: str) -> bytes:
        """Synthesize text into audio bytes (e.g. WAV or PCM)."""
