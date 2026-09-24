"""Main Window for Zoom AI Copilot GUI."""

import logging

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from zoom_ai_copilot.audio.devices import get_input_devices, get_output_devices
from zoom_ai_copilot.models import PipelineState
from zoom_ai_copilot.pipeline.controller import PipelineController
from zoom_ai_copilot.ui.widgets import AudioDeviceSelector, StatusBadge

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Main desktop interface for Zoom AI Copilot."""

    # Thread-safe signals to update GUI from background callbacks
    state_signal = Signal(str)
    transcript_signal = Signal(str)
    response_signal = Signal(str)
    error_signal = Signal(str)

    def __init__(self, controller: PipelineController) -> None:
        super().__init__()
        self.controller = controller
        self.setWindowTitle("Zoom AI Copilot")
        self.setMinimumSize(540, 680)

        self._setup_ui()
        self._connect_signals()
        self._load_audio_devices()

    def _setup_ui(self) -> None:
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(18, 18, 18, 18)

        # Header with App Title and Status Badge
        header_layout = QHBoxLayout()
        title_label = QLabel("Zoom AI Copilot")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.status_badge = StatusBadge(self)

        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.status_badge)
        main_layout.addLayout(header_layout)

        # Separator line
        main_layout.addWidget(self._create_separator())

        # Remote Transcript Section
        transcript_label = QLabel("Remote Transcript")
        transcript_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        main_layout.addWidget(transcript_label)

        self.transcript_box = QTextEdit(self)
        self.transcript_box.setPlaceholderText("Waiting for remote participant speech...")
        self.transcript_box.setReadOnly(True)
        self.transcript_box.setFixedHeight(110)
        self.transcript_box.setStyleSheet(
            "QTextEdit { background-color: #f8f9fa; border: 1px solid #ced4da; border-radius: 6px; padding: 8px; }"
        )
        main_layout.addWidget(self.transcript_box)

        # AI Suggested Response Section
        response_label = QLabel("AI Suggested Response")
        response_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        main_layout.addWidget(response_label)

        self.response_box = QTextEdit(self)
        self.response_box.setPlaceholderText("AI response proposal will appear here...")
        self.response_box.setFixedHeight(130)
        self.response_box.setStyleSheet(
            "QTextEdit { background-color: #ffffff; border: 1px solid #ced4da; border-radius: 6px; padding: 8px; }"
        )
        main_layout.addWidget(self.response_box)

        # Action Buttons: [Speak] [Stop] [Regenerate]
        btn_layout = QHBoxLayout()
        self.speak_button = QPushButton("Speak")
        self.speak_button.setFixedHeight(38)
        self.speak_button.setStyleSheet(
            "QPushButton { background-color: #198754; color: white; font-weight: bold; font-size: 14px; border-radius: 6px; } "
            "QPushButton:hover { background-color: #157347; }"
        )

        self.stop_button = QPushButton("Stop")
        self.stop_button.setFixedHeight(38)
        self.stop_button.setStyleSheet(
            "QPushButton { background-color: #dc3545; color: white; font-weight: bold; font-size: 14px; border-radius: 6px; } "
            "QPushButton:hover { background-color: #bb2d3b; }"
        )

        self.regenerate_button = QPushButton("Regenerate")
        self.regenerate_button.setFixedHeight(38)
        self.regenerate_button.setStyleSheet(
            "QPushButton { background-color: #0d6efd; color: white; font-weight: bold; font-size: 14px; border-radius: 6px; } "
            "QPushButton:hover { background-color: #0b5ed7; }"
        )

        btn_layout.addWidget(self.speak_button)
        btn_layout.addWidget(self.stop_button)
        btn_layout.addWidget(self.regenerate_button)
        main_layout.addLayout(btn_layout)

        # Audio Device Selectors
        main_layout.addWidget(self._create_separator())
        self.input_selector = AudioDeviceSelector("Input:", self)
        self.output_selector = AudioDeviceSelector("Output:", self)
        main_layout.addWidget(self.input_selector)
        main_layout.addWidget(self.output_selector)

        # Checkboxes: [x] Physical Mic Pass-through, [ ] Auto Speak
        main_layout.addWidget(self._create_separator())
        options_layout = QVBoxLayout()
        options_layout.setSpacing(6)

        self.chk_mic_passthrough = QCheckBox("Physical Mic Pass-through", self)
        self.chk_mic_passthrough.setChecked(self.controller.settings.physical_mic_passthrough)

        self.chk_auto_speak = QCheckBox(
            "Auto Speak (Warning: disabled by default for safety)", self
        )
        self.chk_auto_speak.setChecked(self.controller.settings.auto_speak)

        options_layout.addWidget(self.chk_mic_passthrough)
        options_layout.addWidget(self.chk_auto_speak)
        main_layout.addLayout(options_layout)

        # Simulation / Control bar (convenient for testing & mock operation)
        sim_layout = QHBoxLayout()
        self.listen_toggle_button = QPushButton("Start Listening", self)
        self.listen_toggle_button.setStyleSheet(
            "QPushButton { background-color: #6c757d; color: white; border-radius: 4px; padding: 6px; }"
        )
        self.sim_speech_button = QPushButton("Simulate Remote Speech", self)
        self.sim_speech_button.setStyleSheet(
            "QPushButton { background-color: #495057; color: white; border-radius: 4px; padding: 6px; }"
        )
        sim_layout.addWidget(self.listen_toggle_button)
        sim_layout.addWidget(self.sim_speech_button)
        main_layout.addLayout(sim_layout)

        # Error notification bar
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #dc3545; font-weight: bold;")
        self.error_label.setVisible(False)
        main_layout.addWidget(self.error_label)

    def _create_separator(self) -> QFrame:
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("color: #dee2e6;")
        return line

    def _connect_signals(self) -> None:
        # Controller callbacks emit Qt signals to update UI from any thread
        self.controller.on_state_change = lambda state: self.state_signal.emit(state.value)
        self.controller.on_transcript_update = lambda text: self.transcript_signal.emit(text)
        self.controller.on_response_update = lambda text: self.response_signal.emit(text)
        self.controller.on_error = lambda err: self.error_signal.emit(err)

        # Connect Qt signals to slot methods
        self.state_signal.connect(self._on_state_updated)
        self.transcript_signal.connect(self._on_transcript_updated)
        self.response_signal.connect(self._on_response_updated)
        self.error_signal.connect(self._on_error_updated)

        # User interactions
        self.speak_button.clicked.connect(self._on_speak_clicked)
        self.stop_button.clicked.connect(self._on_stop_clicked)
        self.regenerate_button.clicked.connect(self._on_regenerate_clicked)
        self.listen_toggle_button.clicked.connect(self._on_listen_toggle_clicked)
        self.sim_speech_button.clicked.connect(self._on_simulate_speech_clicked)

        self.input_selector.combo.currentIndexChanged.connect(self._on_input_device_changed)
        self.output_selector.combo.currentIndexChanged.connect(self._on_output_device_changed)
        self.chk_auto_speak.toggled.connect(self._on_auto_speak_toggled)
        self.chk_mic_passthrough.toggled.connect(self._on_mic_passthrough_toggled)

    def _load_audio_devices(self) -> None:
        input_devs = get_input_devices()
        output_devs = get_output_devices()

        self.input_selector.populate(input_devs, self.controller.audio_router.input_device_id)
        self.output_selector.populate(output_devs, self.controller.audio_router.output_device_id)

    def _on_state_updated(self, state_str: str) -> None:
        try:
            state = PipelineState(state_str)
            self.status_badge.set_state(state)
            if state == PipelineState.LISTENING:
                self.listen_toggle_button.setText("Stop Listening")
            elif state == PipelineState.IDLE:
                self.listen_toggle_button.setText("Start Listening")
        except ValueError:
            pass

    def _on_transcript_updated(self, text: str) -> None:
        self.transcript_box.setPlainText(text)

    def _on_response_updated(self, text: str) -> None:
        self.response_box.setPlainText(text)

    def _on_error_updated(self, error: str) -> None:
        self.error_label.setText(f"Error: {error}")
        self.error_label.setVisible(bool(error))

    def _on_speak_clicked(self) -> None:
        text = self.response_box.toPlainText().strip()
        self.controller._schedule_async(self.controller.speak(custom_text=text))

    def _on_stop_clicked(self) -> None:
        self.controller.stop_speaking()

    def _on_regenerate_clicked(self) -> None:
        self.controller._schedule_async(self.controller.regenerate_response())

    def _on_listen_toggle_clicked(self) -> None:
        if self.controller.current_state == PipelineState.IDLE:
            self.controller.start_listening()
        else:
            self.controller.stop_listening()

    def _on_simulate_speech_clicked(self) -> None:
        if self.controller.current_state == PipelineState.IDLE:
            self.controller.start_listening()
        if hasattr(self.controller.stt, "simulate_remote_speech"):
            self.controller.stt.simulate_remote_speech()
        else:
            self.controller._on_stt_transcript("森さん、この構成にした理由を教えてください。", True)

    def _on_input_device_changed(self) -> None:
        dev_id = self.input_selector.get_selected_device_id()
        self.controller.audio_router.set_input_device(dev_id)

    def _on_output_device_changed(self) -> None:
        dev_id = self.output_selector.get_selected_device_id()
        self.controller.audio_router.set_output_device(dev_id)

    def _on_auto_speak_toggled(self, checked: bool) -> None:
        self.controller.settings.auto_speak = checked

    def _on_mic_passthrough_toggled(self, checked: bool) -> None:
        self.controller.settings.physical_mic_passthrough = checked
