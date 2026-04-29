"""
Embedding domain modeli.
Bir fotoğraftan çıkarılan özellik vektörünü ve meta verisini tutar.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4

import numpy as np


@dataclass
class Embedding:
    """
    Bir kaplumbağa fotoğrafından çıkarılan özellik vektörü.

    Attributes:
        turtle_id: Hangi kaplumbağaya ait olduğu.
        vector: L2 normalize edilmiş özellik vektörü (float32).
        photo_path: Vektörün çıkarıldığı fotoğrafın yolu.
        model_name: Kullanılan model adı (versiyon takibi için).
        captured_at: Fotoğrafın çekildiği veya eklendiği tarih.
        id: Benzersiz tanımlayıcı.
    """

    turtle_id: UUID
    vector: np.ndarray
    photo_path: str
    model_name: str = "efficientnet_b0"
    captured_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    id: UUID = field(default_factory=uuid4)

    @property
    def dimension(self) -> int:
        """Vektör boyutu."""
        return len(self.vector)

    def is_normalized(self) -> bool:
        """Vektörün L2 normalize edilmiş olup olmadığını kontrol et."""
        norm = float(np.linalg.norm(self.vector))
        return abs(norm - 1.0) < 1e-5

    def __repr__(self) -> str:
        return (
            f"Embedding(id={self.id!s:.8}, turtle_id={self.turtle_id!s:.8}, "
            f"dim={self.dimension}, model={self.model_name!r})"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Embedding):
            return NotImplemented
        return self.id == other.id
