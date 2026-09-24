"""Text-to-Speech package."""

from zoom_ai_copilot.tts.base import TextToSpeech
from zoom_ai_copilot.tts.elevenlabs import ElevenLabsTTS
from zoom_ai_copilot.tts.mock import MockTTS

__all__ = ["ElevenLabsTTS", "MockTTS", "TextToSpeech"]
