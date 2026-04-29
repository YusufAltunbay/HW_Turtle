"""
VerifyView: Fotoğraftan kaplumbağa doğrulama ekranı.
"""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from turtle_id.agents.ui_agent import UIAgent
from turtle_id.core.use_cases.verify_turtle import VerifyTurtleResponse
from turtle_id.ui.widgets.photo_picker import PhotoPicker


class VerifyView(QWidget):
    """Kaplumbağa tanıma ve doğrulama ekranı."""

    verification_done = Signal(object)   # VerifyTurtleResponse

    def __init__(self, ui_agent: UIAgent, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._ui_agent = ui_agent
        self._setup_ui()
        self._connect_signals()

    # ------------------------------------------------------------------ #
    #  UI kurulumu                                                          #
    # ------------------------------------------------------------------ #

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("Kaplumbağa Tanı")
        title.setObjectName("page_title")
        layout.addWidget(title)

        subtitle = QLabel(
            "Bir fotoğraf seçin — sistem kayıtlı kaplumbağalarla karşılaştırır."
        )
        subtitle.setObjectName("status_label")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        # Fotoğraf seçici
        layout.addWidget(self._section("TANIMA FOTOĞRAFI"))
        self._photo_picker = PhotoPicker()
        layout.addWidget(self._photo_picker)

        # Tanı butonu
        self._verify_button = QPushButton("Kaplumbağayı Tanı")
        self._verify_button.setObjectName("primary_button")
        self._verify_button.setEnabled(False)
        layout.addWidget(self._verify_button)

        # Durum
        self._status_label = QLabel("")
        self._status_label.setObjectName("status_label")
        self._status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._status_label)

        layout.addStretch()

    # ------------------------------------------------------------------ #
    #  Sinyal bağlantıları                                                 #
    # ------------------------------------------------------------------ #

    def _connect_signals(self) -> None:
        self._photo_picker.photo_selected.connect(self._on_photo_selected)
        self._verify_button.clicked.connect(self._on_verify_clicked)
        self._ui_agent.signals.verification_completed.connect(self._on_verification_done)
        self._ui_agent.signals.processing_started.connect(self._on_processing_started)
        self._ui_agent.signals.processing_finished.connect(self._on_processing_finished)
        self._ui_agent.signals.error_occurred.connect(self._on_error)

    # ------------------------------------------------------------------ #
    #  Slot'lar                                                            #
    # ------------------------------------------------------------------ #

    def _on_photo_selected(self, path: str) -> None:
        self._verify_button.setEnabled(True)
        self._status_label.setStyleSheet("")
        self._status_label.setText(f"Seçildi: {path.split('/')[-1]}")

    def _on_verify_clicked(self) -> None:
        if not self._photo_picker.photo_path:
            QMessageBox.warning(self, "Eksik", "Lütfen bir fotoğraf seçin.")
            return
        self._ui_agent.request_verification(self._photo_picker.photo_path)

    def _on_verification_done(self, response: VerifyTurtleResponse) -> None:
        if not response.success:
            self._status_label.setStyleSheet("color: #ef9a9a;")
            self._status_label.setText("✗  Fotoğraf işlenemedi.")
            QMessageBox.critical(
                self, "Doğrulama Hatası",
                "\n".join(f"• {e}" for e in response.errors)
            )
        elif response.is_identified:
            self._status_label.setStyleSheet("color: #a5d6a7;")
            self._status_label.setText(
                f"✓  Tanındı: {response.turtle.name}  "
                f"(%{int(response.match_result.confidence * 100)} güven)"
            )
        else:
            self._status_label.setStyleSheet("color: #ffcc80;")
            score = response.match_result.similarity_score if response.match_result else 0.0
            self._status_label.setText(
                f"?  Kayıtlı kaplumbağa bulunamadı. "
                f"(En yüksek skor: {score:.3f})"
            )

        if response.warnings:
            QMessageBox.information(
                self, "Fotoğraf Uyarısı",
                "\n".join(f"• {w}" for w in response.warnings)
            )

        self.verification_done.emit(response)

    def _on_processing_started(self, message: str) -> None:
        self._verify_button.setEnabled(False)
        self._status_label.setStyleSheet("color: #4fc3f7;")
        self._status_label.setText(f"⏳  {message}")

    def _on_processing_finished(self) -> None:
        self._verify_button.setEnabled(bool(self._photo_picker.photo_path))

    def _on_error(self, message: str) -> None:
        self._status_label.setStyleSheet("color: #ef9a9a;")
        self._status_label.setText("✗  Beklenmeyen hata.")
        QMessageBox.critical(self, "Hata", message)

    @staticmethod
    def _section(text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setObjectName("section_label")
        return lbl
