"""Application entrypoint for Zoom AI Copilot."""

import argparse
import logging
import sys

from PySide6.QtWidgets import QApplication

from zoom_ai_copilot.audio.router import AudioRouter
from zoom_ai_copilot.config import get_settings
from zoom_ai_copilot.llm.mock import MockLLM
from zoom_ai_copilot.llm.openai import OpenAILLM
from zoom_ai_copilot.pipeline.controller import PipelineController
from zoom_ai_copilot.stt.mock import MockSTT
from zoom_ai_copilot.stt.openai_realtime import OpenAIRealtimeSTT
from zoom_ai_copilot.tts.elevenlabs import ElevenLabsTTS
from zoom_ai_copilot.tts.mock import MockTTS
from zoom_ai_copilot.ui.main_window import MainWindow

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("zoom_ai_copilot")


def build_pipeline_controller() -> PipelineController:
    """Instantiate and wire components according to settings."""
    settings = get_settings()

    # STT Provider
    if settings.stt_provider == "openai":
        stt = OpenAIRealtimeSTT(
            api_key=settings.openai_api_key.get_secret_value() if settings.openai_api_key else None,
            model=settings.openai_realtime_model,
        )
    else:
        stt = MockSTT()

    # LLM Provider
    if settings.llm_provider == "openai":
        llm = OpenAILLM(
            api_key=settings.openai_api_key.get_secret_value() if settings.openai_api_key else None,
            model=settings.openai_llm_model,
        )
    else:
        llm = MockLLM()

    # TTS Provider
    if settings.tts_provider == "elevenlabs":
        tts = ElevenLabsTTS(
            api_key=settings.elevenlabs_api_key.get_secret_value()
            if settings.elevenlabs_api_key
            else None,
            voice_id=settings.elevenlabs_voice_id,
            model_id=settings.elevenlabs_model_id,
        )
    else:
        tts = MockTTS()

    audio_router = AudioRouter()
    return PipelineController(
        settings=settings,
        stt=stt,
        llm=llm,
        tts=tts,
        audio_router=audio_router,
    )


def main() -> int:
    """Main CLI entrypoint."""
    parser = argparse.ArgumentParser(description="Zoom AI Copilot")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run initial boot diagnostics without entering GUI event loop",
    )
    args = parser.parse_args()

    controller = build_pipeline_controller()
    logger.info(
        "Initialized Zoom AI Copilot (STT: %s, LLM: %s, TTS: %s)",
        controller.settings.stt_provider,
        controller.settings.llm_provider,
        controller.settings.tts_provider,
    )

    if args.dry_run:
        logger.info("Dry-run verification completed successfully.")
        return 0

    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    window = MainWindow(controller)
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
