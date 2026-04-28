from turtle_id.core.ports.i_embedding_extractor import IEmbeddingExtractor
from turtle_id.core.ports.i_image_preprocessor import IImagePreprocessor
from turtle_id.core.ports.i_matcher import IMatcher
from turtle_id.core.ports.i_turtle_repository import ITurtleRepository

__all__ = [
    "IImagePreprocessor",
    "IEmbeddingExtractor",
    "IMatcher",
    "ITurtleRepository",
]
