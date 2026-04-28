"""
RegisterTurtleUseCase: Yeni kaplumbağa kayıt iş akışı.

Koordinasyon:
  1. PhotoValidationAgent → fotoğraf geçerli mi?
  2. ImageAgent → fotoğraftan embedding üret
  3. Turtle domain nesnesi oluştur
  4. DataAgent → veritabanına kaydet

Use case'ler ajan implementasyonlarını değil, ajanları doğrudan kullanır.
Bu katman iş akışını kurgular; teknik detay ajanlarda kapsüllenir.
"""
from __future__ import annotations

from dataclasses import dataclass

from loguru import logger

from turtle_id.agents.data_agent import DataAgent
from turtle_id.agents.image_agent import ImageAgent
from turtle_id.agents.photo_validation_agent import PhotoValidationAgent
from turtle_id.core.models.turtle import Turtle


@dataclass(frozen=True)
class RegisterTurtleRequest:
    """Kayıt isteği veri taşıyıcısı (Value Object)."""
    name: str
    photo_path: str
    species: str = ""
    notes: str = ""


@dataclass(frozen=True)
class RegisterTurtleResponse:
    """Kayıt sonucu veri taşıyıcısı."""
    success: bool
    turtle: Turtle | None = None
    errors: list[str] = None
    warnings: list[str] = None

    def __post_init__(self):
        object.__setattr__(self, "errors", self.errors or [])
        object.__setattr__(self, "warnings", self.warnings or [])


class RegisterTurtleUseCase:
    """
    Yeni kaplumbağa kayıt iş akışını orkestre eder.

    Args:
        validation_agent: Fotoğraf doğrulama ajanı.
        image_agent:      Embedding üretim ajanı.
        data_agent:       Veritabanı kayıt ajanı.
    """

    def __init__(
        self,
        validation_agent: PhotoValidationAgent,
        image_agent: ImageAgent,
        data_agent: DataAgent,
    ) -> None:
        self._validation_agent = validation_agent
        self._image_agent = image_agent
        self._data_agent = data_agent

    def execute(self, request: RegisterTurtleRequest) -> RegisterTurtleResponse:
        """
        Kayıt iş akışını çalıştır.

        Args:
            request: Kayıt isteği (isim, fotoğraf yolu, tür, notlar).

        Returns:
            RegisterTurtleResponse: Başarı/hata durumu ve kaydedilen Turtle.
        """
        logger.info(f"RegisterTurtleUseCase: başladı — {request.name!r}")

        # Adım 1: Fotoğraf doğrulama
        validation = self._validation_agent.validate(request.photo_path)
        if not validation.is_valid:
            logger.warning(f"RegisterTurtleUseCase: validasyon başarısız — {validation.errors}")
            return RegisterTurtleResponse(
                success=False,
                errors=validation.errors,
                warnings=validation.warnings,
            )

        # Adım 2: Turtle nesnesi oluştur (ID otomatik üretilir)
        turtle = Turtle(
            name=request.name,
            species=request.species,
            notes=request.notes,
            primary_photo_path=request.photo_path,
        )

        # Adım 3: Fotoğraftan embedding üret
        embedding = self._image_agent.process(request.photo_path, turtle.id)
        turtle.add_embedding(embedding)

        # Adım 4: Veritabanına kaydet
        saved_turtle = self._data_agent.save_turtle(turtle)

        logger.info(
            f"RegisterTurtleUseCase: tamamlandı — "
            f"{saved_turtle.name!r}, id={saved_turtle.id!s:.8}"
        )
        return RegisterTurtleResponse(
            success=True,
            turtle=saved_turtle,
            warnings=validation.warnings,
        )
