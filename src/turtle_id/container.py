"""
Bağımlılık Enjeksiyon Konteyneri.

Tüm somut implementasyonların birleştiği tek yer.
Üst katmanlar (use case'ler, UI) bu modülden hazır nesne alır;
hangi implementasyonun kullanıldığını bilmez → DIP korunur.

Kullanım:
    container = AppContainer()
    container.init()
    use_case = container.register_turtle_use_case()
"""
from __future__ import annotations

from pathlib import Path

from loguru import logger

from turtle_id.agents.config_agent import ConfigAgent
from turtle_id.agents.data_agent import DataAgent
from turtle_id.agents.image_agent import ImageAgent
from turtle_id.agents.matching_agent import MatchingAgent
from turtle_id.agents.photo_validation_agent import PhotoValidationAgent
from turtle_id.core.use_cases.register_turtle import RegisterTurtleUseCase
from turtle_id.core.use_cases.verify_turtle import VerifyTurtleUseCase
from turtle_id.infrastructure.matching.cosine_matcher import CosineMatcher
from turtle_id.infrastructure.persistence.database import (
    build_engine,
    build_session_factory,
    init_db,
)
from turtle_id.infrastructure.persistence.sqlite_turtle_repo import SQLiteTurtleRepository
from turtle_id.infrastructure.vision.opencv_preprocessor import OpenCVPreprocessor
from turtle_id.infrastructure.vision.timm_extractor import TimmEfficientNetExtractor
from turtle_id.shared.event_bus import EventBus


class AppContainer:
    """
    Uygulama bağımlılık konteyneri.

    Tüm ajanlar ve use case'ler burada tek sefer oluşturulur (singleton benzeri).
    init() çağrılmadan kullanılamaz.
    """

    def __init__(self, settings_path: Path = Path("settings.json")) -> None:
        self._settings_path = settings_path
        self._initialized = False

        # Ajanlar
        self._event_bus: EventBus | None = None
        self._config_agent: ConfigAgent | None = None
        self._validation_agent: PhotoValidationAgent | None = None
        self._image_agent: ImageAgent | None = None
        self._matching_agent: MatchingAgent | None = None
        self._data_agent: DataAgent | None = None

        # Use case'ler
        self._register_use_case: RegisterTurtleUseCase | None = None
        self._verify_use_case: VerifyTurtleUseCase | None = None

    def init(self) -> None:
        """
        Tüm bağımlılıkları oluştur ve ajanları başlat.
        Uygulama başlangıcında bir kez çağrılmalıdır.
        """
        if self._initialized:
            return

        logger.info("AppContainer: başlatılıyor...")

        # 1. EventBus — tüm ajanlar paylaşır
        self._event_bus = EventBus()

        # 2. ConfigAgent — diğer ajanlardan önce başlatılır
        self._config_agent = ConfigAgent(self._event_bus, self._settings_path)
        self._config_agent.start()

        # 3. Veritabanı
        engine = build_engine(self._config_agent.db_path)
        session_factory = build_session_factory(engine)
        init_db(engine)
        repository = SQLiteTurtleRepository(session_factory)

        # 4. Altyapı implementasyonları
        preprocessor = OpenCVPreprocessor()
        extractor = TimmEfficientNetExtractor()
        matcher = CosineMatcher()

        # 5. Ajanlar
        self._validation_agent = PhotoValidationAgent(self._event_bus)
        self._image_agent = ImageAgent(self._event_bus, preprocessor, extractor)
        self._matching_agent = MatchingAgent(
            event_bus=self._event_bus,
            matcher=matcher,
            repository=repository,
            threshold=self._config_agent.similarity_threshold,
            top_k=self._config_agent.top_k_results,
        )
        self._data_agent = DataAgent(self._event_bus, repository)

        # 6. ConfigAgent → MatchingAgent threshold köprüsü
        self._event_bus.subscribe(
            EventType.CONFIG_CHANGED,
            self._on_config_changed,
        )

        # 7. Ajanları başlat
        for agent in [
            self._validation_agent,
            self._image_agent,
            self._matching_agent,
            self._data_agent,
        ]:
            agent.start()

        # 8. Use case'ler
        self._register_use_case = RegisterTurtleUseCase(
            validation_agent=self._validation_agent,
            image_agent=self._image_agent,
            data_agent=self._data_agent,
        )
        self._verify_use_case = VerifyTurtleUseCase(
            validation_agent=self._validation_agent,
            image_agent=self._image_agent,
            matching_agent=self._matching_agent,
            data_agent=self._data_agent,
        )

        self._initialized = True
        logger.info("AppContainer: hazır.")

    def shutdown(self) -> None:
        """Tüm ajanları durdur."""
        for agent in [
            self._data_agent,
            self._matching_agent,
            self._image_agent,
            self._validation_agent,
            self._config_agent,
        ]:
            if agent:
                agent.stop()
        logger.info("AppContainer: kapatıldı.")

    # ------------------------------------------------------------------ #
    #  Public erişimciler                                                  #
    # ------------------------------------------------------------------ #

    @property
    def register_turtle_use_case(self) -> RegisterTurtleUseCase:
        self._assert_initialized()
        return self._register_use_case

    @property
    def verify_turtle_use_case(self) -> VerifyTurtleUseCase:
        self._assert_initialized()
        return self._verify_use_case

    @property
    def config_agent(self) -> ConfigAgent:
        self._assert_initialized()
        return self._config_agent

    @property
    def data_agent(self) -> DataAgent:
        self._assert_initialized()
        return self._data_agent

    @property
    def event_bus(self) -> EventBus:
        self._assert_initialized()
        return self._event_bus

    # ------------------------------------------------------------------ #
    #  Private                                                             #
    # ------------------------------------------------------------------ #

    def _assert_initialized(self) -> None:
        if not self._initialized:
            raise RuntimeError("AppContainer.init() henüz çağrılmadı.")

    def _on_config_changed(self, _event_type, payload: dict) -> None:
        """CONFIG_CHANGED → MatchingAgent threshold güncelle."""
        if payload.get("key") == "similarity_threshold":
            self._matching_agent.update_threshold(float(payload["value"]))


# EventType import'u init metodundan sonra gelmeli (circular import önlemi)
from turtle_id.shared.events import EventType  # noqa: E402
