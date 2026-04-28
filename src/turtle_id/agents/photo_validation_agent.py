"""
PhotoValidationAgent: Fotoğrafı işleme öncesi doğrulayan ajan.

Sorumluluk:
  - Dosya varlığı ve format kontrolü
  - Minimum boyut kontrolü
  - Bozuk dosya tespiti (OpenCV okuma testi)
  - Bulanıklık uyarısı (Laplacian variance)
  - Aşırı karanlık/parlak görüntü uyarısı

Ayrı ajan olma nedeni: ImageAgent sadece embedding üretmekten sorumlu (SRP).
Validasyon, kullanıcıya erken ve açıklayıcı geri bildirim verir.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from loguru import logger

from turtle_id.agents.base_agent import BaseAgent
from turtle_id.shared.event_bus import EventBus
from turtle_id.shared.events import EventType

_SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tiff"}
_MIN_WIDTH = 100
_MIN_HEIGHT = 100
_BLUR_THRESHOLD = 50.0       # Laplacian variance altında uyarı ver
_MIN_BRIGHTNESS = 20.0       # 0-255 ortalama parlaklık
_MAX_BRIGHTNESS = 240.0


@dataclass
class ValidationResult:
    """Doğrulama sonucu."""
    is_valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def has_warnings(self) -> bool:
        return len(self.warnings) > 0

    def add_error(self, message: str) -> None:
        self.errors.append(message)
        self.is_valid = False

    def add_warning(self, message: str) -> None:
        self.warnings.append(message)


class PhotoValidationAgent(BaseAgent):
    """
    Fotoğrafı işlem hattına sokmadan önce kalite ve geçerlilik kontrolü yapar.

    Args:
        event_bus: Paylaşılan EventBus.
    """

    def __init__(self, event_bus: EventBus) -> None:
        super().__init__(event_bus)

    @property
    def name(self) -> str:
        return "photo_validation_agent"

    def validate(self, image_path: str) -> ValidationResult:
        """
        Fotoğrafı doğrula.

        Args:
            image_path: Fotoğraf dosyasının tam yolu.

        Returns:
            ValidationResult: Geçerli mi, hatalar ve uyarılar listesi.
        """
        self._set_busy()
        self._publish(EventType.PHOTO_VALIDATION_STARTED, {"path": image_path})

        result = ValidationResult(is_valid=True)
        path = Path(image_path)

        self._check_file_exists(path, result)
        self._check_extension(path, result)

        if result.is_valid:
            self._check_image_readable(path, result)

        if result.is_valid:
            self._check_dimensions(path, result)
            self._check_blur(path, result)
            self._check_brightness(path, result)

        if result.is_valid:
            self._publish(EventType.PHOTO_VALID, {"path": image_path, "warnings": result.warnings})
            logger.info(f"PhotoValidationAgent: geçerli — {path.name}")
        else:
            self._publish(EventType.PHOTO_INVALID, {"path": image_path, "errors": result.errors})
            logger.warning(f"PhotoValidationAgent: geçersiz — {result.errors}")

        self._set_idle()
        return result

    # ------------------------------------------------------------------ #
    #  Private kontrol metodları                                           #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _check_file_exists(path: Path, result: ValidationResult) -> None:
        if not path.exists():
            result.add_error(f"Dosya bulunamadı: {path}")

    @staticmethod
    def _check_extension(path: Path, result: ValidationResult) -> None:
        if path.suffix.lower() not in _SUPPORTED_EXTENSIONS:
            result.add_error(
                f"Desteklenmeyen format: '{path.suffix}'. "
                f"Kabul edilenler: {', '.join(sorted(_SUPPORTED_EXTENSIONS))}"
            )

    @staticmethod
    def _check_image_readable(path: Path, result: ValidationResult) -> None:
        try:
            import cv2  # noqa: PLC0415
            img = cv2.imread(str(path))
            if img is None:
                result.add_error("Görüntü okunamadı (bozuk veya desteklenmeyen dosya).")
        except Exception as exc:
            result.add_error(f"Görüntü okuma hatası: {exc}")

    @staticmethod
    def _check_dimensions(path: Path, result: ValidationResult) -> None:
        try:
            import cv2  # noqa: PLC0415
            img = cv2.imread(str(path))
            if img is not None:
                h, w = img.shape[:2]
                if w < _MIN_WIDTH or h < _MIN_HEIGHT:
                    result.add_error(
                        f"Görüntü çok küçük: {w}×{h} px. "
                        f"Minimum: {_MIN_WIDTH}×{_MIN_HEIGHT} px."
                    )
        except Exception:
            pass

    @staticmethod
    def _check_blur(path: Path, result: ValidationResult) -> None:
        """Laplacian variance ile bulanıklık tespiti."""
        try:
            import cv2  # noqa: PLC0415
            img = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
            if img is not None:
                variance = float(cv2.Laplacian(img, cv2.CV_64F).var())
                if variance < _BLUR_THRESHOLD:
                    result.add_warning(
                        f"Görüntü bulanık görünüyor (keskinlik skoru: {variance:.1f}). "
                        "Daha net bir fotoğraf kullanmak doğruluğu artırır."
                    )
        except Exception:
            pass

    @staticmethod
    def _check_brightness(path: Path, result: ValidationResult) -> None:
        """Ortalama parlaklık kontrolü."""
        try:
            import cv2  # noqa: PLC0415
            img = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
            if img is not None:
                mean_brightness = float(img.mean())
                if mean_brightness < _MIN_BRIGHTNESS:
                    result.add_warning(
                        f"Görüntü çok karanlık (ortalama parlaklık: {mean_brightness:.1f}/255). "
                        "Daha iyi aydınlatılmış bir fotoğraf kullanın."
                    )
                elif mean_brightness > _MAX_BRIGHTNESS:
                    result.add_warning(
                        f"Görüntü aşırı parlak (ortalama parlaklık: {mean_brightness:.1f}/255). "
                        "Daha az pozlanmış bir fotoğraf kullanın."
                    )
        except Exception:
            pass
