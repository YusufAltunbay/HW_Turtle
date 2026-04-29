"""
EventBus birim testleri.
"""
import threading
import pytest

from turtle_id.shared.event_bus import EventBus
from turtle_id.shared.events import EventType


class TestEventBus:
    def setup_method(self):
        self.bus = EventBus()

    def test_subscribe_ve_publish(self):
        received = []
        self.bus.subscribe(EventType.TURTLE_SAVED, lambda et, p: received.append(p))
        self.bus.publish(EventType.TURTLE_SAVED, {"name": "Ninja"})
        assert received == [{"name": "Ninja"}]

    def test_birden_fazla_dinleyici(self):
        log = []
        self.bus.subscribe(EventType.EMBEDDING_READY, lambda et, p: log.append("A"))
        self.bus.subscribe(EventType.EMBEDDING_READY, lambda et, p: log.append("B"))
        self.bus.publish(EventType.EMBEDDING_READY, None)
        assert log == ["A", "B"]

    def test_farkli_olay_tipleri_karismiyor(self):
        saved = []
        self.bus.subscribe(EventType.TURTLE_SAVED, lambda et, p: saved.append(p))
        self.bus.publish(EventType.MATCH_FOUND, {"irrelevant": True})
        assert saved == []

    def test_unsubscribe(self):
        calls = []
        handler = lambda et, p: calls.append(p)
        self.bus.subscribe(EventType.DATA_ERROR, handler)
        self.bus.publish(EventType.DATA_ERROR, "hata1")
        self.bus.unsubscribe(EventType.DATA_ERROR, handler)
        self.bus.publish(EventType.DATA_ERROR, "hata2")
        assert calls == ["hata1"]

    def test_hata_veren_handler_digeri_engellemez(self):
        results = []

        def kotu_handler(et, p):
            raise RuntimeError("Handler patladı!")

        def iyi_handler(et, p):
            results.append(p)

        self.bus.subscribe(EventType.CONFIG_CHANGED, kotu_handler)
        self.bus.subscribe(EventType.CONFIG_CHANGED, iyi_handler)
        self.bus.publish(EventType.CONFIG_CHANGED, "test")
        assert results == ["test"]

    def test_thread_safe_publish(self):
        """Çoklu thread'den eş zamanlı publish güvenli olmalı."""
        received = []
        lock = threading.Lock()

        def handler(et, p):
            with lock:
                received.append(p)

        self.bus.subscribe(EventType.PROCESSING_PROGRESS, handler)

        threads = [
            threading.Thread(
                target=self.bus.publish,
                args=(EventType.PROCESSING_PROGRESS, i),
            )
            for i in range(20)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(received) == 20

    def test_clear(self):
        calls = []
        self.bus.subscribe(EventType.TURTLE_SAVED, lambda et, p: calls.append(p))
        self.bus.clear()
        self.bus.publish(EventType.TURTLE_SAVED, "test")
        assert calls == []
