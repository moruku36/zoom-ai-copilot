"""Mock Speech-to-Text implementation for testing without external APIs."""

import logging
import threading
import time
from collections.abc import Callable

import numpy as np

from zoom_ai_copilot.stt.base import SpeechToText

logger = logging.getLogger(__name__)

DEFAULT_MOCK_UTTERANCE = "森さん、この構成にした理由を教えてください。"


class MockSTT(SpeechToText):
    """Mock STT that emits configured utterances for end-to-end testing."""

    def __init__(
        self,
        canned_utterance: str = DEFAULT_MOCK_UTTERANCE,
        auto_emit_delay: float | None = None,
    ) -> None:
        self.canned_utterance = canned_utterance
        self.auto_emit_delay = auto_emit_delay
        self._callback: Callable[[str, bool], None] | None = None
        self._running = False
        self._thread: threading.Thread | None = None

    def start(self, on_transcript: Callable[[str, bool], None]) -> None:
        self._callback = on_transcript
        self._running = True

        if self.auto_emit_delay is not None:

            def _auto_worker() -> None:
                time.sleep(self.auto_emit_delay)
                if self._running:
                    self.simulate_remote_speech(self.canned_utterance)

            self._thread = threading.Thread(target=_auto_worker, daemon=True)
            self._thread.start()

    def stop(self) -> None:
        self._running = False
        self._callback = None

    def feed_audio(self, audio_chunk: np.ndarray) -> None:
        # Mock simply ignores real audio input or logs it
        pass

    def simulate_remote_speech(self, text: str | None = None) -> None:
        """Trigger transcription event manually."""
        utterance = text or self.canned_utterance
        if self._callback is not None:
            self._callback(utterance, True)
