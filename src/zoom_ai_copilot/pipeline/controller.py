"""Pipeline controller coordinating STT, LLM, TTS, Audio I/O, and UI."""

import asyncio
import logging
import threading
from collections.abc import Callable
from typing import Any

from zoom_ai_copilot.audio.router import AudioRouter
from zoom_ai_copilot.config import Settings
from zoom_ai_copilot.llm.base import LanguageModel
from zoom_ai_copilot.models import LLMContext, PipelineState, TranscriptUtterance
from zoom_ai_copilot.pipeline.state import PipelineStateManager
from zoom_ai_copilot.stt.base import SpeechToText
from zoom_ai_copilot.tts.base import TextToSpeech

logger = logging.getLogger(__name__)


class PipelineController:
    """Central orchestrator for meeting audio transcription, AI reasoning, and voice reply."""

    def __init__(
        self,
        settings: Settings,
        stt: SpeechToText,
        llm: LanguageModel,
        tts: TextToSpeech,
        audio_router: AudioRouter,
    ) -> None:
        self.settings = settings
        self.stt = stt
        self.llm = llm
        self.tts = tts
        self.audio_router = audio_router

        self.state_manager = PipelineStateManager(PipelineState.IDLE)
        self.transcript_history: list[TranscriptUtterance] = []
        self.latest_remote_transcript: str = ""
        self.suggested_response: str = ""
        self.error_message: str | None = None

        # Callbacks for UI updates
        self.on_state_change: Callable[[PipelineState], None] | None = None
        self.on_transcript_update: Callable[[str], None] | None = None
        self.on_response_update: Callable[[str], None] | None = None
        self.on_error: Callable[[str], None] | None = None

        self.state_manager.add_listener(self._notify_state_change)

    @property
    def current_state(self) -> PipelineState:
        return self.state_manager.current_state

    def _notify_state_change(self, state: PipelineState) -> None:
        if self.on_state_change is not None:
            self.on_state_change(state)

    def start_listening(self) -> None:
        """Start listening to incoming remote meeting audio."""
        try:
            self.state_manager.transition_to(PipelineState.LISTENING)
            self.stt.start(self._on_stt_transcript)
        except Exception as exc:
            self._handle_failure(f"Failed to start STT: {exc}")

    def stop_listening(self) -> None:
        """Stop listening and stop all active streams."""
        try:
            self.stt.stop()
            self.audio_router.stop_audio()
            self.state_manager.transition_to(PipelineState.IDLE)
        except Exception as exc:
            self._handle_failure(f"Failed to stop: {exc}")

    def _on_stt_transcript(self, text: str, is_final: bool) -> None:
        """Invoked when STT yields transcription."""
        if not text.strip():
            return

        self.latest_remote_transcript = text
        if self.on_transcript_update is not None:
            self.on_transcript_update(text)

        if is_final:
            self.transcript_history.append(TranscriptUtterance(speaker="Remote", text=text))
            self.state_manager.transition_to(PipelineState.TRANSCRIBING)
            # Run async LLM response generation in background
            self._schedule_async(self.generate_response())

    def _schedule_async(self, coro: Any) -> None:
        """Helper to run async coroutines from sync callbacks or background threads."""
        try:
            asyncio.get_running_loop()
            asyncio.create_task(coro)
        except RuntimeError:
            threading.Thread(target=lambda: asyncio.run(coro), daemon=True).start()

    async def generate_response(self) -> str:
        """Generate response proposal based on transcript history."""
        try:
            self.state_manager.transition_to(PipelineState.GENERATING)
            context = LLMContext(
                system_prompt=self.settings.system_prompt,
                meeting_context=self.settings.meeting_context,
                transcript_history=list(self.transcript_history),
                latest_utterance=self.latest_remote_transcript,
            )
            response = await self.llm.generate_response(context)
            self.suggested_response = response

            if self.on_response_update is not None:
                self.on_response_update(response)

            self.state_manager.transition_to(PipelineState.READY_TO_SPEAK)

            # Auto-speak check (Strictly OFF by default!)
            if self.settings.auto_speak:
                logger.info("Auto Speak is enabled: initiating speech output.")
                await self.speak()

            return response
        except Exception as exc:
            self._handle_failure(f"Failed to generate response: {exc}")
            return ""

    async def regenerate_response(self) -> str:
        """Regenerate proposal with current context."""
        return await self.generate_response()

    async def speak(self, custom_text: str | None = None) -> None:
        """Synthesize and output response to virtual microphone device."""
        text_to_speak = (custom_text or self.suggested_response).strip()
        if not text_to_speak:
            logger.warning("Speak called with empty text.")
            return

        try:
            self.state_manager.transition_to(PipelineState.SPEAKING)
            audio_bytes = await self.tts.synthesize(text_to_speak)

            if audio_bytes:
                self.audio_router.play_audio(audio_bytes)

            # Record user/AI utterance in meeting history
            self.transcript_history.append(TranscriptUtterance(speaker="User", text=text_to_speak))
            self.state_manager.transition_to(PipelineState.READY_TO_SPEAK)
        except Exception as exc:
            self._handle_failure(f"Failed to speak audio: {exc}")

    def stop_speaking(self) -> None:
        """Immediately interrupt audio playback."""
        self.audio_router.stop_audio()
        if self.current_state == PipelineState.SPEAKING:
            self.state_manager.transition_to(PipelineState.READY_TO_SPEAK)

    def _handle_failure(self, error: str) -> None:
        """Handle errors safely without crashing the UI."""
        logger.error("Pipeline error: %s", error)
        self.error_message = error
        self.state_manager.transition_to(PipelineState.ERROR)
        if self.on_error is not None:
            self.on_error(error)
