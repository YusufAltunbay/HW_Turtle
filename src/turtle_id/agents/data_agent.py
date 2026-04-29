"""
DataAgent: Kaplumbağa kayıtlarının CRUD işlemlerini yöneten ajan.

Sorumluluk:
  - Yeni kaplumbağa kaydet
  - ID ile kaplumbağa getir
  - Tüm kaplumbağaları listele
  - Mevcut kaplumbağaya yeni embedding/fotoğraf ekle
  - Doğrulama logunu kaydet

ITurtleRepository arayüzü üzerinden çalışır; SQLite detayı görmez.
"""
from __future__ import annotations

from uuid import UUID

from loguru import logger

from turtle_id.agents.base_agent import BaseAgent
from turtle_id.core.models.embedding import Embedding
from turtle_id.core.models.match_result import MatchResult
from turtle_id.core.models.turtle import Turtle
from turtle_id.core.ports.i_turtle_repository import ITurtleRepository
from turtle_id.shared.event_bus import EventBus
from turtle_id.shared.events import EventType


class DataAgent(BaseAgent):
    """
    Kalıcı depolama işlemlerini kapsülleyen ajan.

    Args:
        event_bus:   Paylaşılan EventBus.
        repository:  Veri deposu implementasyonu (ITurtleRepository).
    """

    def __init__(self, event_bus: EventBus, repository: ITurtleRepository) -> None:
        super().__init__(event_bus)
        self._repository = repository

    @property
    def name(self) -> str:
        return "data_agent"

    def _register_handlers(self) -> None:
        """MATCH_FOUND olayını dinle → doğrulama logunu otomatik kaydet."""
        self._subscribe(EventType.MATCH_FOUND, self._on_match_found)
        self._subscribe(EventType.MATCH_NOT_FOUND, self._on_match_not_found)

    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #

    def save_turtle(self, turtle: Turtle) -> Turtle:
        """Kaplumbağa kaydını veritabanına kaydet."""
        try:
            saved = self._repository.save(turtle)
            self._publish(EventType.TURTLE_SAVED, saved)
            logger.info(f"DataAgent: kaplumbağa kaydedildi — {saved.name!r}")
            return saved
        except Exception as exc:
            self._publish(EventType.DATA_ERROR, {"error": str(exc)})
            logger.error(f"DataAgent save_turtle hatası: {exc}")
            raise

    def get_turtle(self, turtle_id: UUID) -> Turtle | None:
        """ID ile kaplumbağayı getir."""
        try:
            turtle = self._repository.find_by_id(turtle_id)
            if turtle:
                self._publish(EventType.TURTLE_LOADED, turtle)
            return turtle
        except Exception as exc:
            self._publish(EventType.DATA_ERROR, {"error": str(exc)})
            logger.error(f"DataAgent get_turtle hatası: {exc}")
            raise

    def list_turtles(self) -> list[Turtle]:
        """Tüm kayıtlı kaplumbağaları döndür."""
        try:
            return self._repository.find_all()
        except Exception as exc:
            self._publish(EventType.DATA_ERROR, {"error": str(exc)})
            logger.error(f"DataAgent list_turtles hatası: {exc}")
            raise

    def add_embedding(self, embedding: Embedding) -> Embedding:
        """Mevcut bir kaplumbağaya yeni embedding/fotoğraf ekle."""
        try:
            saved = self._repository.add_embedding(embedding)
            logger.info(
                f"DataAgent: embedding eklendi — "
                f"turtle_id={embedding.turtle_id!s:.8}"
            )
            return saved
        except Exception as exc:
            self._publish(EventType.DATA_ERROR, {"error": str(exc)})
            logger.error(f"DataAgent add_embedding hatası: {exc}")
            raise

    # ------------------------------------------------------------------ #
    #  EventBus handler'ları (otomatik log)                               #
    # ------------------------------------------------------------------ #

    def _on_match_found(self, _event_type: EventType, result: MatchResult) -> None:
        """MATCH_FOUND olayında doğrulama logunu kaydet."""
        self._save_verification_log(result)

    def _on_match_not_found(self, _event_type: EventType, result: MatchResult) -> None:
        """MATCH_NOT_FOUND olayında da log kaydet."""
        self._save_verification_log(result)

    def _save_verification_log(self, result: MatchResult) -> None:
        """Doğrulama geçmişini VerificationLogORM'a yaz."""
        try:
            from turtle_id.infrastructure.persistence.models import VerificationLogORM  # noqa: PLC0415
            from uuid import uuid4  # noqa: PLC0415
            from datetime import datetime, timezone  # noqa: PLC0415

            # Session factory doğrudan erişim — repository'nin private session factory'sini kullan
            if hasattr(self._repository, "_session_factory"):
                with self._repository._session_factory() as session:
                    log = VerificationLogORM(
                        id=str(uuid4()),
                        query_photo_path="",  # use case katmanı doldurur
                        matched_turtle_id=(
                            str(result.matched_turtle_id) if result.matched_turtle_id else None
                        ),
                        similarity_score=result.similarity_score,
                        confidence_score=result.confidence,
                        threshold_used=result.threshold_used,
                        is_match=result.is_match,
                        verified_at=datetime.now(timezone.utc).replace(tzinfo=None),
                    )
                    session.add(log)
                    session.commit()
        except Exception as exc:
            logger.warning(f"DataAgent: doğrulama logu kaydedilemedi: {exc}")
