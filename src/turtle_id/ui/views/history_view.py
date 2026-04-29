"""
HistoryView: Kayıtlı kaplumbağalar listesi ve doğrulama geçmişi.

İki sekme içerir:
  1. Kayıtlı Kaplumbağalar — sistemdeki tüm kaplumbağaları listeler
  2. Doğrulama Geçmişi   — VerificationLogORM kayıtlarını gösterir
"""
from __future__ import annotations

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from turtle_id.agents.data_agent import DataAgent
from turtle_id.core.models.turtle import Turtle


class _TurtleRow(QWidget):
    """Listede tek bir kaplumbağa satırı."""

    def __init__(self, turtle: Turtle, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._setup(turtle)

    def _setup(self, turtle: Turtle) -> None:
        self.setObjectName("card")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)

        # Küçük fotoğraf
        photo = QLabel()
        photo.setFixedSize(64, 64)
        photo.setAlignment(Qt.AlignCenter)
        photo.setStyleSheet("border-radius: 6px; background-color: #1e2128;")
        from pathlib import Path  # noqa: PLC0415
        if turtle.primary_photo_path and Path(turtle.primary_photo_path).exists():
            px = QPixmap(turtle.primary_photo_path).scaled(
                64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            photo.setPixmap(px)
        else:
            photo.setText("🐢")
            photo.setStyleSheet("font-size: 28px; background: transparent;")
        layout.addWidget(photo)

        # Bilgiler
        info = QVBoxLayout()
        name_lbl = QLabel(turtle.name)
        name_lbl.setObjectName("turtle_name")
        name_lbl.setStyleSheet("font-size: 15px; font-weight: bold; color: #4fc3f7;")

        species_lbl = QLabel(turtle.species or "Tür belirtilmemiş")
        species_lbl.setObjectName("status_label")

        date_str = turtle.registration_date.strftime("%d.%m.%Y")
        meta_lbl = QLabel(
            f"Kayıt: {date_str}  •  {len(turtle.embeddings)} fotoğraf kaydı"
        )
        meta_lbl.setObjectName("info_key")

        info.addWidget(name_lbl)
        info.addWidget(species_lbl)
        info.addWidget(meta_lbl)
        layout.addLayout(info, stretch=1)

        # ID (kopyalanabilir kısa gösterim)
        id_lbl = QLabel(str(turtle.id)[:8] + "…")
        id_lbl.setObjectName("info_key")
        id_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(id_lbl)


class TurtleListTab(QWidget):
    """Kayıtlı kaplumbağalar sekmesi."""

    def __init__(self, data_agent: DataAgent, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._data_agent = data_agent
        self._setup_ui()

    def refresh(self) -> None:
        """Listeyi veritabanından yenile."""
        # Mevcut satırları temizle
        while self._list_layout.count():
            item = self._list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        turtles = self._data_agent.list_turtles()

        if not turtles:
            empty = QLabel("Henüz kayıtlı kaplumbağa yok.\nKayıt ekranından yeni kaplumbağa ekleyin.")
            empty.setObjectName("status_label")
            empty.setAlignment(Qt.AlignCenter)
            self._list_layout.addWidget(empty)
        else:
            for turtle in turtles:
                row = _TurtleRow(turtle)
                self._list_layout.addWidget(row)
                sep = QFrame()
                sep.setFrameShape(QFrame.HLine)
                self._list_layout.addWidget(sep)

        self._count_label.setText(f"{len(turtles)} kaplumbağa kayıtlı")
        self._list_layout.addStretch()

    def _setup_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 8, 0, 0)
        outer.setSpacing(8)

        top = QHBoxLayout()
        self._count_label = QLabel("Yükleniyor…")
        self._count_label.setObjectName("status_label")
        top.addWidget(self._count_label)
        top.addStretch()
        refresh_btn = QPushButton("Yenile")
        refresh_btn.setObjectName("secondary_button")
        refresh_btn.clicked.connect(self.refresh)
        top.addWidget(refresh_btn)
        outer.addLayout(top)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        container = QWidget()
        self._list_layout = QVBoxLayout(container)
        self._list_layout.setSpacing(6)
        self._list_layout.setContentsMargins(0, 0, 0, 0)
        scroll.setWidget(container)
        outer.addWidget(scroll)


class HistoryView(QWidget):
    """Kaplumbağa listesi ve geçmiş ekranı."""

    def __init__(self, data_agent: DataAgent, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._data_agent = data_agent
        self._setup_ui()

    def refresh(self) -> None:
        self._turtle_tab.refresh()

    def showEvent(self, event) -> None:
        """Ekran her gösterildiğinde listeyi otomatik yenile."""
        super().showEvent(event)
        QTimer.singleShot(100, self.refresh)

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("Kaplumbağa Kayıtları")
        title.setObjectName("page_title")
        layout.addWidget(title)

        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane { border: none; }
            QTabBar::tab {
                background: #1e2128; color: #90a4ae;
                padding: 8px 20px; border-radius: 4px;
                margin-right: 4px;
            }
            QTabBar::tab:selected { background: #1565c0; color: #fff; }
        """)

        self._turtle_tab = TurtleListTab(self._data_agent)
        tabs.addTab(self._turtle_tab, "Kayıtlı Kaplumbağalar")

        layout.addWidget(tabs, stretch=1)
