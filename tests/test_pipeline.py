"""End-to-end tests for PipelineController."""

from unittest.mock import MagicMock

import pytest

from zoom_ai_copilot.audio.router import AudioRouter
from zoom_ai_copilot.config import Settings
from zoom_ai_copilot.llm.mock import MockLLM
from zoom_ai_copilot.models import PipelineState
from zoom_ai_copilot.pipeline.controller import PipelineController
from zoom_ai_copilot.stt.mock import MockSTT
from zoom_ai_copilot.tts.mock import MockTTS


@pytest.fixture
def controller():
    settings = Settings(
        stt_provider="mock",
        llm_provider="mock",
        tts_provider="mock",
        auto_speak=False,
    )
    stt = MockSTT(canned_utterance="質問: なぜこの技術を選定したのですか？")
    llm = MockLLM(
        canned_response="回答: 開発スピードと堅牢性を重視したためです。", simulated_delay=0.0
    )
    tts = MockTTS(duration_sec=0.05)

    mock_input = MagicMock()
    mock_output = MagicMock()
    audio_router = AudioRouter(audio_input=mock_input, audio_output=mock_output)

    return PipelineController(
        settings=settings,
        stt=stt,
        llm=llm,
        tts=tts,
        audio_router=audio_router,
    )


@pytest.mark.asyncio
async def test_pipeline_safety_default_no_autospeak(controller):
    """Verify auto_speak defaults to False and never speaks automatically."""
    assert controller.settings.auto_speak is False
    assert controller.current_state == PipelineState.IDLE

    # Start listening
    controller.start_listening()
    assert controller.current_state == PipelineState.LISTENING

    # Trigger transcript and await response generation
    response = await controller.generate_response()
    assert response == "回答: 開発スピードと堅牢性を重視したためです。"
    # Must stop at READY_TO_SPEAK without speaking!
    assert controller.current_state == PipelineState.READY_TO_SPEAK
    assert controller.suggested_response == response


@pytest.mark.asyncio
async def test_pipeline_user_speak_and_stop(controller):
    """Verify user can trigger Speak and Stop."""
    controller.suggested_response = "確認済みの回答です。"

    # User presses Speak
    await controller.speak()
    assert len(controller.transcript_history) == 1
    assert controller.transcript_history[0].speaker == "User"
    assert controller.transcript_history[0].text == "確認済みの回答です。"

    # Stop speaking
    controller.stop_speaking()


@pytest.mark.asyncio
async def test_pipeline_regeneration(controller):
    """Verify user can regenerate response."""
    controller.latest_remote_transcript = "質問: 他の選択肢は検討しましたか？"
    first = await controller.generate_response()
    assert first == "回答: 開発スピードと堅牢性を重視したためです。"

    second = await controller.regenerate_response()
    assert "再生成回答 #2" in second


def test_config_provider_switching():
    """Verify configuration allows toggling providers."""
    s1 = Settings(stt_provider="mock", llm_provider="mock", tts_provider="mock")
    assert s1.stt_provider == "mock"

    s2 = Settings(stt_provider="openai", llm_provider="openai", tts_provider="elevenlabs")
    assert s2.stt_provider == "openai"
    assert s2.llm_provider == "openai"
    assert s2.tts_provider == "elevenlabs"
