"""
CosineMatcher: IMatcher'ın scikit-learn cosine similarity implementasyonu.

L2 normalize vektörler arasında cosine similarity hesaplar.
L2 normalize vektörler için: cosine_similarity = dot product.
"""
from __future__ import annotations

from uuid import UUID

import numpy as np
from loguru import logger
from sklearn.metrics.pairwise import cosine_similarity

from turtle_id.core.models.embedding import Embedding
from turtle_id.core.models.match_result import MatchResult
from turtle_id.core.ports.i_matcher import IMatcher


class CosineMatcher(IMatcher):
    """
    Cosine benzerliği tabanlı eşleştirici.

    Tüm aday embedding'lere karşı tek seferde matris çarpımı yapar.
    Scikit-learn'ün vektörleştirilmiş cosine_similarity fonksiyonunu kullanır.
    """

    def find_best_match(
        self,
        query_vector: np.ndarray,
        candidates: list[Embedding],
        threshold: float,
        top_k: int = 3,
    ) -> MatchResult:
        """
        Sorgu vektörünü tüm adaylara karşı karşılaştır.

        Args:
            query_vector: (D,) float32 sorgu vektörü.
            candidates:   Veritabanındaki tüm embedding kayıtları.
            threshold:    Eşleşme kabul eşiği (0.0 - 1.0).
            top_k:        Döndürülecek en iyi aday sayısı.

        Returns:
            MatchResult nesnesi.
        """
        if not candidates:
            logger.warning("CosineMatcher: aday embedding listesi boş.")
            return MatchResult.no_match(similarity_score=0.0, threshold=threshold)

        query_2d = query_vector.reshape(1, -1)
        candidate_matrix = np.stack([c.vector for c in candidates])  # (N, D)

        scores: np.ndarray = cosine_similarity(query_2d, candidate_matrix)[0]  # (N,)

        top_indices = np.argsort(scores)[::-1][:top_k]
        top_candidates = [
            (candidates[i].turtle_id, float(scores[i]))
            for i in top_indices
        ]

        best_index = int(np.argmax(scores))
        best_score = float(scores[best_index])
        best_turtle_id: UUID = candidates[best_index].turtle_id

        is_match = best_score >= threshold

        logger.debug(
            f"CosineMatcher: best_score={best_score:.4f}, "
            f"threshold={threshold:.2f}, match={is_match}"
        )

        return MatchResult(
            is_match=is_match,
            similarity_score=best_score,
            threshold_used=threshold,
            matched_turtle_id=best_turtle_id if is_match else None,
            top_candidates=top_candidates,
        )
