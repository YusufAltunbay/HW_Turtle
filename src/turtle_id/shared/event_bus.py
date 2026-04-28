"""
EventBus: Ajanlar arası publish/subscribe iletişim katmanı.

Her ajan EventBus üzerinden olay yayımlar ve dinler.
Bu sayede ajanlar birbirini doğrudan import etmez → düşük bağlılık.
"""
from __future__ import annotations

import threading
from collections import defaultdict
from typing import Callable, Any

from loguru import logger

from turtle_id.shared.events import EventType


Handler = Callable[[EventType, Any], None]


class EventBus:
    """
    Thread-safe publish/subscribe olay yöneticisi.

    Kullanım:
        bus = EventBus()
        bus.subscribe(EventType.EMBEDDING_READY, my_handler)
        bus.publish(EventType.EMBEDDING_READY, payload)
    """

    def __init__(self) -> None:
        self._handlers: dict[EventType, list[Handler]] = defaultdict(list)
        self._lock = threading.Lock()

    def subscribe(self, event_type: EventType, handler: Handler) -> None:
        """Bir olay tipine dinleyici ekle."""
        with self._lock:
            self._handlers[event_type].append(handler)
        logger.debug(f"EventBus: '{handler.__qualname__}' → {event_type.value} dinliyor")

    def unsubscribe(self, event_type: EventType, handler: Handler) -> None:
        """Dinleyiciyi kaldır."""
        with self._lock:
            handlers = self._handlers.get(event_type, [])
            self._handlers[event_type] = [h for h in handlers if h != handler]

    def publish(self, event_type: EventType, payload: Any = None) -> None:
        """
        Bir olay yayımla. Tüm kayıtlı dinleyiciler sırayla çağrılır.
        Dinleyici hataları diğer dinleyicileri engellemez.
        """
        with self._lock:
            handlers = list(self._handlers.get(event_type, []))

        logger.debug(f"EventBus yayım: {event_type.value} → {len(handlers)} dinleyici")

        for handler in handlers:
            try:
                handler(event_type, payload)
            except Exception as exc:
                logger.error(
                    f"EventBus handler hatası [{handler.__qualname__}] "
                    f"olay={event_type.value}: {exc}"
                )

    def clear(self) -> None:
        """Tüm dinleyicileri temizle (test amaçlı)."""
        with self._lock:
            self._handlers.clear()
