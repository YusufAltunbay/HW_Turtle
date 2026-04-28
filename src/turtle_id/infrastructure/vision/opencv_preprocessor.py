"""
OpenCVPreprocessor: IImagePreprocessor'ın OpenCV implementasyonu.

Farklı zamanlarda çekilen fotoğraflar arasındaki ışık ve renk
farklılıklarını normalize ederek modelin daha tutarlı embedding
üretmesini sağlar.
"""
from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
from loguru import logger

from turtle_id.core.ports.i_image_preprocessor import IImagePreprocessor

# ImageNet normalizasyon sabitleri (timm varsayılanı)
_IMAGENET_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
_IMAGENET_STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)

_TARGET_SIZE = (224, 224)
_SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tiff"}


class OpenCVPreprocessor(IImagePreprocessor):
    """
    Ham fotoğrafı EfficientNet girdisine hazır tensöre dönüştürür.

    İşlem sırası:
      1. Dosyayı oku (BGR → RGB)
      2. En-boy oranını koruyarak 224×224'e sığdır (letterbox)
      3. CLAHE ile kontrast normalleştirmesi (aydınlatma değişimine karşı)
      4. ImageNet mean/std ile normalize et
      5. float32 numpy dizisi olarak döndür
    """

    def preprocess(self, image_path: str) -> np.ndarray:
        """
        Args:
            image_path: Fotoğraf dosyasının tam yolu.

        Returns:
            (224, 224, 3) float32 numpy dizisi, ImageNet normalize edilmiş.

        Raises:
            FileNotFoundError: Dosya yoksa.
            ValueError: Format desteklenmiyorsa veya görüntü okunamazsa.
        """
        path = Path(image_path)
        self._validate_path(path)

        image_bgr = self._read_image(path)
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        resized = self._letterbox_resize(image_rgb, _TARGET_SIZE)
        enhanced = self._apply_clahe(resized)
        normalized = self._normalize(enhanced)

        logger.debug(f"Görüntü ön işlendi: {path.name} → {normalized.shape}")
        return normalized

    # ------------------------------------------------------------------ #
    #  Private: adım adım işlemler                                         #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _validate_path(path: Path) -> None:
        if not path.exists():
            raise FileNotFoundError(f"Fotoğraf bulunamadı: {path}")
        if path.suffix.lower() not in _SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Desteklenmeyen format: {path.suffix!r}. "
                f"Kabul edilenler: {_SUPPORTED_EXTENSIONS}"
            )

    @staticmethod
    def _read_image(path: Path) -> np.ndarray:
        image = cv2.imread(str(path))
        if image is None:
            raise ValueError(f"Görüntü okunamadı (bozuk dosya?): {path}")
        return image

    @staticmethod
    def _letterbox_resize(image: np.ndarray, target: tuple[int, int]) -> np.ndarray:
        """
        En-boy oranını bozmadan hedef boyuta sığdır.
        Boş alanı siyah padding ile doldur.
        """
        h, w = image.shape[:2]
        target_w, target_h = target

        scale = min(target_w / w, target_h / h)
        new_w = int(w * scale)
        new_h = int(h * scale)

        resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)

        canvas = np.zeros((target_h, target_w, 3), dtype=np.uint8)
        pad_x = (target_w - new_w) // 2
        pad_y = (target_h - new_h) // 2
        canvas[pad_y:pad_y + new_h, pad_x:pad_x + new_w] = resized

        return canvas

    @staticmethod
    def _apply_clahe(image: np.ndarray) -> np.ndarray:
        """
        CLAHE (Contrast Limited Adaptive Histogram Equalization) uygula.
        Sadece L kanalına uygulanır (LAB renk uzayı) — renk bilgisi korunur.
        Farklı aydınlatma koşullarındaki fotoğrafları normalize eder.
        """
        lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        lab[:, :, 0] = clahe.apply(lab[:, :, 0])
        return cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)

    @staticmethod
    def _normalize(image: np.ndarray) -> np.ndarray:
        """uint8 [0,255] → float32 [0,1] → ImageNet normalize."""
        img = image.astype(np.float32) / 255.0
        img = (img - _IMAGENET_MEAN) / _IMAGENET_STD
        return img
