"""
Sentetik kaplumbağa test fotoğrafları üretici.

Her "kaplumbağa" için birden fazla görüntü oluşturur:
  - Farklı ışık koşulları (parlaklık varyasyonu)
  - Hafif renk değişimleri (aynı kaplumbağanın farklı zamanlarda çekilmiş hissi)
  - Gürültü ekleme

Kullanım:
    python data/generate_test_photos.py

Çıktı:
    data/sample_photos/
        turtle_alpha/   → 3 fotoğraf (kayıt + test için)
        turtle_beta/    → 3 fotoğraf
        turtle_gamma/   → 3 fotoğraf
        turtle_delta/   → 3 fotoğraf
        turtle_epsilon/ → 3 fotoğraf
"""
from __future__ import annotations

import os
import sys

import cv2
import numpy as np

# ──────────────────────────────────────────────────────────────────────────────
# Kaplumbağa "şablonları": her biri farklı görsel kimliğe sahip
# ──────────────────────────────────────────────────────────────────────────────
TURTLES: dict[str, dict] = {
    "turtle_alpha": {
        "base_color": (34, 85, 40),       # koyu yeşil — yaygın su kaplumbağası
        "pattern": "hexagon",
        "shell_lightness": 0.55,
    },
    "turtle_beta": {
        "base_color": (20, 60, 100),      # zeytin-kahve
        "pattern": "stripe",
        "shell_lightness": 0.45,
    },
    "turtle_gamma": {
        "base_color": (80, 110, 30),      # sarı-yeşil
        "pattern": "spot",
        "shell_lightness": 0.65,
    },
    "turtle_delta": {
        "base_color": (15, 40, 55),       # koyu kahve
        "pattern": "solid",
        "shell_lightness": 0.35,
    },
    "turtle_epsilon": {
        "base_color": (55, 90, 60),       # açık yeşil
        "pattern": "hexagon",
        "shell_lightness": 0.70,
    },
}

IMG_SIZE   = 224   # model giriş boyutu ile aynı
PHOTOS_PER = 3     # her kaplumbağa için kaç görüntü


# ──────────────────────────────────────────────────────────────────────────────
# Çizim yardımcıları
# ──────────────────────────────────────────────────────────────────────────────

def _make_background(size: int, color: tuple[int, int, int]) -> np.ndarray:
    """Hafif gradyanlı arka plan oluştur."""
    img = np.zeros((size, size, 3), dtype=np.uint8)
    # BGR renk gradyanı
    for i in range(size):
        t = i / size
        b = int(color[0] * (0.6 + 0.4 * t))
        g = int(color[1] * (0.6 + 0.4 * t))
        r = int(color[2] * (0.6 + 0.4 * t))
        img[i, :] = [b, g, r]
    return img


def _draw_shell(img: np.ndarray, cx: int, cy: int,
                rx: int, ry: int, color: tuple[int, int, int],
                lightness: float) -> None:
    """Elips şeklinde kabuk gövdesi çiz."""
    shell_color = tuple(int(c * lightness) for c in color)
    cv2.ellipse(img, (cx, cy), (rx, ry), 0, 0, 360, shell_color, -1)
    # kabuk kenarı
    edge_color = tuple(max(0, int(c * lightness * 0.6)) for c in color)
    cv2.ellipse(img, (cx, cy), (rx, ry), 0, 0, 360, edge_color, 3)


