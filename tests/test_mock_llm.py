"""Tests for Mock LLM provider."""

import pytest

from zoom_ai_copilot.llm.mock import MockLLM
from zoom_ai_copilot.models import LLMContext, TranscriptUtterance


@pytest.mark.asyncio
async def test_mock_llm_response():
    """Verify MockLLM returns the canned response."""
    llm = MockLLM(canned_response="モック回答テキスト", simulated_delay=0.0)
    context = LLMContext(
        system_prompt="system",
        meeting_context="meeting",
        transcript_history=[TranscriptUtterance(speaker="Remote", text="質問テキスト")],
        latest_utterance="質問テキスト",
    )

    response = await llm.generate_response(context)
    assert response == "モック回答テキスト"

    # Regeneration check
    second_response = await llm.generate_response(context)
    assert "再生成回答 #2" in second_response
