"""
ConfigAgent: Uygulama ayarlarını merkezi olarak yöneten singleton ajan.

Sorumluluk:
  - settings.json'dan ayarları oku/yaz
  - Runtime'da ayar değişikliklerini EventBus üzerinden yayımla
  - MatchingAgent'ın threshold değerini güncelle (CONFIG_CHANGED olayı)
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from loguru import logger

from turtle_id.agents.base_agent import BaseAgent
from turtle_id.shared.event_bus import EventBus
from turtle_id.shared.events import EventType

_DEFAULT_SETTINGS_PATH = Path("settings.json")

_DEFAULTS: dict[str, Any] = {
    "similarity_threshold": 0.82,
    "top_k_results": 3,
    "model_name": "efficientnet_b0",
    "min_image_width": 100,
    "min_image_height": 100,
    "blur_threshold": 50.0,
    "db_path": "data/turtle_db.sqlite",
}


class ConfigAgent(BaseAgent):
    """
    Uygulama ayarları yöneticisi.

    Singleton olarak kullanılmalıdır; tüm ajanlar aynı instance'ı paylaşır.

    Args:
        event_bus:     Paylaşılan EventBus.
        settings_path: settings.json dosyasının yolu.
    """

    def __init__(
        self,
        event_bus: EventBus,
        settings_path: Path = _DEFAULT_SETTINGS_PATH,
    ) -> None:
        super().__init__(event_bus)
        self._settings_path = settings_path
        self._settings: dict[str, Any] = dict(_DEFAULTS)
        self._load_if_exists()

    @property
    def name(self) -> str:
        return "config_agent"

    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #

    def get(self, key: str, default: Any = None) -> Any:
        """Ayar değerini döndür."""
        return self._settings.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """
        Ayar değerini güncelle ve CONFIG_CHANGED yayımla.
        MatchingAgent gibi ilgili ajanlar bu olayı dinleyerek kendini günceller.
        """
        old_value = self._settings.get(key)
        self._settings[key] = value
        self._publish(EventType.CONFIG_CHANGED, {"key": key, "value": value, "old_value": old_value})
        logger.info(f"ConfigAgent: {key!r} → {old_value!r} → {value!r}")

    def save(self) -> None:
        """Mevcut ayarları settings.json'a yaz."""
        try:
            self._settings_path.write_text(
                json.dumps(self._settings, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            logger.info(f"ConfigAgent: ayarlar kaydedildi → {self._settings_path}")
        except Exception as exc:
            logger.error(f"ConfigAgent: ayarlar kaydedilemedi: {exc}")

    # Kısayol property'leri — sık kullanılan ayarlar için tip güvenliği
    @property
    def similarity_threshold(self) -> float:
        return float(self._settings.get("similarity_threshold", _DEFAULTS["similarity_threshold"]))

    @property
    def top_k_results(self) -> int:
        return int(self._settings.get("top_k_results", _DEFAULTS["top_k_results"]))

    @property
    def db_path(self) -> str:
        return str(self._settings.get("db_path", _DEFAULTS["db_path"]))

    # ------------------------------------------------------------------ #
    #  Private                                                             #
    # ------------------------------------------------------------------ #

    def _load_if_exists(self) -> None:
        if self._settings_path.exists():
            try:
                data = json.loads(self._settings_path.read_text(encoding="utf-8"))
                self._settings.update(data)
                logger.info(f"ConfigAgent: ayarlar yüklendi ← {self._settings_path}")
            except Exception as exc:
                logger.warning(f"ConfigAgent: ayarlar yüklenemedi, varsayılanlar kullanılıyor: {exc}")
