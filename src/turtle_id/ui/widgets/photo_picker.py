"""
PhotoPicker: Fotoğraf seçme ve önizleme widget'ı.

Tıklanınca QFileDialog açar, seçilen fotoğrafı önizler.
Sürükle-bırak da desteklenir.
"""
from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QPixmap
from PySide6.QtWidgets import (
    QFileDialog,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

_SUPPORTED = "Fotoğraflar (*.jpg *.jpeg *.png *.bmp *.webp *.tiff)"


class PhotoPicker(QWidget):
    """
    Fotoğraf seçme ve önizleme widget'ı.

    Sinyaller:
        photo_selected(str): Kullanıcı geçerli bir fotoğraf seçtiğinde
                             fotoğrafın tam yolunu yayımlar.
    """

    photo_selected = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._photo_path: str | None = None
        self._setup_ui()
        self.setAcceptDrops(True)

    @property
    def photo_path(self) -> str | None:
        """Seçili fotoğrafın tam yolu (seçilmediyse None)."""
        return self._photo_path

    def clear(self) -> None:
        """Seçimi sıfırla."""
        self._photo_path = None
        self._preview.setPixmap(QPixmap())
        self._hint.show()
        self._preview.hide()

    # ------------------------------------------------------------------ #
    #  Qt olayları                                                         #
    # ------------------------------------------------------------------ #

    def mousePressEvent(self, _event) -> None:
        self._open_dialog()

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:
        urls = event.mimeData().urls()
        if urls:
            self._set_photo(urls[0].toLocalFile())

    # ------------------------------------------------------------------ #
    #  Private                                                             #
    # ------------------------------------------------------------------ #

    def _setup_ui(self) -> None:
        self.setObjectName("photo_picker")
        self.setCursor(Qt.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMinimumHeight(220)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        # İpucu etiketi
        self._hint = QLabel("📷  Fotoğraf seçmek için tıklayın\nveya sürükleyip bırakın")
        self._hint.setAlignment(Qt.AlignCenter)
        self._hint.setStyleSheet("color: #546e7a; font-size: 13px;")
        layout.addWidget(self._hint)

        # Önizleme
        self._preview = QLabel()
        self._preview.setAlignment(Qt.AlignCenter)
        self._preview.setScaledContents(False)
        self._preview.hide()
        layout.addWidget(self._preview)

    def _open_dialog(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Fotoğraf Seç", "", _SUPPORTED)
        if path:
            self._set_photo(path)

    def _set_photo(self, path: str) -> None:
        if not Path(path).exists():
            return
        self._photo_path = path
        pixmap = QPixmap(path)
        if pixmap.isNull():
            return
        scaled = pixmap.scaled(300, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self._preview.setPixmap(scaled)
        self._hint.hide()
        self._preview.show()
        self.photo_selected.emit(path)
