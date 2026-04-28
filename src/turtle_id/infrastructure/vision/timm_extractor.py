"""
TimmEfficientNetExtractor: IEmbeddingExtractor'ın timm/EfficientNet implementasyonu.

EfficientNet-B0 modelini özellik çıkarıcı olarak kullanır.
Son sınıflandırma katmanı devre dışı bırakılır; 1280-boyutlu
global average pooling çıktısı L2 normalize edilerek döndürülür.
"""
from __future__ import annotations

import numpy as np
from loguru import logger

from turtle_id.core.ports.i_embedding_extractor import IEmbeddingExtractor

# torch ve timm: ağır bağımlılıklar; lazy import ile uygulama başlangıcını hızlandır
try:
    import timm
    import torch
    import torch.nn.functional as F
    _TORCH_AVAILABLE = True
except ImportError:
    _TORCH_AVAILABLE = False


_MODEL_NAME = "efficientnet_b0"
_EMBEDDING_DIM = 1280


class TimmEfficientNetExtractor(IEmbeddingExtractor):
    """
    timm kütüphanesi ile EfficientNet-B0 tabanlı özellik çıkarıcı.

    İlk kullanımda model yüklemesi yapılır (lazy init).
    GPU varsa otomatik kullanılır; yoksa CPU'ya düşer.
    """

    def __init__(self) -> None:
        self._model = None
        self._device: str | None = None

    def _ensure_model_loaded(self) -> None:
        """Model henüz yüklü değilse yükle (lazy initialization)."""
        if self._model is not None:
            return

        if not _TORCH_AVAILABLE:
            raise RuntimeError(
                "torch ve timm kurulu değil. "
                "Lütfen: pip install torch torchvision timm"
            )

        self._device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"EfficientNet-B0 yükleniyor... (device={self._device})")

        self._model = timm.create_model(
            _MODEL_NAME,
            pretrained=True,
            num_classes=0,          # Sınıflandırıcıyı kaldır
            global_pool="avg",      # Global average pooling → 1280-dim
        )
        self._model.eval()
        self._model.to(self._device)
        logger.info("EfficientNet-B0 hazır.")

    def extract(self, image: np.ndarray) -> np.ndarray:
        """
        Görüntüden L2 normalize özellik vektörü çıkar.

        Args:
            image: (H, W, C) float32 numpy dizisi, ImageNet normalize edilmiş.

        Returns:
            (1280,) float32 L2 normalize vektör.
        """
        self._ensure_model_loaded()

        tensor = self._to_tensor(image)

        with torch.no_grad():
            features = self._model(tensor)            # (1, 1280)

        vector = features.squeeze(0).cpu().numpy()    # (1280,)
        normalized = self._l2_normalize(vector)

        logger.debug(f"Embedding çıkarıldı: dim={len(normalized)}, norm≈1.0")
        return normalized

    @property
    def model_name(self) -> str:
        return _MODEL_NAME

    @property
    def embedding_dim(self) -> int:
        return _EMBEDDING_DIM

    # ------------------------------------------------------------------ #
    #  Private yardımcılar                                                 #
    # ------------------------------------------------------------------ #

    def _to_tensor(self, image: np.ndarray):
        """numpy (H,W,C) float32 → torch (1,C,H,W) tensor."""
        import torch  # noqa: PLC0415
        tensor = torch.from_numpy(image).permute(2, 0, 1).unsqueeze(0).float()
        return tensor.to(self._device)

    @staticmethod
    def _l2_normalize(vector: np.ndarray) -> np.ndarray:
        """Vektörü L2 normalize et; cosine similarity için hazırla."""
        norm = np.linalg.norm(vector)
        if norm < 1e-9:
            logger.warning("Sıfır normlu vektör — siyah/bozuk görüntü olabilir.")
            return vector
        return (vector / norm).astype(np.float32)
