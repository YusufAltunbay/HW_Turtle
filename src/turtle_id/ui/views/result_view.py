"""
ResultView: Doğrulama sonucunu gösteren ekran.

VerifyView'dan gelen VerifyTurtleResponse'u alır ve
TurtleCard widget'ı aracılığıyla detaylı sonucu görüntüler.
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from turtle_id.core.use_cases.verify_turtle import VerifyTurtleResponse
from turtle_id.ui.widgets.turtle_card import TurtleCard


class ResultView(QWidget):
    """Tanıma sonuçlarını detaylı gösteren ekran."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._setup_ui()

    def show_result(self, response: VerifyTurtleResponse) -> None:
        """Doğrulama sonucunu ekrana yansıt."""
        if response.is_identified and response.turtle and response.match_result:
            self._badge.setText("EŞLEŞME BULUNDU")
            self._badge.setObjectName("badge_match")
            self._turtle_card.load(response.turtle, response.match_result)
            self._card_area.show()
            self._no_match_label.hide()
        else:
            self._badge.setText("KAYITLI DEĞİL")
            self._badge.setObjectName("badge_no_match")
            self._card_area.hide()
            score = (
                response.match_result.similarity_score
                if response.match_result else 0.0
            )
            self._no_match_label.setText(
                f"Bu kaplumbağa sistemde kayıtlı değil.\n\n"
                f"En yüksek benzerlik skoru: {score:.4f}\n"
                f"Eşleşme için gereken minimum: "
                f"{response.match_result.threshold_used if response.match_result else '—'}"
            )
            self._no_match_label.show()

        # Badge stilini yenile
        self._badge.style().unpolish(self._badge)
        self._badge.style().polish(self._badge)

    def clear(self) -> None:
        self._badge.setText("")
        self._turtle_card.clear()
        self._no_match_label.hide()

    # ------------------------------------------------------------------ #
    #  Private                                                             #
    # ------------------------------------------------------------------ #

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("Tanıma Sonucu")
        title.setObjectName("page_title")
        layout.addWidget(title)

        # Rozet (EŞLEŞME / KAYITLI DEĞİL)
        self._badge = QLabel("")
        self._badge.setAlignment(Qt.AlignLeft)
        self._badge.setFixedHeight(28)
        layout.addWidget(self._badge)

        # Kaydırılabilir kart alanı
        self._card_area = QScrollArea()
        self._card_area.setWidgetResizable(True)
        self._card_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self._turtle_card = TurtleCard()
        self._card_area.setWidget(self._turtle_card)
        layout.addWidget(self._card_area)

        # Eşleşme yok mesajı
        self._no_match_label = QLabel("")
        self._no_match_label.setObjectName("status_label")
        self._no_match_label.setAlignment(Qt.AlignCenter)
        self._no_match_label.setWordWrap(True)
        self._no_match_label.hide()
        layout.addWidget(self._no_match_label)

        layout.addStretch()
