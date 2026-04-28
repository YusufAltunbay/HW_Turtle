"""
Sistem genelinde kullanılan olay tipleri ve veri yapıları.
Tüm ajanlar bu modüldeki EventType enum'unu kullanır.
"""
from enum import Enum


class EventType(Enum):
    # Fotoğraf doğrulama olayları
    PHOTO_VALIDATION_STARTED = "photo.validation.started"
    PHOTO_VALID = "photo.validation.passed"
    PHOTO_INVALID = "photo.validation.failed"

    # Embedding olayları
    EMBEDDING_STARTED = "embedding.started"
    EMBEDDING_READY = "embedding.ready"
    EMBEDDING_FAILED = "embedding.failed"

    # Eşleştirme olayları
    MATCHING_STARTED = "matching.started"
    MATCH_FOUND = "matching.found"
    MATCH_NOT_FOUND = "matching.not_found"

    # Veri olayları
    TURTLE_SAVED = "data.turtle_saved"
    TURTLE_LOADED = "data.turtle_loaded"
    DATA_ERROR = "data.error"

    # Config olayları
    CONFIG_CHANGED = "config.changed"

    # İşlem durumu
    PROCESSING_PROGRESS = "processing.progress"
