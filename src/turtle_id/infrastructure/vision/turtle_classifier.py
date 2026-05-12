"""
TurtleClassifier: Fotoğrafın kaplumbağa içerip içermediğini tespit eder.

EfficientNet-B0 (ImageNet-1k sınıflandırıcısı) kullanır.
ImageNet indeks 33-37 kaplumbağa türlerine karşılık gelir:
  33 → loggerhead (Caretta caretta)
  34 → leatherback turtle (Dermochelys coriacea)
  35 → mud turtle
  36 → terrapin
  37 → box turtle / box tortoise

Eğer top-10 tahmin içinde herhangi bir kaplumbağa sınıfının güveni
CONFIDENCE_THRESHOLD'u aşarsa fotoğraf kaplumbağa içeriyor kabul edilir.
"""
from __future__ import annotations

import numpy as np
from loguru import logger

try:
    import timm
    import torch
    import torch.nn.functional as F
    _TORCH_AVAILABLE = True
except ImportError:
    _TORCH_AVAILABLE = False

# ImageNet-1k kaplumbağa sınıf indeksleri (ILSVRC2012 standart sıralaması)
_TURTLE_CLASS_INDICES = frozenset([33, 34, 35, 36, 37])

# Bu skoru aşan ilk kaplumbağa sınıfı → kaplumbağa kabul edilir
CONFIDENCE_THRESHOLD = 0.05

_MODEL_NAME = "efficientnet_b0"

# ImageNet normalizasyon sabitleri
_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
_STD  = np.array([0.229, 0.224, 0.225], dtype=np.float32)
_SIZE = 224


class TurtleClassifier:
    """
    Fotoğrafın kaplumbağa içerip içermediğini EfficientNet-B0 ile sınıflandırır.

    İlk çağrıda model yüklenir (lazy init). Sonraki çağrılarda önbellekten kullanılır.
    """

    def __init__(self) -> None:
        self._model = None
        self._device: str | None = None

    def is_turtle(self, image_path: str) -> tuple[bool, float]:
        """
        Fotoğrafı analiz et.

        Args:
            image_path: Fotoğraf dosyasının tam yolu.

        Returns:
            (kaplumbağa_mi, en_yüksek_kaplumbağa_güveni) tuple.
            Model yüklenemezse (True, 0.0) döner → hata yokmuş gibi davran.
        """
        if not _TORCH_AVAILABLE:
            logger.warning("TurtleClassifier: torch/timm bulunamadı, kaplumbağa kontrolü atlandı.")
            return True, 0.0

        try:
            self._ensure_model_loaded()
            tensor = self._preprocess(image_path)
            if tensor is None:
                return True, 0.0  # Görüntü okunamazsa validasyon zaten hata verir

            with torch.no_grad():
                logits = self._model(tensor)          # (1, 1000)
                probs  = F.softmax(logits, dim=1)     # olasılıklar

            probs_np = probs.squeeze(0).cpu().numpy()  # (1000,)

            # Kaplumbağa sınıflarındaki en yüksek olasılık
            turtle_scores = {idx: float(probs_np[idx]) for idx in _TURTLE_CLASS_INDICES}
            max_score = max(turtle_scores.values())
            best_class = max(turtle_scores, key=turtle_scores.get)

            logger.debug(
                f"TurtleClassifier: en yüksek kaplumbağa skoru = "
                f"{max_score:.3f} (sınıf {best_class})"
            )

            return max_score >= CONFIDENCE_THRESHOLD, max_score

        except Exception as exc:
            logger.warning(f"TurtleClassifier: beklenmedik hata — {exc}. Kontrol atlandı.")
            return True, 0.0  # Hata durumunda kayıta izin ver, kullanıcıyı engelleme

    # ------------------------------------------------------------------ #
    #  Private                                                             #
    # ------------------------------------------------------------------ #

    def _ensure_model_loaded(self) -> None:
        """Model henüz yüklü değilse yükle."""
        if self._model is not None:
            return

        self._device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"TurtleClassifier: EfficientNet-B0 yükleniyor... (device={self._device})")

        self._model = timm.create_model(
            _MODEL_NAME,
            pretrained=True,
            num_classes=1000,   # Tam ImageNet sınıflandırıcı
        )
        self._model.eval()
        self._model.to(self._device)
        logger.info("TurtleClassifier: hazır.")

    def _preprocess(self, image_path: str):
        """Görüntüyü modele uygun tensöre dönüştür."""
        try:
            import cv2  # noqa: PLC0415

            img_bgr = cv2.imread(image_path)
            if img_bgr is None:
                return None

            img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

            # Kaplumbağa tespiti için basit center-crop resize yeterli
            img_resized = cv2.resize(img_rgb, (_SIZE, _SIZE), interpolation=cv2.INTER_AREA)

            # ImageNet normalize
            img_f = img_resized.astype(np.float32) / 255.0
            img_f = (img_f - _MEAN) / _STD

            # (H, W, C) → (1, C, H, W)
            tensor = torch.from_numpy(img_f).permute(2, 0, 1).unsqueeze(0).float()
            return tensor.to(self._device)

        except Exception as exc:
            logger.warning(f"TurtleClassifier: ön işleme hatası — {exc}")
            return None
