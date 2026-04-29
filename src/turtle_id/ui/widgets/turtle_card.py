"""
TurtleCard: Kaplumbağa bilgilerini gösteren widget.

Eşleşme sonucunda tanımlanan kaplumbağanın fotoğrafını,
ismini, türünü, güven skorunu ve ek bilgilerini görüntüler.
"""
from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)

from turtle_id.core.models.match_result import MatchResult
from turtle_id.core.models.turtle import Turtle


class TurtleCard(QWidget):
    """
    Tanımlanan kaplumbağanın tüm bilgilerini gösteren kart widget'ı.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._setup_ui()

    def load(self, turtle: Turtle, match_result: MatchResult) -> None:
        """Kaplumbağa ve eşleşme verisiyle kartı doldur."""
        self._name.setText(turtle.name)
        self._species.setText(turtle.species if turtle.species else "Tür belirtilmemiş")
        self._notes.setText(turtle.notes if turtle.notes else "—")

        date_str = turtle.registration_date.strftime("%d.%m.%Y")
        self._reg_date.setText(date_str)

        emb_count = len(turtle.embeddings)
        self._emb_count.setText(f"{emb_count} fotoğraf kaydı")

        confidence_pct = int(match_result.confidence * 100)
        self._confidence_bar.setValue(confidence_pct)
        self._confidence_label.setText(f"%{confidence_pct} eşleşme güveni")

        if confidence_pct >= 85:
            self._confidence_bar.setProperty("warning", False)
        else:
            self._confidence_bar.setProperty("warning", True)
        self._confidence_bar.style().unpolish(self._confidence_bar)
        self._confidence_bar.style().polish(self._confidence_bar)

        score_str = f"{match_result.similarity_score:.4f}"
        self._score_label.setText(f"Benzerlik skoru: {score_str}")

        self._load_photo(turtle.primary_photo_path)

    def clear(self) -> None:
        """Kartı temizle."""
        self._name.setText("—")
        self._species.setText("—")
        self._notes.setText("—")
        self._reg_date.setText("—")
        self._emb_count.setText("—")
        self._confidence_bar.setValue(0)
        self._confidence_label.setText("")
        self._score_label.setText("")
        self._photo.setPixmap(QPixmap())

    # ------------------------------------------------------------------ #
    #  Private                                                             #
    # ------------------------------------------------------------------ #

    def _setup_ui(self) -> None:
        self.setObjectName("turtle_card")

        root = QHBoxLayout(self)
        root.setSpacing(20)

        # Sol: fotoğraf
        self._photo = QLabel()
        self._photo.setFixedSize(160, 160)
        self._photo.setAlignment(Qt.AlignCenter)
        self._photo.setStyleSheet(
            "border-radius: 8px; background-color: #1e2128;"
        )
        root.addWidget(self._photo)

        # Sağ: bilgiler
        info = QVBoxLayout()
        info.setSpacing(6)

        self._name = QLabel("—")
        self._name.setObjectName("turtle_name")

        self._species = QLabel("—")
        self._species.setObjectName("turtle_species")

        info.addWidget(self._name)
        info.addWidget(self._species)
        info.addWidget(self._separator())

        for label_text, attr_name in [
            ("Kayıt tarihi", "_reg_date"),
            ("Fotoğraf sayısı", "_emb_count"),
            ("Notlar", "_notes"),
        ]:
            row = QHBoxLayout()
            key = QLabel(label_text + ":")
            key.setObjectName("info_key")
            key.setFixedWidth(110)
            val = QLabel("—")
            val.setObjectName("info_value")
            val.setWordWrap(True)
            setattr(self, attr_name, val)
            row.addWidget(key)
            row.addWidget(val)
            info.addLayout(row)

        info.addWidget(self._separator())

        self._confidence_bar = QProgressBar()
        self._confidence_bar.setRange(0, 100)
        self._confidence_bar.setValue(0)
        self._confidence_bar.setFixedHeight(12)
        info.addWidget(self._confidence_bar)

        self._confidence_label = QLabel("")
        self._confidence_label.setObjectName("info_value")
        info.addWidget(self._confidence_label)

        self._score_label = QLabel("")
        self._score_label.setObjectName("info_key")
        info.addWidget(self._score_label)

        info.addStretch()
        root.addLayout(info)

    def _load_photo(self, path: str) -> None:
        if path and Path(path).exists():
            pixmap = QPixmap(path).scaled(
                160, 160, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self._photo.setPixmap(pixmap)
        else:
            self._photo.setText("Fotoğraf\nyok")

    @staticmethod
    def _separator() -> QFrame:
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        return line
