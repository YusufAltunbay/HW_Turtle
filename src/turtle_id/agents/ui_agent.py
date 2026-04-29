"""
UIAgent: View katmanı ile use case'ler arasındaki köprü.

Sorumluluk:
  - View sinyallerini dinle (kullanıcı eylemi)
  - İlgili use case'i arka planda çalıştır (QThread)
  - Sonucu Qt sinyalleriyle ana thread'e ilet
  - Yükleniyor/hata durumlarını koordine et
"""
from __future__ import annotations

from PySide6.QtCore import QObject, Signal

from turtle_id.agents.base_agent import BaseAgent
from turtle_id.agents.data_agent import DataAgent
from turtle_id.agents.image_agent import ImageAgent
from turtle_id.core.models.match_result import MatchResult
from turtle_id.core.models.turtle import Turtle
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
from turtle_id.shared.event_bus import EventBus


class UIAgentSignals(QObject):
    """
    UIAgent'ın Qt sinyalleri.

    QObject'ten türetilmiş ayrı sınıf olarak tanımlanır;
    BaseAgent'ın Python ABC'siyle Qt meta-object sistemi çakışmasın diye.
    """
    registration_completed = Signal(object)   # RegisterTurtleResponse
    verification_completed = Signal(object)   # VerifyTurtleResponse
    error_occurred = Signal(str)
    processing_started = Signal(str)          # işlem açıklaması
    processing_finished = Signal()


class UIAgent(BaseAgent):
    """
    UI koordinasyon ajanı.

    View'lardan gelen istekleri use case'lere yönlendirir,
    sonuçları Qt sinyalleri aracılığıyla view'lara geri gönderir.
    """

    def __init__(
        self,
        event_bus: EventBus,
        register_use_case: RegisterTurtleUseCase,
        verify_use_case: VerifyTurtleUseCase,
        image_agent: ImageAgent | None = None,
        data_agent: DataAgent | None = None,
    ) -> None:
        super().__init__(event_bus)
        self._register_use_case = register_use_case
        self._verify_use_case = verify_use_case
        self._image_agent = image_agent
        self._data_agent = data_agent
        self.signals = UIAgentSignals()

    @property
    def name(self) -> str:
        return "ui_agent"

    def request_registration(
        self,
        name: str,
        photo_path: str,
        species: str = "",
        notes: str = "",
    ) -> None:
        """
        Kayıt isteğini arka plan thread'inde çalıştır.
        Worker, tamamlanınca signals.registration_completed yayımlar.
        """
        from turtle_id.ui.workers import RegisterWorker  # noqa: PLC0415 — circular önlemi
        self.signals.processing_started.emit("Kaplumbağa kaydediliyor...")
        request = RegisterTurtleRequest(
            name=name,
            photo_path=photo_path,
            species=species,
            notes=notes,
        )
        worker = RegisterWorker(self._register_use_case, request)
        worker.signals.finished.connect(self._on_registration_done)
        worker.signals.error.connect(self._on_error)
        worker.start()
        self._active_workers = getattr(self, "_active_workers", [])
        self._active_workers.append(worker)  # GC'den koruma

    def request_add_photo(self, turtle_id: str, photo_path: str) -> None:
        """
        Mevcut kaplumbağaya ek fotoğraf/embedding ekle.
        """
        from turtle_id.ui.workers import AddPhotoWorker  # noqa: PLC0415
        self.signals.processing_started.emit("Fotoğraf ekleniyor...")
        worker = AddPhotoWorker(turtle_id, photo_path, self._image_agent, self._data_agent)
        worker.signals.finished.connect(lambda r: (
            self.signals.processing_finished.emit(),
            self.signals.registration_completed.emit(r),
        ))
        worker.signals.error.connect(self._on_error)
        worker.start()
        self._active_workers = getattr(self, "_active_workers", [])
        self._active_workers.append(worker)

    def request_verification(self, photo_path: str) -> None:
        """
        Doğrulama isteğini arka plan thread'inde çalıştır.
        """
        from turtle_id.ui.workers import VerifyWorker  # noqa: PLC0415
        self.signals.processing_started.emit("Kaplumbağa tanınıyor...")
        request = VerifyTurtleRequest(photo_path=photo_path)
        worker = VerifyWorker(self._verify_use_case, request)
        worker.signals.finished.connect(self._on_verification_done)
        worker.signals.error.connect(self._on_error)
        worker.start()
        self._active_workers = getattr(self, "_active_workers", [])
        self._active_workers.append(worker)

    # ------------------------------------------------------------------ #
    #  Slot'lar — worker thread'lerinden gelen sonuçlar                   #
    # ------------------------------------------------------------------ #

    def _on_registration_done(self, response: RegisterTurtleResponse) -> None:
        self.signals.processing_finished.emit()
        self.signals.registration_completed.emit(response)

    def _on_verification_done(self, response: VerifyTurtleResponse) -> None:
        self.signals.processing_finished.emit()
        self.signals.verification_completed.emit(response)

    def _on_error(self, message: str) -> None:
        self.signals.processing_finished.emit()
        self.signals.error_occurred.emit(message)
