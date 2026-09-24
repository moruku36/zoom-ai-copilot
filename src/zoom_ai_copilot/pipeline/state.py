"""Pipeline state definitions and transition events."""

from collections.abc import Callable

from zoom_ai_copilot.models import PipelineState


class PipelineStateManager:
    """Tracks and notifies state changes across the application."""

    def __init__(self, initial_state: PipelineState = PipelineState.IDLE) -> None:
        self._current_state = initial_state
        self._listeners: list[Callable[[PipelineState], None]] = []

    @property
    def current_state(self) -> PipelineState:
        return self._current_state

    def add_listener(self, listener: Callable[[PipelineState], None]) -> None:
        self._listeners.append(listener)

    def transition_to(self, new_state: PipelineState) -> None:
        """Update current state and notify listeners."""
        if self._current_state != new_state:
            self._current_state = new_state
            for listener in list(self._listeners):
                try:
                    listener(new_state)
                except Exception:
                    pass
