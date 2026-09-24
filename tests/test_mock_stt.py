"""Tests for Mock STT provider."""

import numpy as np

from zoom_ai_copilot.stt.mock import MockSTT


def test_mock_stt_simulate_speech():
    """Verify MockSTT triggers callback with simulated speech."""
    received = []

    def on_transcript(text: str, is_final: bool) -> None:
        received.append((text, is_final))

    stt = MockSTT(canned_utterance="テスト音声発話")
    stt.start(on_transcript)

    stt.simulate_remote_speech()
    assert len(received) == 1
    assert received[0] == ("テスト音声発話", True)

    stt.simulate_remote_speech("カスタム発話")
    assert len(received) == 2
    assert received[1] == ("カスタム発話", True)

    stt.stop()
    # After stop, further simulated speech should not trigger callback
    stt.simulate_remote_speech("停止後発話")
    assert len(received) == 2


def test_mock_stt_feed_audio():
    """Verify feed_audio is accepted without raising."""
    stt = MockSTT()
    stt.feed_audio(np.zeros(1024, dtype=np.int16))
