"""Configuration settings using pydantic-settings."""

from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_SYSTEM_PROMPT = """You are a meeting copilot.

Generate a concise spoken response to the other participant.

Requirements:
- Answer the latest question directly.
- Prefer short spoken Japanese.
- Do not invent facts.
- If context is insufficient, say so.
- Avoid unnecessarily long explanations.
- Output only the response that should be spoken."""


class Settings(BaseSettings):
    """Application settings loaded from environment or .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Provider Selection
    stt_provider: Literal["mock", "openai"] = Field(
        default="mock",
        description="STT engine provider",
    )
    llm_provider: Literal["mock", "openai"] = Field(
        default="mock",
        description="LLM engine provider",
    )
    tts_provider: Literal["mock", "elevenlabs"] = Field(
        default="mock",
        description="TTS engine provider",
    )

    # OpenAI Settings
    openai_api_key: SecretStr | None = Field(default=None)
    openai_llm_model: str = Field(default="gpt-4o-mini")
    openai_realtime_model: str = Field(default="gpt-4o-realtime-preview")

    # ElevenLabs Settings
    elevenlabs_api_key: SecretStr | None = Field(default=None)
    elevenlabs_voice_id: str | None = Field(default=None)
    elevenlabs_model_id: str = Field(default="eleven_multilingual_v2")

    # Audio Device Settings
    audio_input_device: str | None = Field(default=None)
    audio_output_device: str | None = Field(default=None)

    # Safety & Audio Behavior
    auto_speak: bool = Field(
        default=False,
        description="Auto speak AI response without user confirmation. MUST default to False.",
    )
    physical_mic_passthrough: bool = Field(
        default=True,
        description="Enable pass-through mixing for physical microphone.",
    )

    # Meeting Context & Prompts
    system_prompt: str = Field(default=DEFAULT_SYSTEM_PROMPT)
    meeting_context: str = Field(
        default="Standard engineering discussion or project status update.",
    )


def get_settings() -> Settings:
    """Load and return settings."""
    return Settings()
