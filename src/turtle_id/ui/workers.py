"""
Worker thread'ler: ağır işlemleri (model inference, DB) arka planda çalıştırır.

QThread kullanımı GUI'nin donmasını engeller.
Her worker kendi QObject sinyalleriyle sonucu ana thread'e iletir.
"""
from __future__ import annotations
from uuid import UUID

from PySide6.QtCore import QObject, QThread, Signal

from turtle_id.core.use_cases.register_turtle import (
    RegisterTurtleRequest,
    RegisterTurtleResponse,
    RegisterTurtleUseCase,
)
from turtle_id.core.use_cases.verify_turtle import (
    VerifyTurtleRequest,
    VerifyTurtleResponse,
    VerifyTurtleUseCase,
)


class _WorkerSignals(QObject):
    """Tüm worker'ların paylaştığı sinyal seti."""
    finished = Signal(object)   # Response nesnesi
    error = Signal(str)         # Hata mesajı


class RegisterWorker(QThread):
    """Kaplumbağa kayıt use case'ini arka planda çalıştırır."""

    def __init__(
        self,
        use_case: RegisterTurtleUseCase,
        request: RegisterTurtleRequest,
    ) -> None:
        super().__init__()
        self._use_case = use_case
        self._request = request
        self.signals = _WorkerSignals()

    def run(self) -> None:
        try:
            response: RegisterTurtleResponse = self._use_case.execute(self._request)
            self.signals.finished.emit(response)
        except Exception as exc:
            self.signals.error.emit(str(exc))


class VerifyWorker(QThread):
    """Kaplumbağa doğrulama use case'ini arka planda çalıştırır."""

    def __init__(
        self,
        use_case: VerifyTurtleUseCase,
        request: VerifyTurtleRequest,
    ) -> None:
        super().__init__()
        self._use_case = use_case
        self._request = request
        self.signals = _WorkerSignals()

    def run(self) -> None:
        try:
            response: VerifyTurtleResponse = self._use_case.execute(self._request)
            self.signals.finished.emit(response)
        except Exception as exc:
            self.signals.error.emit(str(exc))


class AddPhotoWorker(QThread):
    """Mevcut kaplumbağaya ek fotoğraf/embedding ekler."""

    def __init__(
        self,
        turtle_id: str,
        photo_path: str,
        image_agent,
        data_agent,
    ) -> None:
        super().__init__()
        self._turtle_id = UUID(turtle_id)
        self._photo_path = photo_path
        self._image_agent = image_agent
        self._data_agent = data_agent
        self.signals = _WorkerSignals()

    def run(self) -> None:
        try:
            from turtle_id.core.use_cases.register_turtle import RegisterTurtleResponse  # noqa: PLC0415
            embedding = self._image_agent.process(self._photo_path, self._turtle_id)
            self._data_agent.add_embedding(embedding)
            turtle = self._data_agent.get_turtle(self._turtle_id)
            response = RegisterTurtleResponse(success=True, turtle=turtle)
            self.signals.finished.emit(response)
        except Exception as exc:
            self.signals.error.emit(str(exc))
