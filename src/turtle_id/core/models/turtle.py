"""
Turtle domain modeli.
Veritabanı veya UI detayı içermez; saf iş mantığı nesnesidir.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from turtle_id.core.models.embedding import Embedding


@dataclass
class Turtle:
    """
    Kayıtlı bir kaplumbağayı temsil eder.

    Attributes:
        id: Benzersiz tanımlayıcı.
        name: Kaplumbağanın ismi veya etiketi.
        species: Tür bilgisi (opsiyonel).
        notes: Ek notlar (opsiyonel).
        primary_photo_path: İlk kayıt fotoğrafının dosya yolu.
        registration_date: Sisteme kayıt tarihi.
        embeddings: Bu kaplumbağaya ait tüm embedding kayıtları.
    """

    name: str
    primary_photo_path: str
    id: UUID = field(default_factory=uuid4)
    species: str = ""
    notes: str = ""
    registration_date: datetime = field(default_factory=datetime.utcnow)
    embeddings: list[Embedding] = field(default_factory=list)

    def add_embedding(self, embedding: Embedding) -> None:
        """Kaplumbağaya yeni bir embedding kaydı ekle."""
        self.embeddings.append(embedding)

    def has_embeddings(self) -> bool:
        """En az bir embedding kaydı var mı?"""
        return len(self.embeddings) > 0

    def __repr__(self) -> str:
        return (
            f"Turtle(id={self.id!s:.8}, name={self.name!r}, "
            f"species={self.species!r}, embeddings={len(self.embeddings)})"
        )
