"""
Sentetik kaplumbaga test fotograflari uretici.

Her kaplumbaga icin birden fazla goruntu olusturur:
  - Farkli isik kosullari
  - Hafif renk/gurultu varyasyonu (ayni kaplumbaganin farkli zamanlarda cekilmis hissi)

5 kaplumbaga tamamen farkli gorsel kimlige sahip:
  alpha   - Yesil deniz kaplumbagasi  | altigen kabuk | kumlu sahil
  beta    - Loggerbalik               | kirmizi-kahve | mavi okyanus
  gamma   - Rengarenk kutu kaplumbaga | sari+siyah    | orman zemini
  delta   - Deri sirti                | siyah/koyu    | derin deniz
  epsilon - Tatli su kaplumbagasi     | parlak zeytin | tasilik dere

Kullanim:
    python data/generate_test_photos.py
"""
from __future__ import annotations

import os
import numpy as np
import cv2

IMG_SIZE = 224
PHOTOS_PER = 3

# ─────────────────────────────────────────────────────
#  Kaplumbaga kimlikleri — cok farkli gorsel profiller
# ─────────────────────────────────────────────────────
TURTLES = {
    "turtle_alpha": {
        "desc": "Yesil deniz kaplumbagasi — kumlu sahil",
        "bg_top":    (194, 178, 128),   # kum rengi
        "bg_bot":    (160, 142,  90),   # islak kum
        "body":      ( 45, 110,  55),   # zengin yesil
        "shell_mul": 0.55,
        "pattern":   "hexagon",
        "head_col":  ( 40,  90,  45),
        "acc_col":   (200, 220, 100),   # aci sari aksan
    },
    "turtle_beta": {
        "desc": "Loggerbalik — kirmizi-kahve, mavi okyanus",
        "bg_top":    ( 30,  80, 160),   # derin mavi
        "bg_bot":    ( 10,  40,  90),   # karanlik mavi
        "body":      ( 30,  60, 140),   # pahli kirmizi-kahve
        "shell_mul": 0.50,
        "pattern":   "ridge",
        "head_col":  ( 20,  45, 100),
        "acc_col":   ( 60, 100, 200),   # acik mavi aksan
    },
    "turtle_gamma": {
        "desc": "Kutu kaplumbaga — sari+siyah, orman zemini",
        "bg_top":    ( 30,  60,  20),   # koyu yesil orman
        "bg_bot":    ( 15,  35,  10),   # golgeli zemin
        "body":      (  0,   0,   0),   # siyah govde
        "shell_mul": 1.0,
        "pattern":   "boxturtle",
        "head_col":  ( 20,  80,  20),
        "acc_col":   (  0, 200, 220),   # parlak sari
    },
    "turtle_delta": {
        "desc": "Deri sirti — siyah, derin deniz",
        "bg_top":    (  8,   8,  30),   # gece mavisi
        "bg_bot":    (  3,   3,  15),   # siyah
        "body":      ( 15,  15,  20),   # neredeyse siyah
        "shell_mul": 0.40,
        "pattern":   "leatherback",
        "head_col":  ( 10,  10,  15),
        "acc_col":   (140, 140, 160),   # soluk gri aksan
    },
    "turtle_epsilon": {
        "desc": "Tatli su kaplumbagasi — zeytin, tasilik dere",
        "bg_top":    ( 60, 100,  40),   # yosunlu yesil
        "bg_bot":    ( 80,  80,  50),   # tasilik kahve
        "body":      ( 25,  80,  35),   # mat zeytin yesili
        "shell_mul": 0.65,
        "pattern":   "spot",
        "head_col":  ( 30,  70,  30),
        "acc_col":   (  0, 160,  80),   # neon yesil aksan
    },
}


# ─────────────────────────────────────────────────────
#  Arka plan
# ─────────────────────────────────────────────────────
def _background(size, top, bot):
    img = np.zeros((size, size, 3), np.uint8)
    for y in range(size):
        t = y / size
        img[y] = [
            int(top[0] + (bot[0] - top[0]) * t),
            int(top[1] + (bot[1] - top[1]) * t),
            int(top[2] + (bot[2] - top[2]) * t),
        ]
    return img


def _add_bg_texture(img, seed=0):
    rng = np.random.default_rng(seed)
    noise = rng.integers(-18, 18, img.shape, dtype=np.int16)
    return np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)


