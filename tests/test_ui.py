"""Tests for Zoom AI Copilot PySide6 GUI."""

import pytest

from zoom_ai_copilot.audio.router import AudioRouter
from zoom_ai_copilot.config import Settings
from zoom_ai_copilot.llm.mock import MockLLM
from zoom_ai_copilot.models import PipelineState
from zoom_ai_copilot.pipeline.controller import PipelineController
from zoom_ai_copilot.stt.mock import MockSTT
from zoom_ai_copilot.tts.mock import MockTTS
from zoom_ai_copilot.ui.main_window import MainWindow


@pytest.fixture
def main_window(qtbot):
    settings = Settings()
    controller = PipelineController(
        settings=settings,
        stt=MockSTT(),
        llm=MockLLM(),
        tts=MockTTS(),
        audio_router=AudioRouter(),
    )
    window = MainWindow(controller)
    qtbot.addWidget(window)
    return window


def test_main_window_components(main_window):
    """Verify window title, initial state badge, and default settings."""
    assert main_window.windowTitle() == "Zoom AI Copilot"
    assert "IDLE" in main_window.status_badge.label.text()
    assert main_window.chk_auto_speak.isChecked() is False
    assert main_window.chk_mic_passthrough.isChecked() is True
    assert main_window.speak_button.text() == "Speak"
    assert main_window.stop_button.text() == "Stop"
    assert main_window.regenerate_button.text() == "Regenerate"


def test_simulate_speech_flow_in_gui(main_window, qtbot):
    """Verify simulated speech updates transcript and proposed response in GUI."""
    # Simulate incoming speech
    main_window.sim_speech_button.click()

    # Wait for transcript and response to update
    qtbot.waitUntil(
        lambda: "森さん、この構成にした理由を教えてください。" in main_window.transcript_box.toPlainText(),
        timeout=2000,
    )
    qtbot.waitUntil(
        lambda: "主な理由はコストと運用負荷です" in main_window.response_box.toPlainText(),
        timeout=2000,
    )
    assert main_window.status_badge.label.text() == f"Status: {PipelineState.READY_TO_SPEAK.value}"
