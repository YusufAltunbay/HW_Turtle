"""
ImageAgent: Ham fotoğraftan Embedding nesnesi üreten ajan.

Sorumluluk:
  - IImagePreprocessor ile görüntüyü normalize et
  - IEmbeddingExtractor ile özellik vektörü çıkar
  - Sonucu Embedding domain nesnesine paketle
  - EventBus üzerinden EMBEDDING_READY veya EMBEDDING_FAILED yayımla

Bu ajan, PHOTO_VALID olayını dinler ve otomatik tetiklenebilir;
ya da use case'ler tarafından doğrudan process() metodu ile çağrılır.
"""
from __future__ import annotations

from uuid import UUID

from loguru import logger

from turtle_id.agents.base_agent import BaseAgent
from turtle_id.core.models.embedding import Embedding
from turtle_id.core.ports.i_embedding_extractor import IEmbeddingExtractor
from turtle_id.core.ports.i_image_preprocessor import IImagePreprocessor
from turtle_id.shared.event_bus import EventBus
from turtle_id.shared.events import EventType


class ImageAgent(BaseAgent):
    """
    Fotoğraf dosyasından Embedding nesnesi üretir.

    Args:
        event_bus: Paylaşılan EventBus.
        preprocessor: Görüntü ön işleme implementasyonu.
        extractor: Özellik vektörü çıkarma implementasyonu.
    """

    def __init__(
        self,
        event_bus: EventBus,
        preprocessor: IImagePreprocessor,
        extractor: IEmbeddingExtractor,
    ) -> None:
        super().__init__(event_bus)
        self._preprocessor = preprocessor
        self._extractor = extractor

    @property
    def name(self) -> str:
        return "image_agent"

    def process(self, image_path: str, turtle_id: UUID) -> Embedding:
        """
        Fotoğraf dosyasını işle ve Embedding nesnesi üret.

        Args:
            image_path: Fotoğraf dosyasının tam yolu.
            turtle_id:  Bu embedding'in hangi kaplumbağaya ait olduğu.

        Returns:
            L2 normalize edilmiş Embedding nesnesi.

        Raises:
            FileNotFoundError: Dosya yoksa.
            ValueError: Görüntü okunamazsa.
            RuntimeError: Model çıkarımı başarısız olursa.
        """
        self._set_busy()
        self._publish(EventType.EMBEDDING_STARTED, {"image_path": image_path})

        try:
            image_array = self._preprocessor.preprocess(image_path)
            vector = self._extractor.extract(image_array)

            embedding = Embedding(
                turtle_id=turtle_id,
                vector=vector,
                photo_path=image_path,
                model_name=self._extractor.model_name,
            )

            self._publish(EventType.EMBEDDING_READY, embedding)
            self._set_idle()
            logger.info(
                f"ImageAgent: embedding hazır — "
                f"turtle_id={turtle_id!s:.8}, dim={embedding.dimension}"
            )
            return embedding

        except Exception as exc:
            self._set_error()
            self._publish(EventType.EMBEDDING_FAILED, {"error": str(exc)})
            logger.error(f"ImageAgent hata: {exc}")
            raise
