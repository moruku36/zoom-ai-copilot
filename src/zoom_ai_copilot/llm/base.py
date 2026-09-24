"""Base interface for Language Model providers."""

from abc import ABC, abstractmethod

from zoom_ai_copilot.models import LLMContext


class LanguageModel(ABC):
    """Abstract base class for LLM response generators."""

    @abstractmethod
    async def generate_response(self, context: LLMContext) -> str:
        """Generate a concise spoken response suggestion for the meeting."""
