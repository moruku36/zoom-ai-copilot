"""Custom reusable UI widgets for Zoom AI Copilot."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QWidget,
)

from zoom_ai_copilot.models import AudioDeviceInfo, PipelineState


class StatusBadge(QFrame):
    """Visual status pill badge indicating the pipeline state."""

    STATE_COLORS = {
        PipelineState.IDLE: ("#6c757d", "#ffffff"),
        PipelineState.LISTENING: ("#0d6efd", "#ffffff"),
        PipelineState.TRANSCRIBING: ("#0dcaf0", "#000000"),
        PipelineState.GENERATING: ("#ffc107", "#000000"),
        PipelineState.READY_TO_SPEAK: ("#198754", "#ffffff"),
        PipelineState.SPEAKING: ("#d63384", "#ffffff"),
        PipelineState.ERROR: ("#dc3545", "#ffffff"),
    }

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 4, 10, 4)

        self.label = QLabel("Status: IDLE")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)
        self.set_state(PipelineState.IDLE)

    def set_state(self, state: PipelineState) -> None:
        bg, fg = self.STATE_COLORS.get(state, ("#6c757d", "#ffffff"))
        self.setStyleSheet(
            f"StatusBadge {{ background-color: {bg}; border-radius: 12px; }} "
            f"QLabel {{ color: {fg}; font-weight: bold; font-size: 13px; }}"
        )
        self.label.setText(f"Status: {state.value}")


class AudioDeviceSelector(QWidget):
    """Dropdown selector for input or output audio devices."""

    def __init__(self, label_text: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.title_label = QLabel(label_text)
        self.title_label.setFixedWidth(60)
        self.combo = QComboBox()
        self.combo.setMinimumWidth(240)

        layout.addWidget(self.title_label)
        layout.addWidget(self.combo)

    def populate(self, devices: list[AudioDeviceInfo], selected_id: int | None = None) -> None:
        self.combo.clear()
        if not devices:
            self.combo.addItem("No devices found", -1)
            return

        selected_index = 0
        for idx, dev in enumerate(devices):
            self.combo.addItem(f"{dev.name} (id: {dev.id})", dev.id)
            if selected_id is not None and dev.id == selected_id:
                selected_index = idx

        self.combo.setCurrentIndex(selected_index)

    def get_selected_device_id(self) -> int | None:
        data = self.combo.currentData()
        return None if data is None or data == -1 else int(data)
