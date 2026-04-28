"""
IImagePreprocessor port arayüzü.

Bağımlılık tersim (DIP) için soyut sözleşme.
Somut implementasyon: infrastructure/vision/opencv_preprocessor.py
"""
from abc import ABC, abstractmethod

import numpy as np


class IImagePreprocessor(ABC):
    """
    Ham fotoğraf dosyasını model girdisine hazır tensöre dönüştürür.
    """

    @abstractmethod
    def preprocess(self, image_path: str) -> np.ndarray:
        """
        Fotoğrafı yükle ve ön işle.

        Args:
            image_path: Fotoğraf dosyasının tam yolu.

        Returns:
            (H, W, C) şeklinde float32 numpy dizisi.
            Değerler ImageNet normalize edilmiş (mean/std).

        Raises:
            FileNotFoundError: Dosya bulunamazsa.
            ValueError: Görüntü okunamazsa veya format desteklenmiyorsa.
        """
