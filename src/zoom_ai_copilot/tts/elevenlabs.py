"""ElevenLabs TTS client implementation stub."""

import logging

from zoom_ai_copilot.tts.base import TextToSpeech

logger = logging.getLogger(__name__)


class ElevenLabsTTS(TextToSpeech):
    """ElevenLabs Text-to-Speech API client."""

    def __init__(
        self,
        api_key: str | None = None,
        voice_id: str | None = None,
        model_id: str = "eleven_multilingual_v2",
    ) -> None:
        self.api_key = api_key
        self.voice_id = voice_id
        self.model_id = model_id

    async def synthesize(self, text: str) -> bytes:
        """Call ElevenLabs API to synthesize speech (fully wired in Phase 3)."""
        logger.info("ElevenLabsTTS synthesize called for voice %s", self.voice_id)
        # Real integration in Phase 3
        return b""
