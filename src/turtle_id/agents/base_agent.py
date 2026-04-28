"""
BaseAgent: Tüm ajanların türediği soyut temel sınıf.

Her ajan:
  - Yaşam döngüsü yönetimi (start/stop)
  - EventBus erişimi (publish/subscribe)
  - Loguru tabanlı loglama
  - Sağlık durumu kontrolü
sağlar.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum, auto

from loguru import logger

from turtle_id.shared.event_bus import EventBus
from turtle_id.shared.events import EventType


class AgentStatus(Enum):
    IDLE = auto()
    BUSY = auto()
    ERROR = auto()
    STOPPED = auto()


class BaseAgent(ABC):
    """
    Tüm ajanların uyması gereken temel sözleşme.

    Args:
        event_bus: Ajanlar arası iletişim için paylaşılan EventBus örneği.
    """

    def __init__(self, event_bus: EventBus) -> None:
        self._event_bus = event_bus
        self._status = AgentStatus.IDLE
        self._logger = logger.bind(agent=self.name)

    @property
    @abstractmethod
    def name(self) -> str:
        """Ajanın benzersiz adı (loglama ve debug için)."""

    def start(self) -> None:
        """Ajanı başlat ve dinleyicileri kaydet."""
        self._status = AgentStatus.IDLE
        self._register_handlers()
        self._logger.info(f"Ajan başlatıldı: {self.name}")

    def stop(self) -> None:
        """Ajanı durdur ve kaynakları serbest bırak."""
        self._status = AgentStatus.STOPPED
        self._logger.info(f"Ajan durduruldu: {self.name}")

    def health_check(self) -> bool:
        """Ajan sağlıklı mı? ERROR veya STOPPED ise False."""
        return self._status not in (AgentStatus.ERROR, AgentStatus.STOPPED)

    @property
    def status(self) -> AgentStatus:
        return self._status

    def _register_handlers(self) -> None:
        """
        Alt sınıflar bu metodu override ederek EventBus dinleyicilerini kaydeder.
        Varsayılan: hiçbir şey kaydetme.
        """

    def _publish(self, event_type: EventType, payload: object = None) -> None:
        """EventBus'a olay yayımla (kısayol)."""
        self._event_bus.publish(event_type, payload)

    def _subscribe(self, event_type: EventType, handler: object) -> None:
        """EventBus'a dinleyici kaydet (kısayol)."""
        self._event_bus.subscribe(event_type, handler)

    def _set_busy(self) -> None:
        self._status = AgentStatus.BUSY

    def _set_idle(self) -> None:
        self._status = AgentStatus.IDLE

    def _set_error(self) -> None:
        self._status = AgentStatus.ERROR

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r}, status={self._status.name})"
