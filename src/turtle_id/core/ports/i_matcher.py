"""
IMatcher port arayüzü.

Bağımlılık tersim (DIP) için soyut sözleşme.
Somut implementasyon: infrastructure/matching/cosine_matcher.py

Açık/Kapalı Prensibi (OCP): Yeni bir eşleştirme algoritması (FAISS vb.)
eklemek için bu arayüzü implemente eden yeni bir sınıf yazmak yeterlidir;
MatchingAgent'ın kodu değişmez.
"""
from abc import ABC, abstractmethod
from uuid import UUID

import numpy as np

from turtle_id.core.models.embedding import Embedding
from turtle_id.core.models.match_result import MatchResult


class IMatcher(ABC):
    """
    Sorgu embedding'ini kayıtlı embedding listesiyle karşılaştırır.
    """

    @abstractmethod
    def find_best_match(
        self,
        query_vector: np.ndarray,
        candidates: list[Embedding],
        threshold: float,
        top_k: int = 3,
    ) -> MatchResult:
        """
        En iyi eşleşmeyi bul.

        Args:
            query_vector: Doğrulanacak fotoğrafın embedding vektörü.
            candidates: Veritabanındaki tüm embedding kayıtları.
            threshold: Eşleşme kabul eşiği (0.0 - 1.0).
            top_k: Döndürülecek aday sayısı.

        Returns:
            MatchResult: Eşleşme sonucu ve güven skoru.
        """
