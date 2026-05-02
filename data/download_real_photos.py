"""
iNaturalist API uzerinden gercek kaplumbaga fotograflarini indir.

iNaturalist: Creative Commons lisansli, arastirmaci/gonullu gozlem veritabani.
Her fotograf CC-BY veya CC-BY-NC lisansiyla serbestce kullanilabilir.

Kullanim:
    python data/download_real_photos.py

Cikti:
    data/real_photos/
        <gozlem_id>/  photo_01.jpg  photo_02.jpg  ...
        metadata.json
"""
from __future__ import annotations

import json
import os
import time
import urllib.request
import urllib.error
from pathlib import Path

# ─────────────────────────────────────────────────────────────────
#  Hedef turler: her biri gorsel olarak cok farkli
# ─────────────────────────────────────────────────────────────────
TARGET_SPECIES = [
    {
        "taxon_name": "Chelonia mydas",
        "common_name": "Yesil Deniz Kaplumbagasi",
        "photos_wanted": 3,
    },
    {
        "taxon_name": "Caretta caretta",
        "common_name": "Loggerbalik",
        "photos_wanted": 3,
    },
    {
        "taxon_name": "Dermochelys coriacea",
        "common_name": "Deri Sirti Kaplumbaga",
        "photos_wanted": 3,
    },
    {
        "taxon_name": "Trachemys scripta",
        "common_name": "Kirmizi Kulakli Tatli Su Kaplumbagasi",
        "photos_wanted": 3,
    },
    {
        "taxon_name": "Terrapene carolina",
        "common_name": "Dogu Kutu Kaplumbagasi",
        "photos_wanted": 3,
    },
]

INAT_API  = "https://api.inaturalist.org/v1"
IMG_SIZE  = 224   # kaydetmeden once yeniden boyutlandir


def _get(url: str, timeout: int = 15) -> dict:
    """JSON endpoint'ini cek."""
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "TurtleID-Research/1.0 (educational project)"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode())


def _download_image(url: str, dest: str, timeout: int = 20) -> bool:
    """Goruntu indir, 224x224 olarak kaydet."""
    try:
        import cv2
        import numpy as np

        req = urllib.request.Request(
            url,
            headers={"User-Agent": "TurtleID-Research/1.0"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()

        arr = np.frombuffer(data, np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if img is None:
            return False

        # Letterbox resize
        h, w = img.shape[:2]
        scale = IMG_SIZE / max(h, w)
        nh, nw = int(h * scale), int(w * scale)
        resized = cv2.resize(img, (nw, nh), interpolation=cv2.INTER_AREA)
        canvas = np.zeros((IMG_SIZE, IMG_SIZE, 3), np.uint8)
        y0 = (IMG_SIZE - nh) // 2
        x0 = (IMG_SIZE - nw) // 2
        canvas[y0:y0+nh, x0:x0+nw] = resized

        cv2.imwrite(dest, canvas, [cv2.IMWRITE_JPEG_QUALITY, 92])
        return True
    except Exception as exc:
        print(f"    [uyari] Goruntu indirilemedi: {exc}")
        return False


def _fetch_observations(taxon_name: str, count: int) -> list[dict]:
    """
    iNaturalist'ten arastirma kalitesinde, CC lisansli gozlemleri cek.
    Her gozlemde en az 1 fotograf olmali.
    """
    params = (
        f"taxon_name={urllib.parse.quote(taxon_name)}"
        f"&quality_grade=research"
        f"&license=cc-by,cc-by-nc,cc0"
        f"&photos=true"
        f"&per_page={min(count * 3, 30)}"
        f"&order_by=votes"
    )
    url  = f"{INAT_API}/observations?{params}"
    data = _get(url)
    return data.get("results", [])


def download_all(output_dir: str = "data/real_photos") -> None:
    import urllib.parse   # noqa: PLC0415 — lazy import iceride kullaniyor

    os.makedirs(output_dir, exist_ok=True)
    metadata = []
    total_downloaded = 0

    for species in TARGET_SPECIES:
        taxon   = species["taxon_name"]
        cname   = species["common_name"]
        wanted  = species["photos_wanted"]

        print(f"\n[{cname}] ({taxon}) gozlemleri axtariliyor...")

        try:
            observations = _fetch_observations(taxon, wanted)
        except Exception as exc:
            print(f"  [hata] API hatasi: {exc}")
            continue

        saved = 0
        for obs in observations:
            if saved >= wanted:
                break

            obs_id = obs.get("id")
            photos = obs.get("photos", [])
            if not photos:
                continue

            photo      = photos[0]
            photo_url  = photo.get("url", "")
            license_   = photo.get("license_code", "unknown")

            # Orta cozunurluk: 'square' (75px) yerine 'medium' (500px) kullan
            photo_url = photo_url.replace("/square.", "/medium.")

            folder = os.path.join(output_dir, f"{taxon.replace(' ','_')}_{obs_id}")
            os.makedirs(folder, exist_ok=True)
            dest   = os.path.join(folder, "photo_01.jpg")

            ok = _download_image(photo_url, dest)
            if not ok:
                continue

            saved += 1
            total_downloaded += 1
            print(f"  [ok] {dest}  (obs={obs_id}, lisans={license_})")

            metadata.append({
                "taxon": taxon,
                "common_name": cname,
                "observation_id": obs_id,
                "inat_url": f"https://www.inaturalist.org/observations/{obs_id}",
                "photo_license": license_,
                "local_path": dest,
                "attribution": obs.get("user", {}).get("login", "unknown"),
            })

            time.sleep(0.5)   # API rate limit icin kibarca bekle

        if saved < wanted:
            print(f"  [uyari] {saved}/{wanted} fotograf indirilebildi")

    # Metadata kaydet
    meta_path = os.path.join(output_dir, "metadata.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"\n[TAMAM] {total_downloaded} gercek kaplumbaga fotografu indirildi -> {output_dir}")
    print(f"[TAMAM] Kaynak bilgisi: {meta_path}")
    print()
    print("Kullanim:")
    print("  - Her kaplumbaga klasorundeki photo_01.jpg -> Kayit icin kullan")
    print("  - Farkli turun fotografiyla Dogrulama testini dene")
    print("  - metadata.json: kaynak, lisans ve atif bilgilerini icerir")


if __name__ == "__main__":
    root   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output = os.path.join(root, "data", "real_photos")
    print("iNaturalist'ten gercek kaplumbaga fotograflari indiriliyor...")
    print("(CC lisansli, arastirma kalitesi gozlemler)\n")
    download_all(output)
