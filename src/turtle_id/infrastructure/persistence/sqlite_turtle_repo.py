"""
SQLiteTurtleRepository: ITurtleRepository'nin SQLite implementasyonu.

Domain modelleri (Turtle, Embedding) ile ORM modelleri (TurtleORM, EmbeddingORM)
arasındaki dönüşümü bu sınıf yönetir. Üst katmanlar (use case'ler, ajanlar)
sadece ITurtleRepository arayüzünü bilir; SQLite detayı burada kapsüllenir.
"""
from __future__ import annotations

from uuid import UUID

import numpy as np
from loguru import logger
from sqlalchemy.orm import Session, sessionmaker

from turtle_id.core.models.embedding import Embedding
from turtle_id.core.models.turtle import Turtle
from turtle_id.core.ports.i_turtle_repository import ITurtleRepository
from turtle_id.infrastructure.persistence.models import (
    EmbeddingORM,
    TurtleORM,
)


class SQLiteTurtleRepository(ITurtleRepository):
    """
    ITurtleRepository'nin SQLite + SQLAlchemy implementasyonu.

    Args:
        session_factory: SQLAlchemy sessionmaker örneği.
    """

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    # ------------------------------------------------------------------ #
    #  Yardımcı: Domain ↔ ORM dönüşümleri                                 #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _to_orm(turtle: Turtle) -> TurtleORM:
        return TurtleORM(
            id=str(turtle.id),
            name=turtle.name,
            species=turtle.species,
            notes=turtle.notes,
            primary_photo_path=turtle.primary_photo_path,
            registration_date=turtle.registration_date,
            is_active=True,
        )

    @staticmethod
    def _embedding_to_orm(emb: Embedding) -> EmbeddingORM:
        return EmbeddingORM(
            id=str(emb.id),
            turtle_id=str(emb.turtle_id),
            vector_blob=emb.vector.astype(np.float32).tobytes(),
            vector_dim=emb.dimension,
            photo_path=emb.photo_path,
            model_name=emb.model_name,
            captured_at=emb.captured_at,
        )

    @staticmethod
    def _embedding_from_orm(row: EmbeddingORM) -> Embedding:
        vector = np.frombuffer(row.vector_blob, dtype=np.float32).copy()
        return Embedding(
            id=UUID(row.id),
            turtle_id=UUID(row.turtle_id),
            vector=vector,
            photo_path=row.photo_path,
            model_name=row.model_name,
            captured_at=row.captured_at,
        )

    @staticmethod
    def _turtle_from_orm(row: TurtleORM) -> Turtle:
        turtle = Turtle(
            id=UUID(row.id),
            name=row.name,
            species=row.species or "",
            notes=row.notes or "",
            primary_photo_path=row.primary_photo_path,
            registration_date=row.registration_date,
        )
        for emb_row in row.embeddings:
            turtle.add_embedding(SQLiteTurtleRepository._embedding_from_orm(emb_row))
        return turtle

    # ------------------------------------------------------------------ #
    #  ITurtleRepository implementasyonu                                   #
    # ------------------------------------------------------------------ #

    def save(self, turtle: Turtle) -> Turtle:
        """Kaplumbağayı ve varsa embedding'lerini kaydet."""
        with self._session_factory() as session:
            orm = self._to_orm(turtle)
            for emb in turtle.embeddings:
                orm.embeddings.append(self._embedding_to_orm(emb))
            session.add(orm)
            session.commit()
            logger.info(f"Kaplumbağa kaydedildi: {turtle.name!r} (id={turtle.id!s:.8})")
        return turtle

    def find_by_id(self, turtle_id: UUID) -> Turtle | None:
        """ID ile kaplumbağa sorgula."""
        with self._session_factory() as session:
            row = session.get(TurtleORM, str(turtle_id))
            if row is None or not row.is_active:
                return None
            return self._turtle_from_orm(row)

    def find_all(self) -> list[Turtle]:
        """Tüm aktif kaplumbağaları döndür."""
        with self._session_factory() as session:
            rows = session.query(TurtleORM).filter_by(is_active=True).all()
            return [self._turtle_from_orm(r) for r in rows]

    def update(self, turtle: Turtle) -> Turtle:
        """Kaplumbağa meta verisini güncelle."""
        with self._session_factory() as session:
            row = session.get(TurtleORM, str(turtle.id))
            if row is None:
                raise ValueError(f"Kaplumbağa bulunamadı: {turtle.id}")
            row.name = turtle.name
            row.species = turtle.species
            row.notes = turtle.notes
            row.primary_photo_path = turtle.primary_photo_path
            session.commit()
            logger.info(f"Kaplumbağa güncellendi: id={turtle.id!s:.8}")
        return turtle

    def delete(self, turtle_id: UUID) -> None:
        """Soft delete: is_active = False."""
        with self._session_factory() as session:
            row = session.get(TurtleORM, str(turtle_id))
            if row is None:
                raise ValueError(f"Kaplumbağa bulunamadı: {turtle_id}")
            row.is_active = False
            session.commit()
            logger.info(f"Kaplumbağa silindi (soft): id={turtle_id!s:.8}")

    def add_embedding(self, embedding: Embedding) -> Embedding:
        """Mevcut bir kaplumbağaya yeni embedding ekle."""
        with self._session_factory() as session:
            row = session.get(TurtleORM, str(embedding.turtle_id))
            if row is None:
                raise ValueError(f"Kaplumbağa bulunamadı: {embedding.turtle_id}")
            orm = self._embedding_to_orm(embedding)
            session.add(orm)
            session.commit()
            logger.info(
                f"Embedding eklendi: turtle_id={embedding.turtle_id!s:.8}, "
                f"dim={embedding.dimension}"
            )
        return embedding

    def get_all_embeddings(self) -> list[Embedding]:
        """
        Tüm aktif kaplumbağaların embedding'lerini döndür.
        Eşleştirme ajanı tarafından kullanılır.
        """
        with self._session_factory() as session:
            rows = (
                session.query(EmbeddingORM)
                .join(TurtleORM, TurtleORM.id == EmbeddingORM.turtle_id)
                .filter(TurtleORM.is_active == True)  # noqa: E712
                .all()
            )
            return [self._embedding_from_orm(r) for r in rows]

    def get_embeddings_by_turtle(self, turtle_id: UUID) -> list[Embedding]:
        """Belirli bir kaplumbağanın embedding'lerini döndür."""
        with self._session_factory() as session:
            rows = (
                session.query(EmbeddingORM)
                .filter_by(turtle_id=str(turtle_id))
                .all()
            )
            return [self._embedding_from_orm(r) for r in rows]
