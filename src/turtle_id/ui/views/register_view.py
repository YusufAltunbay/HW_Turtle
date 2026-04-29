"""
RegisterView: Yeni kaplumbağa kayıt ekranı.
"""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from turtle_id.agents.ui_agent import UIAgent
from turtle_id.core.use_cases.register_turtle import RegisterTurtleResponse
from turtle_id.ui.widgets.photo_picker import PhotoPicker


class RegisterView(QWidget):
    """Yeni kaplumbağa kayıt formu."""

    registration_done = Signal(object)   # RegisterTurtleResponse

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

        title = QLabel("Kaplumbağa Kayıt")
        title.setObjectName("page_title")
        layout.addWidget(title)

        subtitle = QLabel("Yeni bir kaplumbağayı sisteme ekleyin.")
        subtitle.setObjectName("status_label")
        layout.addWidget(subtitle)

        # Fotoğraf seçici
        layout.addWidget(self._section("FOTOĞRAF"))
        self._photo_picker = PhotoPicker()
        layout.addWidget(self._photo_picker)

        # İsim
        layout.addWidget(self._section("KAPLAUMBAĞA İSMİ *"))
        self._name_input = QLineEdit()
        self._name_input.setPlaceholderText("örn. Ninja, Turbo, Kabuk...")
        layout.addWidget(self._name_input)

        # Tür
        layout.addWidget(self._section("TÜR (opsiyonel)"))
        self._species_input = QLineEdit()
        self._species_input.setPlaceholderText("örn. Chelonia mydas, Caretta caretta...")
        layout.addWidget(self._species_input)

        # Notlar
        layout.addWidget(self._section("NOTLAR (opsiyonel)"))
        self._notes_input = QTextEdit()
        self._notes_input.setPlaceholderText("Ayırt edici özellikler, bulunduğu yer...")
        self._notes_input.setMaximumHeight(80)
        layout.addWidget(self._notes_input)

        # Kaydet butonu
        self._save_button = QPushButton("Kaydet")
        self._save_button.setObjectName("primary_button")
        self._save_button.setEnabled(False)
        layout.addWidget(self._save_button)

        # Durum etiketi
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
        self._save_button.clicked.connect(self._on_save_clicked)
        self._ui_agent.signals.registration_completed.connect(self._on_registration_done)
        self._ui_agent.signals.processing_started.connect(self._on_processing_started)
        self._ui_agent.signals.processing_finished.connect(self._on_processing_finished)
        self._ui_agent.signals.error_occurred.connect(self._on_error)

    # ------------------------------------------------------------------ #
    #  Slot'lar                                                            #
    # ------------------------------------------------------------------ #

    def _on_photo_selected(self, path: str) -> None:
        self._save_button.setEnabled(True)
        self._status_label.setText(f"Seçildi: {path.split('/')[-1]}")

    def _on_save_clicked(self) -> None:
        name = self._name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Eksik Bilgi", "Lütfen kaplumbağa ismini girin.")
            return
        if not self._photo_picker.photo_path:
            QMessageBox.warning(self, "Eksik Bilgi", "Lütfen bir fotoğraf seçin.")
            return

        self._ui_agent.request_registration(
            name=name,
            photo_path=self._photo_picker.photo_path,
            species=self._species_input.text().strip(),
            notes=self._notes_input.toPlainText().strip(),
        )

    def _on_registration_done(self, response: RegisterTurtleResponse) -> None:
        if response.success:
            self._status_label.setStyleSheet("color: #a5d6a7;")
            self._status_label.setText(
                f"✓  '{response.turtle.name}' başarıyla kaydedildi!"
            )
            self._reset_form()
            if response.warnings:
                QMessageBox.information(
                    self, "Uyarılar",
                    "Kayıt tamamlandı ancak bazı uyarılar var:\n\n"
                    + "\n".join(f"• {w}" for w in response.warnings)
                )
        else:
            self._status_label.setStyleSheet("color: #ef9a9a;")
            self._status_label.setText("✗  Kayıt başarısız.")
            QMessageBox.critical(
                self, "Kayıt Hatası",
                "\n".join(f"• {e}" for e in response.errors)
            )
        self.registration_done.emit(response)

    def _on_processing_started(self, message: str) -> None:
        self._save_button.setEnabled(False)
        self._status_label.setStyleSheet("color: #4fc3f7;")
        self._status_label.setText(f"⏳  {message}")

    def _on_processing_finished(self) -> None:
        self._save_button.setEnabled(bool(self._photo_picker.photo_path))

    def _on_error(self, message: str) -> None:
        self._status_label.setStyleSheet("color: #ef9a9a;")
        self._status_label.setText("✗  Hata oluştu.")
        QMessageBox.critical(self, "Beklenmeyen Hata", message)

    # ------------------------------------------------------------------ #
    #  Yardımcılar                                                         #
    # ------------------------------------------------------------------ #

    def _reset_form(self) -> None:
        self._name_input.clear()
        self._species_input.clear()
        self._notes_input.clear()
        self._photo_picker.clear()
        self._save_button.setEnabled(False)

    @staticmethod
    def _section(text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setObjectName("section_label")
        return lbl
