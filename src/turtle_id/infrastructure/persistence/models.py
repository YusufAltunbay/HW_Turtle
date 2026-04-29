"""
SQLAlchemy ORM tabloları.

Bu modüldeki sınıflar veritabanı şemasını tanımlar.
Domain modelleriyle (core/models) birebir eşleşmez;
dönüşüm sqlite_turtle_repo.py içindeki mapper metodlarında yapılır.
"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    LargeBinary,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from turtle_id.infrastructure.persistence.database import Base


class TurtleORM(Base):
    """
    Kaplumbağa ana kaydı.

    Bir kaplumbağaya birden fazla EmbeddingORM kaydı bağlanabilir
    (farklı zaman/açıdan çekilen fotoğraflar).
    """

    __tablename__ = "turtles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    species: Mapped[str] = mapped_column(String(255), default="")
    notes: Mapped[str] = mapped_column(Text, default="")
    primary_photo_path: Mapped[str] = mapped_column(Text, nullable=False)
    registration_date: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    embeddings: Mapped[list[EmbeddingORM]] = relationship(
        "EmbeddingORM",
        back_populates="turtle",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"TurtleORM(id={self.id!r}, name={self.name!r})"


class EmbeddingORM(Base):
    """
    Özellik vektörü kaydı.

    vector_blob: numpy float32 dizisinin ham byte temsili.
    model_name:  hangi modelle üretildiği (versiyon takibi).
    """

    __tablename__ = "embeddings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    turtle_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("turtles.id", ondelete="CASCADE"), nullable=False
    )
    vector_blob: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    vector_dim: Mapped[int] = mapped_column(Integer, nullable=False)
    photo_path: Mapped[str] = mapped_column(Text, nullable=False)
    model_name: Mapped[str] = mapped_column(String(128), nullable=False)
    captured_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )

    turtle: Mapped[TurtleORM] = relationship("TurtleORM", back_populates="embeddings")

    def __repr__(self) -> str:
        return (
            f"EmbeddingORM(id={self.id!r}, turtle_id={self.turtle_id!r}, "
            f"dim={self.vector_dim})"
        )


class VerificationLogORM(Base):
    """
    Doğrulama işlemi geçmiş kaydı.

    Her /verify çağrısı burada loglanır; denetim izi (audit trail) sağlar.
    """

    __tablename__ = "verification_log"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    query_photo_path: Mapped[str] = mapped_column(Text, nullable=False)
    matched_turtle_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("turtles.id"), nullable=True
    )
    similarity_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    threshold_used: Mapped[float] = mapped_column(Float, nullable=False)
    is_match: Mapped[bool] = mapped_column(Boolean, nullable=False)
    verified_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )

    def __repr__(self) -> str:
        status = "MATCH" if self.is_match else "NO_MATCH"
        return (
            f"VerificationLogORM({status}, score={self.similarity_score:.4f}, "
            f"turtle={self.matched_turtle_id!r})"
        )
