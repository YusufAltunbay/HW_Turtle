"""
VerifyTurtleUseCase: Fotoğraftan kaplumbağa doğrulama iş akışı.

Koordinasyon:
  1. PhotoValidationAgent → fotoğraf geçerli mi?
  2. ImageAgent → sorgu embedding'i üret (geçici turtle_id ile)
  3. MatchingAgent → veritabanıyla karşılaştır
  4. Eşleşme varsa DataAgent → tam Turtle nesnesini getir
  5. Sonucu döndür
"""
from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

from loguru import logger

from turtle_id.agents.data_agent import DataAgent
from turtle_id.agents.image_agent import ImageAgent
from turtle_id.agents.matching_agent import MatchingAgent
from turtle_id.agents.photo_validation_agent import PhotoValidationAgent
from turtle_id.core.models.match_result import MatchResult
from turtle_id.core.models.turtle import Turtle


@dataclass(frozen=True)
class VerifyTurtleRequest:
    """Doğrulama isteği veri taşıyıcısı."""
    photo_path: str


@dataclass(frozen=True)
class VerifyTurtleResponse:
    """Doğrulama sonucu veri taşıyıcısı."""
    success: bool                       # Teknik başarı (hata yok mu?)
    match_result: MatchResult | None = None
    turtle: Turtle | None = None        # Eşleşen kaplumbağa (varsa)
    errors: list[str] = None
    warnings: list[str] = None

    def __post_init__(self):
        object.__setattr__(self, "errors", self.errors or [])
        object.__setattr__(self, "warnings", self.warnings or [])

    @property
    def is_identified(self) -> bool:
        """Kaplumbağa başarıyla tanındı mı?"""
        return self.success and self.match_result is not None and self.match_result.is_match


class VerifyTurtleUseCase:
    """
    Verilen fotoğraftaki kaplumbağayı tanıma iş akışını orkestre eder.

    Args:
        validation_agent: Fotoğraf doğrulama ajanı.
        image_agent:      Embedding üretim ajanı.
        matching_agent:   Eşleştirme ajanı.
        data_agent:       Veritabanı sorgulama ajanı.
    """

    def __init__(
        self,
        validation_agent: PhotoValidationAgent,
        image_agent: ImageAgent,
        matching_agent: MatchingAgent,
        data_agent: DataAgent,
    ) -> None:
        self._validation_agent = validation_agent
        self._image_agent = image_agent
        self._matching_agent = matching_agent
        self._data_agent = data_agent

    def execute(self, request: VerifyTurtleRequest) -> VerifyTurtleResponse:
        """
        Doğrulama iş akışını çalıştır.

        Args:
            request: Doğrulama isteği (fotoğraf yolu).

        Returns:
            VerifyTurtleResponse: Tanıma sonucu ve (varsa) kaplumbağa bilgileri.
        """
        logger.info(f"VerifyTurtleUseCase: başladı — {request.photo_path!r}")

        # Adım 1: Fotoğraf doğrulama
        validation = self._validation_agent.validate(request.photo_path)
        if not validation.is_valid:
            logger.warning(f"VerifyTurtleUseCase: validasyon başarısız — {validation.errors}")
            return VerifyTurtleResponse(
                success=False,
                errors=validation.errors,
                warnings=validation.warnings,
            )

        # Adım 2: Sorgu embedding'i üret (geçici uuid — veritabanına kaydedilmez)
        query_embedding = self._image_agent.process(request.photo_path, uuid4())

        # Adım 3: Eşleştirme
        match_result = self._matching_agent.match(query_embedding.vector)

        # Adım 4: Eşleşme varsa kaplumbağa bilgilerini getir
        turtle: Turtle | None = None
        if match_result.is_match and match_result.matched_turtle_id:
            turtle = self._data_agent.get_turtle(match_result.matched_turtle_id)
            match_result.matched_turtle = turtle

        if match_result.is_match:
            logger.info(
                f"VerifyTurtleUseCase: TANIMLANDI — "
                f"{repr(turtle.name) if turtle else '?'}, "
                f"güven={match_result.confidence:.2%}"
            )
        else:
            logger.info(
                f"VerifyTurtleUseCase: tanımlanamadı — "
                f"en yüksek skor={match_result.similarity_score:.4f}"
            )

        return VerifyTurtleResponse(
            success=True,
            match_result=match_result,
            turtle=turtle,
            warnings=validation.warnings,
        )
