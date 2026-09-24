"""Tests for Mock TTS provider."""

import io
import wave

import pytest

from zoom_ai_copilot.tts.mock import MockTTS


@pytest.mark.asyncio
async def test_mock_tts_synthesize_valid_wav():
    """Verify MockTTS produces a valid WAV audio payload."""
    tts = MockTTS(sample_rate=16000, duration_sec=0.1)
    audio_bytes = await tts.synthesize("テスト発話")

    assert len(audio_bytes) > 44
    assert audio_bytes[:4] == b"RIFF"

    # Verify wave can parse it
    with io.BytesIO(audio_bytes) as bio, wave.open(bio, "rb") as wf:
        assert wf.getframerate() == 16000
        assert wf.getnchannels() == 1
        assert wf.getsampwidth() == 2
        assert wf.getnframes() == int(16000 * 0.1)
