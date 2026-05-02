"""
iNaturalist API uzerinden gercek kaplumbaga fotograflarini indir.

iNaturalist: Creative Commons lisansli, arastirmaci/gonullu gozlem veritabani.
Her fotograf CC-BY veya CC-BY-NC lisansiyla serbestce kullanilabilir.

Kullanim:
    python data/download_real_photos.py

Cikti:
    data/real_photos/
        <tur_adi>/  photo_01.jpg  photo_02.jpg  photo_03.jpg
        metadata.json
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
#  Hedef turler — iNaturalist taxon_id ile (URL encode sorununu oner)
#  ID'leri dogrulamak icin: https://www.inaturalist.org/taxa/<isim>
# ─────────────────────────────────────────────────────────────────────────────
TARGET_SPECIES = [
    {
        "taxon_name":  "Chelonia mydas",
        "common_name": "Yesil Deniz Kaplumbagasi",
        "photos_wanted": 3,
    },
    {
        "taxon_name":  "Caretta caretta",
        "common_name": "Loggerbalik",
        "photos_wanted": 3,
    },
    {
        "taxon_name":  "Dermochelys coriacea",
        "common_name": "Deri Sirti",
        "photos_wanted": 3,
    },
    {
        "taxon_name":  "Trachemys scripta",
        "common_name": "Kirmizi Kulakli Tatli Su Kaplumbagasi",
        "photos_wanted": 3,
    },
    {
        "taxon_name":  "Terrapene carolina",
        "common_name": "Dogu Kutu Kaplumbagasi",
        "photos_wanted": 3,
    },
]

INAT_API = "https://api.inaturalist.org/v1"
IMG_SIZE  = 224
HEADERS   = {"User-Agent": "TurtleID-Research/1.0 (educational, non-commercial)"}


# ─────────────────────────────────────────────────────────────────────────────
#  Yardimci fonksiyonlar
# ─────────────────────────────────────────────────────────────────────────────

def _get_json(url: str, timeout: int = 15) -> dict:
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def _resolve_taxon_id(taxon_name: str) -> int | None:
    """Tur adini iNaturalist taxon_id'ye donustur."""
    q   = urllib.parse.quote(taxon_name)
    url = f"{INAT_API}/taxa?q={q}&rank=species&per_page=5"
    try:
        data = _get_json(url)
        for result in data.get("results", []):
            if result.get("name", "").lower() == taxon_name.lower():
                return result["id"]
        # Tam esleme yoksa ilk sonucu kullan
        results = data.get("results", [])
        if results:
            return results[0]["id"]
    except Exception as exc:
        print(f"  [uyari] taxon_id alinamadi ({taxon_name}): {exc}")
    return None


def _fetch_observations(taxon_id: int, count: int) -> list[dict]:
    """Verilen taxon_id icin CC lisansli, arastirma kalitesi gozlemleri cek."""
    params = "&".join([
        f"taxon_id={taxon_id}",
        "quality_grade=research",
        "license=cc-by,cc-by-nc,cc0",
        "photos=true",
        f"per_page={min(count * 4, 30)}",
        "order_by=votes",
        "order=desc",
    ])
    url = f"{INAT_API}/observations?{params}"
    data = _get_json(url)
    return data.get("results", [])


