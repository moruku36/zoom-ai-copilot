"""Mock Language Model implementation for offline testing."""

import asyncio
import logging

from zoom_ai_copilot.llm.base import LanguageModel
from zoom_ai_copilot.models import LLMContext

logger = logging.getLogger(__name__)

DEFAULT_MOCK_ANSWER = "主な理由はコストと運用負荷です。特に既存環境との統合を考慮しました。"


class MockLLM(LanguageModel):
    """Mock LLM returning predefined responses without external API calls."""

    def __init__(
        self,
        canned_response: str = DEFAULT_MOCK_ANSWER,
        simulated_delay: float = 0.05,
    ) -> None:
        self.canned_response = canned_response
        self.simulated_delay = simulated_delay
        self.generation_count = 0

    async def generate_response(self, context: LLMContext) -> str:
        self.generation_count += 1
        if self.simulated_delay > 0:
            await asyncio.sleep(self.simulated_delay)

        # Vary response slightly if regenerated to verify regeneration in tests
        if self.generation_count > 1:
            return f"{self.canned_response} (再生成回答 #{self.generation_count})"

        return self.canned_response
