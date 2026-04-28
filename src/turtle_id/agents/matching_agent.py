"""
MatchingAgent: Sorgu embedding'ini kayıtlı embedding'lerle karşılaştıran ajan.

Sorumluluk:
  - ITurtleRepository'den tüm embedding'leri çek
  - IMatcher ile en iyi eşleşmeyi bul
  - MatchResult üret ve EventBus'a yayımla
"""
from __future__ import annotations

import numpy as np
from loguru import logger

from turtle_id.agents.base_agent import BaseAgent
from turtle_id.core.models.match_result import MatchResult
from turtle_id.core.ports.i_matcher import IMatcher
from turtle_id.core.ports.i_turtle_repository import ITurtleRepository
from turtle_id.shared.event_bus import EventBus
from turtle_id.shared.events import EventType

_DEFAULT_THRESHOLD = 0.82
_DEFAULT_TOP_K = 3


class MatchingAgent(BaseAgent):
    """
    Kaplumbağa doğrulama mantığı.

    Args:
        event_bus:   Paylaşılan EventBus.
        matcher:     Eşleştirme algoritması (IMatcher).
        repository:  Veritabanı erişimi (ITurtleRepository).
        threshold:   Eşleşme kabul eşiği (varsayılan 0.82).
        top_k:       Döndürülecek aday sayısı.
    """

    def __init__(
        self,
        event_bus: EventBus,
        matcher: IMatcher,
        repository: ITurtleRepository,
        threshold: float = _DEFAULT_THRESHOLD,
        top_k: int = _DEFAULT_TOP_K,
    ) -> None:
        super().__init__(event_bus)
        self._matcher = matcher
        self._repository = repository
        self._threshold = threshold
        self._top_k = top_k

    @property
    def name(self) -> str:
        return "matching_agent"

    @property
    def threshold(self) -> float:
        return self._threshold

    def update_threshold(self, value: float) -> None:
        """Eşleşme eşiğini güncelle (ConfigAgent tarafından çağrılır)."""
        if not 0.0 < value <= 1.0:
            raise ValueError(f"Geçersiz eşik değeri: {value!r}. 0 < threshold <= 1.0 olmalı.")
        self._threshold = value
        logger.info(f"MatchingAgent: eşik güncellendi → {value:.2f}")

    def match(self, query_vector: np.ndarray) -> MatchResult:
        """
        Sorgu vektörünü veritabanındaki tüm embedding'lerle karşılaştır.

        Args:
            query_vector: (D,) float32 sorgu vektörü.

        Returns:
            MatchResult: Eşleşme sonucu.
        """
        self._set_busy()
        self._publish(EventType.MATCHING_STARTED, {"threshold": self._threshold})

        try:
            all_embeddings = self._repository.get_all_embeddings()
            result = self._matcher.find_best_match(
                query_vector=query_vector,
                candidates=all_embeddings,
                threshold=self._threshold,
                top_k=self._top_k,
            )

            if result.is_match:
                self._publish(EventType.MATCH_FOUND, result)
                logger.info(
                    f"MatchingAgent: EŞLEŞME BULUNDU — "
                    f"turtle_id={result.matched_turtle_id!s:.8}, "
                    f"score={result.similarity_score:.4f}"
                )
            else:
                self._publish(EventType.MATCH_NOT_FOUND, result)
                logger.info(
                    f"MatchingAgent: eşleşme yok — "
                    f"en yüksek skor={result.similarity_score:.4f}, "
                    f"eşik={self._threshold:.2f}"
                )

            self._set_idle()
            return result

        except Exception as exc:
            self._set_error()
            logger.error(f"MatchingAgent hata: {exc}")
            raise