# ─────────────────────────────────────────────────────
#  Kabuk desenleri
# ─────────────────────────────────────────────────────
def _hexagon(img, cx, cy, rx, ry, body, mul):
    base = tuple(int(c * mul) for c in body)
    cv2.ellipse(img, (cx, cy), (rx, ry), 0, 0, 360, base, -1)
    edge = tuple(max(0, int(c * mul * 0.5)) for c in body)
    cv2.ellipse(img, (cx, cy), (rx, ry), 0, 0, 360, edge, 3)
    hi = tuple(min(255, int(c * mul * 1.5)) for c in body)
    step = rx // 3
    for dy in range(-ry, ry, step):
        off = step // 2 if (dy // step) % 2 else 0
        for dx in range(-rx, rx, step):
            px, py = cx + dx + off, cy + dy
            if (dx / rx)**2 + (dy / ry)**2 < 0.80:
                pts = np.array([[int(px + 9*np.cos(np.radians(60*a+30))),
                                  int(py + 9*np.sin(np.radians(60*a+30)))]
                                 for a in range(6)], np.int32)
                cv2.polylines(img, [pts], True, hi, 1)


def _ridge(img, cx, cy, rx, ry, body, mul):
    """Loggerbalik: boydan boya kalinturali siritlar."""
    base = tuple(int(c * mul) for c in body)
    cv2.ellipse(img, (cx, cy), (rx, ry), 0, 0, 360, base, -1)
    edge = tuple(max(0, int(c * mul * 0.4)) for c in body)
    cv2.ellipse(img, (cx, cy), (rx, ry), 0, 0, 360, edge, 4)
    ridge_col = tuple(min(255, int(c * mul * 1.6 + 20)) for c in body)
    for off in [-rx//3, 0, rx//3]:
        top_y  = cy - int(ry * np.sqrt(max(0, 1 - (off/rx)**2))) + 4
        bot_y  = cy + int(ry * np.sqrt(max(0, 1 - (off/rx)**2))) - 4
        cv2.line(img, (cx + off, top_y), (cx + off, bot_y), ridge_col, 5)


def _boxturtle(img, cx, cy, rx, ry, body, mul, acc):
    """Kutu kaplumbaga: siyah zemin uzerine sari lekeler."""
    base = tuple(int(c * mul) for c in body)
    cv2.ellipse(img, (cx, cy), (rx, ry), 0, 0, 360, base, -1)
    cv2.ellipse(img, (cx, cy), (rx, ry), 0, 0, 360, (30, 30, 30), 3)
    rng = np.random.default_rng(7)
    for _ in range(20):
        angle  = rng.uniform(0, 2*np.pi)
        r      = rng.uniform(0.15, 0.80)
        dx     = int(rx * r * np.cos(angle))
        dy     = int(ry * r * np.sin(angle))
        radius = int(rng.uniform(5, 14))
        col    = tuple(min(255, int(c * rng.uniform(0.8, 1.2))) for c in acc)
        cv2.circle(img, (cx+dx, cy+dy), radius, col, -1)


def _leatherback(img, cx, cy, rx, ry, body, mul):
    """Deri sirti: mat siyah, 5 kalin sirat."""
    base = tuple(int(c * mul) for c in body)
    cv2.ellipse(img, (cx, cy), (rx, ry), 0, 0, 360, base, -1)
    hi = tuple(min(255, c + 35) for c in base)
    for k in range(5):
        t   = (k - 2) / 3.0
        ox  = int(rx * t * 0.8)
        hy  = cy - int(ry * np.sqrt(max(0, 1 - (ox/rx)**2))) + 3
        by_ = cy + int(ry * np.sqrt(max(0, 1 - (ox/rx)**2))) - 3
        cv2.line(img, (cx+ox, hy), (cx+ox, by_), hi, 6 if k == 2 else 3)


def _spot(img, cx, cy, rx, ry, body, mul, acc):
    """Tatli su kaplumbagasi: kucuk parlak lekeler."""
    base = tuple(int(c * mul) for c in body)
    cv2.ellipse(img, (cx, cy), (rx, ry), 0, 0, 360, base, -1)
    cv2.ellipse(img, (cx, cy), (rx, ry), 0, 0, 360,
                tuple(max(0, int(c * 0.5)) for c in body), 3)
    rng = np.random.default_rng(42)
    for _ in range(16):
        angle  = rng.uniform(0, 2*np.pi)
        r      = rng.uniform(0.1, 0.78)
        dx     = int(rx * r * np.cos(angle))
        dy     = int(ry * r * np.sin(angle))
        radius = int(rng.uniform(3, 8))
        cv2.circle(img, (cx+dx, cy+dy), radius, acc, -1)


# ─────────────────────────────────────────────────────
#  Organlar
# ─────────────────────────────────────────────────────
def _legs(img, cx, cy, rx, ry, col):
    positions = [(-rx+8,-ry+18,-rx-20,-ry-10),
                 ( rx-8,-ry+18, rx+20,-ry-10),
                 (-rx+8, ry-18,-rx-20, ry+10),
                 ( rx-8, ry-18, rx+20, ry+10)]
    for lx1,ly1,lx2,ly2 in positions:
        cv2.ellipse(img, (cx+lx2, cy+ly2), (14,9), 0, 0, 360, col, -1)


def _head(img, cx, cy, ry, head_col, acc_col):
    hy = cy - ry - 16
    cv2.ellipse(img, (cx, hy), (20, 16), 0, 0, 360, head_col, -1)
    cv2.circle(img, (cx-7, hy-3), 4, (240,240,240), -1)
    cv2.circle(img, (cx+7, hy-3), 4, (240,240,240), -1)
    cv2.circle(img, (cx-7, hy-3), 2, (10,10,10),    -1)
    cv2.circle(img, (cx+7, hy-3), 2, (10,10,10),    -1)
    # renkli yanak lekesi (turden tura farkli aksan)
    cv2.circle(img, (cx-13, hy+2), 4, acc_col, -1)
    cv2.circle(img, (cx+13, hy+2), 4, acc_col, -1)


def _tail(img, cx, cy, ry, col):
    cv2.ellipse(img, (cx, cy+ry+14), (9,13), 0, 0, 360, col, -1)


# ─────────────────────────────────────────────────────
#  Isik efektleri
# ─────────────────────────────────────────────────────
def _lighting(img, brightness, contrast):
    r = img.astype(np.float32) * contrast + (brightness-1.0)*45
    return np.clip(r, 0, 255).astype(np.uint8)


def _noise(img, sigma):
    n = np.random.normal(0, sigma, img.shape).astype(np.float32)
    return np.clip(img.astype(np.float32)+n, 0, 255).astype(np.uint8)


def _vignette(img, s=0.45):
    h, w = img.shape[:2]
    Y = np.linspace(-1, 1, h)[:, None]
    X = np.linspace(-1, 1, w)[None, :]
    mask = np.clip(1.0 - s*(X**2+Y**2), 0, 1)
    return np.clip(img.astype(np.float32)*mask[:,:,None], 0, 255).astype(np.uint8)


# ─────────────────────────────────────────────────────
#  Ana uretici
# ─────────────────────────────────────────────────────
def make_image(spec, brightness=1.0, contrast=1.0, noise_sigma=8.0,
               size=IMG_SIZE, seed=0):
    img = _background(size, spec["bg_top"], spec["bg_bot"])
    img = _add_bg_texture(img, seed)

    cx, cy = size//2, size//2 + 14
    rx, ry = 68, 50
    body   = spec["body"]
    mul    = spec["shell_mul"]
    acc    = spec["acc_col"]

    _legs(img, cx, cy, rx, ry, tuple(int(c*0.85) for c in body))
    _tail(img, cx, cy, ry, tuple(int(c*0.80) for c in body))

    pat = spec["pattern"]
    if pat == "hexagon":
        _hexagon(img, cx, cy, rx, ry, body, mul)
    elif pat == "ridge":
        _ridge(img, cx, cy, rx, ry, body, mul)
    elif pat == "boxturtle":
        _boxturtle(img, cx, cy, rx, ry, body, mul, acc)
    elif pat == "leatherback":
        _leatherback(img, cx, cy, rx, ry, body, mul)
    elif pat == "spot":
        _spot(img, cx, cy, rx, ry, body, mul, acc)

    _head(img, cx, cy, ry, spec["head_col"], acc)

    img = _lighting(img, brightness, contrast)
    img = _noise(img, noise_sigma)
    img = _vignette(img)
    return img


VARIATIONS = [
    {"brightness": 1.00, "contrast": 1.00, "noise_sigma":  6.0, "seed": 1},  # standart
    {"brightness": 0.75, "contrast": 0.85, "noise_sigma": 14.0, "seed": 2},  # karanlik/gurultulu
    {"brightness": 1.25, "contrast": 1.15, "noise_sigma":  5.0, "seed": 3},  # parlak
]


def generate_all(output_dir):
    os.makedirs(output_dir, exist_ok=True)
    created = []
    for name, spec in TURTLES.items():
        folder = os.path.join(output_dir, name)
        os.makedirs(folder, exist_ok=True)
        for i, var in enumerate(VARIATIONS[:PHOTOS_PER]):
            img  = make_image(spec, **var)
            path = os.path.join(folder, f"photo_{i+1:02d}.jpg")
            cv2.imwrite(path, img, [cv2.IMWRITE_JPEG_QUALITY, 94])
            created.append(path)
            print(f"  [ok] {path}")
    print(f"\n[TAMAM] {len(created)} fotograf olusturuldu -> {output_dir}")
    return created


if __name__ == "__main__":
    root   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output = os.path.join(root, "data", "sample_photos")
    print("Sentetik kaplumbaga test verisi olusturuluyor...\n")
    generate_all(output)
