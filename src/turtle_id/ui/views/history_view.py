"""
HistoryView: Kayıtlı kaplumbağalar listesi ve doğrulama geçmişi.

İki sekme içerir:
  1. Kayıtlı Kaplumbağalar — silme butonu ile birlikte
  2. Doğrulama Geçmişi   — VerificationLogORM tablosunu listeler
"""
from __future__ import annotations

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
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
    """Listede tek bir kaplumbağa satırı — sil butonu dahil."""

    delete_requested = Signal(object)   # Turtle

    def __init__(self, turtle: Turtle, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._turtle = turtle
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
        name_lbl.setStyleSheet("font-size: 15px; font-weight: bold; color: #4fc3f7;")

        species_lbl = QLabel(turtle.species or "Tür belirtilmemiş")
        species_lbl.setObjectName("status_label")

        date_str = turtle.registration_date.strftime("%d.%m.%Y %H:%M")
        meta_lbl = QLabel(
            f"Kayıt: {date_str}  •  {len(turtle.embeddings)} fotoğraf kaydı"
        )
        meta_lbl.setObjectName("info_key")

        if turtle.notes:
            notes_lbl = QLabel(f"Not: {turtle.notes[:60]}{'…' if len(turtle.notes) > 60 else ''}")
            notes_lbl.setObjectName("info_key")
            info.addWidget(notes_lbl)

        info.addWidget(name_lbl)
        info.addWidget(species_lbl)
        info.addWidget(meta_lbl)
        layout.addLayout(info, stretch=1)

        # Sağ taraf: ID + Sil butonu
        right = QVBoxLayout()
        right.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        id_lbl = QLabel(f"#{str(turtle.id)[:8]}")
        id_lbl.setObjectName("info_key")
        id_lbl.setAlignment(Qt.AlignRight)
        right.addWidget(id_lbl)

        del_btn = QPushButton("Sil")
        del_btn.setObjectName("secondary_button")
        del_btn.setFixedWidth(60)
        del_btn.setStyleSheet("""
            QPushButton#secondary_button {
                border-color: #b71c1c; color: #ef9a9a;
            }
            QPushButton#secondary_button:hover { background-color: #1a0000; }
        """)
        del_btn.clicked.connect(lambda: self.delete_requested.emit(self._turtle))
        right.addWidget(del_btn)
        layout.addLayout(right)


class TurtleListTab(QWidget):
    """Kayıtlı kaplumbağalar sekmesi."""

    def __init__(self, data_agent: DataAgent, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._data_agent = data_agent
        self._setup_ui()

    def refresh(self) -> None:
        while self._list_layout.count():
            item = self._list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        turtles = self._data_agent.list_turtles()

        if not turtles:
            empty = QLabel(
                "Henüz kayıtlı kaplumbağa yok.\n"
                "Sol menüden 'Kaplumbağa Kayıt' ekranına gidin."
            )
            empty.setObjectName("status_label")
            empty.setAlignment(Qt.AlignCenter)
            self._list_layout.addWidget(empty)
        else:
            for turtle in turtles:
                row = _TurtleRow(turtle)
                row.delete_requested.connect(self._on_delete)
                self._list_layout.addWidget(row)
                sep = QFrame()
                sep.setFrameShape(QFrame.HLine)
                self._list_layout.addWidget(sep)

        self._count_label.setText(f"{len(turtles)} kaplumbağa kayıtlı")
        self._list_layout.addStretch()

    def _on_delete(self, turtle: Turtle) -> None:
        reply = QMessageBox.question(
            self,
            "Kaplumbağayı Sil",
            f"'{turtle.name}' adlı kaplumbağa silinsin mi?\n\n"
            f"Bu işlem geri alınamaz.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            try:
                self._data_agent._repository.delete(turtle.id)
                self.refresh()
            except Exception as exc:
                QMessageBox.critical(self, "Hata", str(exc))

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


class VerificationLogTab(QWidget):
    """Doğrulama geçmişi sekmesi."""

    def __init__(self, data_agent: DataAgent, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._data_agent = data_agent
        self._setup_ui()

    def refresh(self) -> None:
        while self._list_layout.count():
            item = self._list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        logs = self._fetch_logs()
        if not logs:
            empty = QLabel("Henüz doğrulama yapılmadı.")
            empty.setObjectName("status_label")
            empty.setAlignment(Qt.AlignCenter)
            self._list_layout.addWidget(empty)
        else:
            for log in logs:
                self._list_layout.addWidget(self._make_row(log))
                sep = QFrame(); sep.setFrameShape(QFrame.HLine)
                self._list_layout.addWidget(sep)

        self._list_layout.addStretch()

    def _fetch_logs(self) -> list:
        try:
            if not hasattr(self._data_agent._repository, "_session_factory"):
                return []
            from turtle_id.infrastructure.persistence.models import VerificationLogORM  # noqa: PLC0415
            with self._data_agent._repository._session_factory() as session:
                return (
                    session.query(VerificationLogORM)
                    .order_by(VerificationLogORM.verified_at.desc())
                    .limit(50)
                    .all()
                )
        except Exception:
            return []

    def _make_row(self, log) -> QWidget:
        w = QWidget()
        w.setObjectName("card")
        row = QHBoxLayout(w)
        row.setContentsMargins(12, 8, 12, 8)

        # Rozet
        if log.is_match:
            badge = QLabel("EŞLEŞME")
            badge.setObjectName("badge_match")
        else:
            badge = QLabel("KAYITLI DEĞİL")
            badge.setObjectName("badge_no_match")
        badge.setFixedWidth(110)
        row.addWidget(badge)

        # Bilgiler
        info = QVBoxLayout()
        date_str = log.verified_at.strftime("%d.%m.%Y %H:%M:%S") if log.verified_at else "—"
        score_str = f"{log.similarity_score:.4f}" if log.similarity_score is not None else "—"
        conf_str = f"%{int((log.confidence_score or 0) * 100)}" if log.is_match else "—"

        info.addWidget(QLabel(f"Tarih: {date_str}"))
        detail = QLabel(f"Skor: {score_str}  •  Güven: {conf_str}  •  Eşik: {log.threshold_used:.2f}")
        detail.setObjectName("info_key")
        info.addWidget(detail)
        row.addLayout(info, stretch=1)

        return w

    def _setup_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 8, 0, 0)
        outer.setSpacing(8)

        top = QHBoxLayout()
        top.addWidget(QLabel("Son 50 doğrulama sorgusu"))
        top.addStretch()
        ref_btn = QPushButton("Yenile")
        ref_btn.setObjectName("secondary_button")
        ref_btn.clicked.connect(self.refresh)
        top.addWidget(ref_btn)
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
        self._log_tab.refresh()

    def showEvent(self, event) -> None:
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
                padding: 8px 20px; border-radius: 4px; margin-right: 4px;
            }
            QTabBar::tab:selected { background: #1565c0; color: #fff; }
        """)

        self._turtle_tab = TurtleListTab(self._data_agent)
        self._log_tab = VerificationLogTab(self._data_agent)

        tabs.addTab(self._turtle_tab, "Kayıtlı Kaplumbağalar")
        tabs.addTab(self._log_tab, "Doğrulama Geçmişi")

        layout.addWidget(tabs, stretch=1)
