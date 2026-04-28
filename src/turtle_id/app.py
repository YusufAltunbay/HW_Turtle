"""
Uygulama giriş noktası.

PySide6 QApplication başlatılır, AppContainer init edilir,
MainWindow gösterilir. Uygulama kapatılırken container temiz kapanır.
"""
from __future__ import annotations

import sys

from loguru import logger

from turtle_id.container import AppContainer


def main() -> None:
    """Uygulamayı başlat."""
    # GUI import'ları burada yapılır — container init'ten önce değil
    from PySide6.QtWidgets import QApplication  # noqa: PLC0415

    app = QApplication(sys.argv)
    app.setApplicationName("Turtle ID")
    app.setApplicationVersion("0.1.0")

    container = AppContainer()
    container.init()

    from turtle_id.ui.main_window import MainWindow  # noqa: PLC0415
    window = MainWindow(container)
    window.show()

    exit_code = app.exec()
    container.shutdown()
    sys.exit(exit_code)


if __name__ == "__main__":
    logger.add("turtle_id.log", rotation="10 MB", retention="7 days", level="DEBUG")
    main()
