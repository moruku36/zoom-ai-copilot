"""Core data models and domain types for Zoom AI Copilot."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class PipelineState(str, Enum):
    """Pipeline operating states."""

    IDLE = "IDLE"
    LISTENING = "LISTENING"
    TRANSCRIBING = "TRANSCRIBING"
    GENERATING = "GENERATING"
    READY_TO_SPEAK = "READY_TO_SPEAK"
    SPEAKING = "SPEAKING"
    ERROR = "ERROR"


@dataclass(frozen=True)
class AudioDeviceInfo:
    """Audio input/output device metadata."""

    id: int
    name: str
    max_input_channels: int
    max_output_channels: int
    default_samplerate: float
    is_input: bool
    is_output: bool


@dataclass
class TranscriptUtterance:
    """Represents a single spoken utterance in the meeting."""

    speaker: str  # e.g., "Remote", "User", "AI"
    text: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class LLMContext:
    """Context bundle passed to LLM for response generation."""

    system_prompt: str
    meeting_context: str
    transcript_history: list[TranscriptUtterance]
    latest_utterance: str
