"""
MainWindow: Ana uygulama penceresi.

Sol tarafta sidebar navigasyonu, sağ tarafta QStackedWidget ile
RegisterView, VerifyView ve ResultView arasında geçiş sağlar.
"""
from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from turtle_id.agents.ui_agent import UIAgent
from turtle_id.container import AppContainer
from turtle_id.core.use_cases.verify_turtle import VerifyTurtleResponse
from turtle_id.ui.views.register_view import RegisterView
from turtle_id.ui.views.result_view import ResultView
from turtle_id.ui.views.verify_view import VerifyView

_PAGE_REGISTER = 0
_PAGE_VERIFY = 1
_PAGE_RESULT = 2

_QSS_PATH = Path(__file__).parent / "styles" / "main.qss"


class MainWindow(QMainWindow):
    """
    Ana pencere: sidebar + sayfa yönetimi.
    """

    def __init__(self, container: AppContainer) -> None:
        super().__init__()
        self._container = container
        self._ui_agent = self._build_ui_agent()
        self._setup_window()
        self._apply_styles()
        self._build_layout()
        self._connect_signals()

    # ------------------------------------------------------------------ #
    #  Kurulum                                                             #
    # ------------------------------------------------------------------ #

    def _build_ui_agent(self) -> UIAgent:
        agent = UIAgent(
            event_bus=self._container.event_bus,
            register_use_case=self._container.register_turtle_use_case,
            verify_use_case=self._container.verify_turtle_use_case,
        )
        agent.start()
        return agent

    def _setup_window(self) -> None:
        self.setWindowTitle("Turtle ID — Kaplumbağa Tanıma Sistemi")
        self.setMinimumSize(880, 620)
        self.resize(1000, 680)

    def _apply_styles(self) -> None:
        if _QSS_PATH.exists():
            self.setStyleSheet(_QSS_PATH.read_text(encoding="utf-8"))

    def _build_layout(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setSpacing(0)
        root.setContentsMargins(0, 0, 0, 0)

        # Sidebar
        root.addWidget(self._build_sidebar())

        # İçerik alanı
        content_wrapper = QWidget()
        content_wrapper.setObjectName("content_area")
        content_layout = QVBoxLayout(content_wrapper)
        content_layout.setContentsMargins(32, 28, 32, 28)

        self._stack = QStackedWidget()
        self._register_view = RegisterView(self._ui_agent)
        self._verify_view = VerifyView(self._ui_agent)
        self._result_view = ResultView()

        self._stack.addWidget(self._wrap(self._register_view))  # 0
        self._stack.addWidget(self._wrap(self._verify_view))    # 1
        self._stack.addWidget(self._wrap(self._result_view))    # 2

        content_layout.addWidget(self._stack)
        root.addWidget(content_wrapper, stretch=1)

    def _build_sidebar(self) -> QWidget:
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        layout = QVBoxLayout(sidebar)
        layout.setSpacing(4)
        layout.setContentsMargins(12, 0, 12, 16)

        logo = QLabel("🐢 Turtle ID")
        logo.setObjectName("logo")
        layout.addWidget(logo)

        tagline = QLabel("Kaplumbağa Tanıma Sistemi")
        tagline.setObjectName("subtitle")
        layout.addWidget(tagline)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        layout.addWidget(sep)
        layout.addSpacing(8)

        self._nav_buttons: list[QPushButton] = []

        nav_items = [
            ("➕  Kaplumbağa Kayıt", _PAGE_REGISTER),
            ("🔍  Kaplumbağa Tanı", _PAGE_VERIFY),
            ("📋  Son Sonuç", _PAGE_RESULT),
        ]
        for label, page_idx in nav_items:
            btn = QPushButton(label)
            btn.setObjectName("nav_button")
            btn.setCheckable(False)
            btn.clicked.connect(lambda checked=False, idx=page_idx: self._go_to(idx))
            layout.addWidget(btn)
            self._nav_buttons.append(btn)

        layout.addStretch()

        version = QLabel("v0.1.0")
        version.setObjectName("status_label")
        version.setAlignment(Qt.AlignCenter)
        layout.addWidget(version)

        return sidebar

    def _connect_signals(self) -> None:
        # VerifyView tamamlanınca ResultView'a geçiş yap ve sonucu göster
        self._verify_view.verification_done.connect(self._on_verification_done)
        # İlk sayfayı seç
        self._go_to(_PAGE_REGISTER)

    # ------------------------------------------------------------------ #
    #  Slot'lar                                                            #
    # ------------------------------------------------------------------ #

    def _go_to(self, page: int) -> None:
        self._stack.setCurrentIndex(page)
        for i, btn in enumerate(self._nav_buttons):
            btn.setProperty("active", str(i == page).lower())
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def _on_verification_done(self, response: VerifyTurtleResponse) -> None:
        if response.success:
            self._result_view.show_result(response)
            self._go_to(_PAGE_RESULT)

    # ------------------------------------------------------------------ #
    #  Yardımcı                                                            #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _wrap(widget: QWidget) -> QWidget:
        """Widget'ı kaydırılabilir alan içine sar."""
        scroll = QScrollArea()
        scroll.setWidget(widget)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setObjectName("content_area")
        return scroll
