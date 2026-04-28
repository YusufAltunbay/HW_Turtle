"""
MatchResult domain modeli.
Eşleştirme ajanının ürettiği doğrulama sonucunu taşır.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from turtle_id.core.models.turtle import Turtle


@dataclass
class MatchResult:
    """
    Bir doğrulama sorgusunun sonucu.

    Attributes:
        is_match: Eşleşme bulundu mu?
        similarity_score: En yüksek cosine benzerlik skoru (0.0 - 1.0).
        threshold_used: Kullanılan eşik değeri.
        matched_turtle_id: Eşleşen kaplumbağanın ID'si (eşleşme yoksa None).
        matched_turtle: Eşleşen kaplumbağa nesnesi (sonradan doldurulur).
        top_candidates: En iyi k adayın (turtle_id, skor) listesi.
    """

    is_match: bool
    similarity_score: float
    threshold_used: float
    matched_turtle_id: UUID | None = None
    matched_turtle: "Turtle | None" = None
    top_candidates: list[tuple[UUID, float]] = field(default_factory=list)

    @property
    def confidence(self) -> float:
        """
        Güven skoru: benzerlik skorunun eşiğe oranı (0.0 - 1.0 arası kırpılmış).
        Eşik altındaki skorlar için 0.0 döner.
        """
        if not self.is_match:
            return 0.0
        return min(self.similarity_score / max(self.threshold_used, 1e-9), 1.0)

    @classmethod
    def no_match(cls, similarity_score: float, threshold: float) -> "MatchResult":
        """Eşleşme bulunamadığında kullanılacak fabrika metodu."""
        return cls(
            is_match=False,
            similarity_score=similarity_score,
            threshold_used=threshold,
        )

    def __repr__(self) -> str:
        status = "EŞLEŞME VAR" if self.is_match else "EŞLEŞME YOK"
        return (
            f"MatchResult({status}, score={self.similarity_score:.4f}, "
            f"threshold={self.threshold_used:.2f}, "
            f"turtle={self.matched_turtle_id!s:.8 if self.matched_turtle_id else 'None'})"
        )
