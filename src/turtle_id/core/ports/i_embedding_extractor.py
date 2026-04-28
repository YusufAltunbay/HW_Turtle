"""
IEmbeddingExtractor port arayüzü.

Bağımlılık tersim (DIP) için soyut sözleşme.
Somut implementasyon: infrastructure/vision/timm_extractor.py
"""
from abc import ABC, abstractmethod

import numpy as np


class IEmbeddingExtractor(ABC):
    """
    Ön işlenmiş görüntüden L2 normalize özellik vektörü çıkarır.
    """

    @abstractmethod
    def extract(self, image: np.ndarray) -> np.ndarray:
        """
        Görüntüden özellik vektörü (embedding) çıkar.

        Args:
            image: Ön işlenmiş (H, W, C) float32 numpy dizisi.

        Returns:
            L2 normalize edilmiş 1D float32 vektör (örn. 1280-dim).

        Raises:
            RuntimeError: Model çıkarımı başarısız olursa.
        """

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Kullanılan modelin adı (versiyon takibi için)."""

    @property
    @abstractmethod
    def embedding_dim(self) -> int:
        """Üretilen vektörün boyutu."""