def _draw_hexagon_pattern(img: np.ndarray, cx: int, cy: int,
                           rx: int, ry: int,
                           color: tuple[int, int, int]) -> None:
    """Kabuk üzerine altıgen desen çiz."""
    hex_color = tuple(min(255, int(c * 1.3)) for c in color)
    spacing = rx // 3
    for dy in range(-ry, ry, spacing):
        offset = (spacing // 2) if (dy // spacing) % 2 else 0
        for dx in range(-rx, rx, spacing):
            px, py = cx + dx + offset, cy + dy
            # elips içinde mi?
            if (dx / rx) ** 2 + (dy / ry) ** 2 < 0.85:
                pts = []
                for a in range(6):
                    angle = np.radians(60 * a + 30)
                    pts.append([int(px + 8 * np.cos(angle)),
                                int(py + 8 * np.sin(angle))])
                pts_arr = np.array(pts, dtype=np.int32)
                cv2.polylines(img, [pts_arr], True, hex_color, 1)


def _draw_stripe_pattern(img: np.ndarray, cx: int, cy: int,
                          rx: int, ry: int,
                          color: tuple[int, int, int]) -> None:
    """Kabuk üzerine çizgi desen çiz."""
    stripe_color = tuple(min(255, int(c * 1.4)) for c in color)
    for i, dy in enumerate(range(-ry + 10, ry - 10, 14)):
        if i % 2 == 0:
            x_half = int(rx * np.sqrt(max(0, 1 - (dy / ry) ** 2)) * 0.9)
            cv2.line(img, (cx - x_half, cy + dy), (cx + x_half, cy + dy),
                     stripe_color, 2)


def _draw_spot_pattern(img: np.ndarray, cx: int, cy: int,
                        rx: int, ry: int,
                        color: tuple[int, int, int]) -> None:
    """Kabuk üzerine leke/nokta desen çiz."""
    spot_color = tuple(min(255, int(c * 1.5)) for c in color)
    rng = np.random.default_rng(42)  # deterministik
    for _ in range(12):
        angle = rng.uniform(0, 2 * np.pi)
        r_scale = rng.uniform(0.2, 0.75)
        dx = int(rx * r_scale * np.cos(angle))
        dy = int(ry * r_scale * np.sin(angle))
        radius = int(rng.uniform(6, 14))
        cv2.circle(img, (cx + dx, cy + dy), radius, spot_color, -1)


def _draw_head(img: np.ndarray, cx: int, cy: int,
               ry: int, color: tuple[int, int, int]) -> None:
    """Baş çiz."""
    head_color = tuple(min(255, int(c * 0.9)) for c in color)
    head_y = cy - ry - 18
    cv2.ellipse(img, (cx, head_y), (22, 18), 0, 0, 360, head_color, -1)
    # göz
    cv2.circle(img, (cx - 8, head_y - 4), 4, (255, 255, 255), -1)
    cv2.circle(img, (cx + 8, head_y - 4), 4, (255, 255, 255), -1)
    cv2.circle(img, (cx - 8, head_y - 4), 2, (10, 10, 10), -1)
    cv2.circle(img, (cx + 8, head_y - 4), 2, (10, 10, 10), -1)


def _draw_legs(img: np.ndarray, cx: int, cy: int,
               rx: int, ry: int, color: tuple[int, int, int]) -> None:
    """Dört bacak çiz."""
    leg_color = tuple(min(255, int(c * 0.85)) for c in color)
    legs = [
        (-rx + 10, -ry + 20, -rx - 22, -ry - 8),   # sol ön
        (rx - 10,  -ry + 20,  rx + 22, -ry - 8),    # sağ ön
        (-rx + 10,  ry - 20, -rx - 22,  ry + 8),    # sol arka
        (rx - 10,   ry - 20,  rx + 22,  ry + 8),    # sağ arka
    ]
    for lx1, ly1, lx2, ly2 in legs:
        cv2.ellipse(img, (cx + lx2, cy + ly2), (14, 10), 0, 0, 360,
                    leg_color, -1)


def _draw_tail(img: np.ndarray, cx: int, cy: int,
               ry: int, color: tuple[int, int, int]) -> None:
    """Kuyruk çiz."""
    tail_color = tuple(min(255, int(c * 0.8)) for c in color)
    tail_y = cy + ry + 15
    cv2.ellipse(img, (cx, tail_y), (10, 15), 0, 0, 360, tail_color, -1)


def _apply_lighting(img: np.ndarray, brightness: float,
                    contrast: float) -> np.ndarray:
    """Parlaklık ve kontrast uygula (float: 1.0 = değişim yok)."""
    result = img.astype(np.float32)
    result = result * contrast + (brightness - 1.0) * 50
    return np.clip(result, 0, 255).astype(np.uint8)


def _add_noise(img: np.ndarray, sigma: float) -> np.ndarray:
    """Gaussian gürültü ekle."""
    noise = np.random.normal(0, sigma, img.shape).astype(np.float32)
    result = img.astype(np.float32) + noise
    return np.clip(result, 0, 255).astype(np.uint8)


def _add_vignette(img: np.ndarray, strength: float = 0.4) -> np.ndarray:
    """Kenar kararması (vignette) efekti."""
    h, w = img.shape[:2]
    Y = np.linspace(-1, 1, h)[:, np.newaxis]
    X = np.linspace(-1, 1, w)[np.newaxis, :]
    mask = 1.0 - strength * (X**2 + Y**2)
    mask = np.clip(mask, 0, 1)
    result = img.astype(np.float32) * mask[:, :, np.newaxis]
    return np.clip(result, 0, 255).astype(np.uint8)


# ──────────────────────────────────────────────────────────────────────────────
# Ana üretici
# ──────────────────────────────────────────────────────────────────────────────

def generate_turtle_image(
    color: tuple[int, int, int],
    pattern: str,
    lightness: float,
    brightness: float = 1.0,
    contrast: float = 1.0,
    noise_sigma: float = 8.0,
    size: int = IMG_SIZE,
) -> np.ndarray:
    """Verilen parametrelerle tek bir kaplumbağa görüntüsü oluştur."""
    img = _make_background(size, color)

    cx, cy = size // 2, size // 2 + 15
    rx, ry = 70, 52

    _draw_legs(img, cx, cy, rx, ry, color)
    _draw_tail(img, cx, cy, ry, color)
    _draw_shell(img, cx, cy, rx, ry, color, lightness)

    if pattern == "hexagon":
        _draw_hexagon_pattern(img, cx, cy, rx, ry, color)
    elif pattern == "stripe":
        _draw_stripe_pattern(img, cx, cy, rx, ry, color)
    elif pattern == "spot":
        _draw_spot_pattern(img, cx, cy, rx, ry, color)
    # "solid" → sadece düz kabuk

    _draw_head(img, cx, cy, ry, color)

    img = _apply_lighting(img, brightness, contrast)
    img = _add_noise(img, noise_sigma)
    img = _add_vignette(img, strength=0.35)
    return img


def generate_all(output_dir: str = "data/sample_photos") -> None:
    """Tüm test fotoğraflarını oluştur ve kaydet."""
    os.makedirs(output_dir, exist_ok=True)

    # Her kaplumbağa için farklı ışık/gürültü varyasyonları
    variations = [
        {"brightness": 1.05, "contrast": 1.05, "noise_sigma": 6.0},   # standart
        {"brightness": 0.80, "contrast": 0.90, "noise_sigma": 12.0},  # karanlık / gürültülü
        {"brightness": 1.20, "contrast": 1.10, "noise_sigma": 5.0},   # parlak
    ]

    created: list[str] = []
    for turtle_name, spec in TURTLES.items():
        folder = os.path.join(output_dir, turtle_name)
        os.makedirs(folder, exist_ok=True)

        for i, var in enumerate(variations[:PHOTOS_PER]):
            img = generate_turtle_image(
                color=spec["base_color"],
                pattern=spec["pattern"],
                lightness=spec["shell_lightness"],
                **var,
            )
            path = os.path.join(folder, f"photo_{i + 1:02d}.jpg")
            cv2.imwrite(path, img, [cv2.IMWRITE_JPEG_QUALITY, 92])
            created.append(path)
            print(f"  [ok] {path}")

    print(f"\n[OK] {len(created)} fotograf olusturuldu -> {output_dir}/")
    print("\nOnerilen test akisi:")
    print("  1. Kayit : her kaplumbaganin photo_01.jpg dosyasini kullan")
    print("  2. Dogrulama : ayni kaplumbaganin photo_02.jpg veya photo_03.jpg ile test et")
    print("  3. Yanlis esleme testi : farkli kaplumbaganin fotografini kullan\n")


if __name__ == "__main__":
    # Script hangi dizinden çalıştırılırsa çalıştırılsın proje köküne göre yaz
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    output = os.path.join(project_root, "data", "sample_photos")

    print("Sentetik kaplumbaga test verisi olusturuluyor...\n")
    generate_all(output)
