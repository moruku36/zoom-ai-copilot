"""OpenAI Realtime STT implementation stub."""

import logging
from collections.abc import Callable

import numpy as np

from zoom_ai_copilot.stt.base import SpeechToText

logger = logging.getLogger(__name__)


class OpenAIRealtimeSTT(SpeechToText):
    """OpenAI Realtime API client for low-latency live audio transcription."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "gpt-4o-realtime-preview",
    ) -> None:
        self.api_key = api_key
        self.model = model
        self._running = False
        self._callback: Callable[[str, bool], None] | None = None

    def start(self, on_transcript: Callable[[str, bool], None]) -> None:
        self._callback = on_transcript
        self._running = True
        logger.info("OpenAIRealtimeSTT initialized (real connection activated in Phase 3).")

    def stop(self) -> None:
        self._running = False
        self._callback = None

    def feed_audio(self, audio_chunk: np.ndarray) -> None:
        if not self._running:
            return
        # Audio forwarding via WebSocket implemented in Phase 3
