"""
PhotoValidationAgent birim testleri.
"""
import pytest
from pathlib import Path

from turtle_id.agents.photo_validation_agent import PhotoValidationAgent
from turtle_id.shared.event_bus import EventBus
from turtle_id.shared.events import EventType


@pytest.fixture()
def agent():
    bus = EventBus()
    a = PhotoValidationAgent(bus)
    a.start()
    return a


class TestPhotoValidationAgent:
    def test_olmayan_dosya_hatasi(self, agent):
        result = agent.validate("olmayan/dosya.jpg")
        assert result.is_valid is False
        assert any("bulunamadı" in e for e in result.errors)

    def test_desteklenmeyen_format_hatasi(self, agent):
        result = agent.validate("dosya.gif")
        assert result.is_valid is False
        assert any("format" in e.lower() for e in result.errors)

    def test_gecerli_fotograf_eventbus_yayimlar(self, tmp_path, agent):
        """Geçici geçerli bir PNG oluştur ve doğrula."""
        import numpy as np
        import cv2

        img = np.ones((200, 200, 3), dtype=np.uint8) * 128
        path = tmp_path / "test.jpg"
        cv2.imwrite(str(path), img)

        events = []
        agent._event_bus.subscribe(
            EventType.PHOTO_VALID,
            lambda et, p: events.append(p),
        )
        result = agent.validate(str(path))
        assert result.is_valid is True
        assert len(events) == 1

    def test_gecersiz_fotograf_eventbus_yayimlar(self, agent):
        events = []
        agent._event_bus.subscribe(
            EventType.PHOTO_INVALID,
            lambda et, p: events.append(p),
        )
        agent.validate("yok.jpg")
        assert len(events) == 1
        assert "errors" in events[0]
