"""OpenAI LLM implementation."""

import logging

from zoom_ai_copilot.llm.base import LanguageModel
from zoom_ai_copilot.models import LLMContext

logger = logging.getLogger(__name__)


class OpenAILLM(LanguageModel):
    """OpenAI Chat Completion client for generating meeting responses."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "gpt-4o-mini",
    ) -> None:
        self.api_key = api_key
        self.model = model

    async def generate_response(self, context: LLMContext) -> str:
        """Call OpenAI Chat Completions API (fully wired in Phase 3)."""
        logger.info("OpenAILLM generate_response called for model %s", self.model)
        # Real integration in Phase 3
        return "OpenAI response placeholder"
