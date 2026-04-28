"""
ITurtleRepository port arayüzü.

Bağımlılık tersim (DIP) için soyut sözleşme.
Somut implementasyon: infrastructure/persistence/sqlite_turtle_repo.py
"""
from abc import ABC, abstractmethod
from uuid import UUID

from turtle_id.core.models.embedding import Embedding
from turtle_id.core.models.turtle import Turtle


class ITurtleRepository(ABC):
    """
    Kaplumbağa ve embedding kayıtlarının kalıcı depolama sözleşmesi.
    """

    @abstractmethod
    def save(self, turtle: Turtle) -> Turtle:
        """Yeni kaplumbağa kaydı oluştur ve geri döndür."""

    @abstractmethod
    def find_by_id(self, turtle_id: UUID) -> Turtle | None:
        """ID ile kaplumbağa sorgula. Bulunamazsa None döner."""

    @abstractmethod
    def find_all(self) -> list[Turtle]:
        """Tüm aktif kaplumbağa kayıtlarını döndür."""

    @abstractmethod
    def update(self, turtle: Turtle) -> Turtle:
        """Mevcut kaplumbağa kaydını güncelle."""

    @abstractmethod
    def delete(self, turtle_id: UUID) -> None:
        """Kaplumbağa kaydını sil (soft delete)."""

    @abstractmethod
    def add_embedding(self, embedding: Embedding) -> Embedding:
        """Mevcut bir kaplumbağaya yeni embedding ekle."""

    @abstractmethod
    def get_all_embeddings(self) -> list[Embedding]:
        """Tüm kaplumbağalara ait embedding'leri döndür (eşleştirme için)."""

    @abstractmethod
    def get_embeddings_by_turtle(self, turtle_id: UUID) -> list[Embedding]:
        """Belirli bir kaplumbağanın tüm embedding'lerini döndür."""