def _download_image(url: str, dest: str, timeout: int = 20) -> bool:
    """Goruntu URL'den indir, 224x224 letterbox ile kaydet."""
    try:
        import cv2        # noqa: PLC0415
        import numpy as np  # noqa: PLC0415

        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = r.read()

        arr = np.frombuffer(data, np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if img is None:
            return False

        # Letterbox resize -> 224x224
        h, w   = img.shape[:2]
        scale  = IMG_SIZE / max(h, w)
        nh, nw = int(h * scale), int(w * scale)
        resized = cv2.resize(img, (nw, nh), interpolation=cv2.INTER_AREA)
        canvas  = np.zeros((IMG_SIZE, IMG_SIZE, 3), np.uint8)
        y0      = (IMG_SIZE - nh) // 2
        x0      = (IMG_SIZE - nw) // 2
        canvas[y0:y0+nh, x0:x0+nw] = resized

        cv2.imwrite(dest, canvas, [cv2.IMWRITE_JPEG_QUALITY, 92])
        return True
    except Exception as exc:
        print(f"    [uyari] Goruntu indirilemedi: {exc}")
        return False


# ─────────────────────────────────────────────────────────────────────────────
#  Ana indirici
# ─────────────────────────────────────────────────────────────────────────────

def download_all(output_dir: str = "data/real_photos") -> None:
    import shutil   # noqa: PLC0415
    # Onceki bozuk indirmeyi temizle
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    metadata: list[dict] = []
    total_downloaded      = 0
    used_obs_ids: set[int] = set()   # diger turlerle capakismayi onle

    for species in TARGET_SPECIES:
        taxon_name  = species["taxon_name"]
        common_name = species["common_name"]
        wanted      = species["photos_wanted"]

        print(f"\n[{common_name}]  ({taxon_name})")

        # 1. taxon_id bul
        taxon_id = _resolve_taxon_id(taxon_name)
        if taxon_id is None:
            print(f"  [hata] taxon_id bulunamadi, atlanıyor.")
            continue
        print(f"  taxon_id = {taxon_id}")
        time.sleep(0.4)

        # 2. Gozlemleri cek
        try:
            observations = _fetch_observations(taxon_id, wanted)
        except Exception as exc:
            print(f"  [hata] API: {exc}")
            continue
        time.sleep(0.4)

        # 3. En fazla fotografi olan gozlemi sec → ayni bireyden cok aci
        #    Boylece photo_01/02/03 AYNI kaplumbaganin farkli acilarini temsil eder.
        safe_name = taxon_name.replace(" ", "_")
        folder    = os.path.join(output_dir, safe_name)
        os.makedirs(folder, exist_ok=True)

        best_obs   = None
        best_count = 0
        for obs in observations:
            obs_id = obs.get("id")
            if obs_id in used_obs_ids:
                continue
            n = len(obs.get("photos", []))
            if n > best_count:
                best_count = n
                best_obs   = obs

        # Eger cok fotografli gozlem yoksa ilk uygun gozlemi kullan
        if best_obs is None:
            for obs in observations:
                obs_id = obs.get("id")
                if obs_id not in used_obs_ids and obs.get("photos"):
                    best_obs = obs
                    break

        if best_obs is None:
            print(f"  [hata] Uygun gozlem bulunamadi.")
            continue

        obs_id    = best_obs["id"]
        all_photos = best_obs.get("photos", [])
        used_obs_ids.add(obs_id)

        # Tek gozlemde birden az fotograf varsa ek gozlemlerden tamamla
        candidate_photos: list[tuple] = []  # (url, license, obs_id, attribution)
        for ph in all_photos:
            url = ph.get("url", "").replace("/square.", "/medium.")
            candidate_photos.append((url, ph.get("license_code","?"), obs_id,
                                     best_obs.get("user",{}).get("login","?")))

        # Yetmiyorsa baska gozlemlerden ekle (farkli birey — yedek)
        if len(candidate_photos) < wanted:
            for obs in observations:
                oid = obs.get("id")
                if oid == obs_id or oid in used_obs_ids:
                    continue
                for ph in obs.get("photos", [])[:1]:
                    url = ph.get("url", "").replace("/square.", "/medium.")
                    candidate_photos.append((url, ph.get("license_code","?"), oid,
                                             obs.get("user",{}).get("login","?")))
                    used_obs_ids.add(oid)
                    if len(candidate_photos) >= wanted:
                        break
                if len(candidate_photos) >= wanted:
                    break

        saved = 0
        for url, lic, oid, attr in candidate_photos[:wanted]:
            dest = os.path.join(folder, f"photo_{saved+1:02d}.jpg")
            ok   = _download_image(url, dest)
            if not ok:
                continue
            saved            += 1
            total_downloaded += 1
            print(f"  [ok] photo_{saved:02d}.jpg  obs={oid}  lisans={lic}  kaynak={attr}")
            metadata.append({
                "taxon":          taxon_name,
                "common_name":    common_name,
                "taxon_id":       taxon_id,
                "observation_id": oid,
                "inat_url":       f"https://www.inaturalist.org/observations/{oid}",
                "photo_license":  lic,
                "local_path":     dest,
                "attribution":    attr,
                "note": "same_individual" if oid == obs_id else "different_individual_backup",
            })
            time.sleep(0.4)

        if saved == 0:
            print(f"  [hata] Hic fotograf indirilemedi.")

        if saved < wanted:
            print(f"  [uyari] {saved}/{wanted} fotograf indirilebildi")

    # Metadata kaydet
    meta_path = os.path.join(output_dir, "metadata.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*55}")
    print(f"  {total_downloaded} gercek kaplumbaga fotografu indirildi")
    print(f"  Kaynak: {output_dir}/metadata.json")
    print(f"{'='*55}")
    print()
    print("KULLANIM:")
    print("  Kayit   -> her klasordeki photo_01.jpg")
    print("  Test    -> photo_02.jpg / photo_03.jpg (ayni tur, farkli fotograf)")
    print("  Negatif -> farkli turun herhangi bir fotografiyla deneyin")


if __name__ == "__main__":
    root   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output = os.path.join(root, "data", "real_photos")
    print("iNaturalist'ten gercek kaplumbaga fotograflari indiriliyor...")
    print("(taxon_id ile filtreleme, CC lisansli, capakisma korumali)\n")
    download_all(output)
