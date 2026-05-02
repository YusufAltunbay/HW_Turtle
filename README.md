# Turtle ID — Kaplumbaga Fotograf Tanima Sistemi

Farkli zamanlarda cekilen fotograflardan ayni kaplumbagayi eslestirebilen,
PySide6 arayuzlu, multi-agent mimarili Python uygulamasi.

---

## Mimari Ozet

```
UIAgent  ──►  ImageAgent  ──►  MatchingAgent
               │                    │
               ▼                    ▼
         EfficientNet-B0      CosineSimilarity
               │                    │
               └──────► DataAgent ◄─┘
                         (SQLite)
```

| Katman | Teknoloji |
|--------|-----------|
| Goruntu ozellikleri | EfficientNet-B0 (timm) — 1280 boyutlu vektor |
| Esleme | Cosine Similarity (scikit-learn) |
| Veritabani | SQLite + SQLAlchemy (WAL modu) |
| Arayuz | PySide6 (QThread worker'lar) |
| Olay tasiyici | Thread-safe EventBus |

---

## Kurulum

### 1. Python Surumu

Python **3.11** veya **3.12** onerilir.  
(Python 3.13 de desteklenir; testler gectigi dogrulandi.)

```bash
python --version
```

### 2. Sanal Ortam Olustur

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python -m venv .venv
source .venv/bin/activate
```

### 3. Bagimliliklar

#### a) PyTorch (CPU)

```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

> GPU varsa: `pip install torch torchvision` (CUDA otomatik secilir)

#### b) Diger paketler

```bash
pip install timm opencv-python PySide6 sqlalchemy loguru scikit-learn numpy
```

#### c) Tek satirda (pyproject.toml ile)

```bash
pip install -e ".[dev]"
```

---

## Uygulamayi Calistir

```bash
# Proje kokunden (venv aktifken):
python -c "import sys; sys.path.insert(0,'src'); from turtle_id.app import main; main()"
```

Ya da daha pratik:

```bash
# Windows PowerShell
$env:PYTHONPATH="src"; python -m turtle_id.app

# macOS / Linux
PYTHONPATH=src python -m turtle_id.app
```

---

## Test Verisini Olustur

Sistemin davranisini denemek icin sentetik kaplumbaga fotograflari olusturabilirsin:

```bash
python data/generate_test_photos.py
```

Bu komut `data/sample_photos/` altinda 5 kaplumbaga × 3 fotograf = **15 JPEG** dosyasi uretir:

```
data/sample_photos/
  turtle_alpha/   photo_01.jpg  photo_02.jpg  photo_03.jpg
  turtle_beta/    photo_01.jpg  photo_02.jpg  photo_03.jpg
  turtle_gamma/   photo_01.jpg  photo_02.jpg  photo_03.jpg
  turtle_delta/   photo_01.jpg  photo_02.jpg  photo_03.jpg
  turtle_epsilon/ photo_01.jpg  photo_02.jpg  photo_03.jpg
```

Her klasordeki fotograflar **ayni** kaplumbagaya ait; farkli isik ve gurultu kosuluyla uretilmistir.

---

## Adim Adim Test Senaryosu

### Senaryo 1 — Dogru Esleme

1. **Uygulamayi calistir**
2. Sol menuден **"Kayit"** sayfasini ac
3. `data/sample_photos/turtle_alpha/photo_01.jpg` sec
4. Ad: `Alpha`, Tur: `Caretta caretta` yaz → **Kaydet**
5. Sol menuден **"Dogrulama"** sayfasini ac
6. `data/sample_photos/turtle_alpha/photo_02.jpg` sec → **Dogrula**
7. Beklenen: **"Esleme Bulundu"** + benzerlik skoru > 0.75

### Senaryo 2 — Yanlis Esleme (Farkli Kaplumbaga)

1. Ayni adimlarla `turtle_beta/photo_01.jpg` kayit et
2. Dogrulamada `turtle_alpha/photo_02.jpg` kullan
3. Beklenen: `Alpha` ile yuksek skor, `Beta` ile dusuk skor

### Senaryo 3 — Bilinmeyen Kaplumbaga

1. Sadece `turtle_alpha` kayitli olsun
2. Dogrulamada `turtle_gamma/photo_01.jpg` kullan (kayitli degil)
3. Beklenen: **"Esleme Bulunamadi"**

---

## Testleri Calistir

```bash
# Proje kokunden:
python -m pytest tests/ -v
```

Beklenen cikti: **41 test gectи** (unit + entegrasyon)

---

## Ayarlar

Arayuzdeki **"Ayarlar"** sayfasindan:

| Ayar | Varsayilan | Aciklama |
|------|-----------|----------|
| Benzerlik Esigi | 0.75 | Bu degerin altindaki skor "esleme yok" sayilir |
| Top-K Aday | 5 | Kac aday kaplumbaga karsilastirilacak |

Degerler `data/settings.json` dosyasina kaydedilir.

---

## Proje Yapisi

```
HW_Turtle/
  src/turtle_id/
    agents/          # 7 ajan (ImageAgent, MatchingAgent, DataAgent, ...)
    core/
      models/        # Turtle, Embedding, MatchResult domain modelleri
      ports/         # Soyut arayuzler (DIP)
      use_cases/     # RegisterTurtle, VerifyTurtle is mantigi
    infrastructure/
      persistence/   # SQLite + SQLAlchemy
      vision/        # EfficientNet-B0, OpenCV onisleme
      matching/      # Cosine Similarity
    ui/
      views/         # Kayit, Dogrulama, Sonuc, Gecmis, Ayarlar
    shared/          # EventBus, EventType
    app.py           # Giris noktasi
    container.py     # Bagimlilik enjeksiyonu
  tests/             # 41 birim + entegrasyon testi
  data/
    generate_test_photos.py
    sample_photos/   # Uretilen test fotograflari
```

---

## Sorun Giderme

| Hata | Cozum |
|------|-------|
| `No module named 'turtle_id'` | `PYTHONPATH=src` ortam degiskenini ayarla |
| `No module named 'sklearn'` | `pip install scikit-learn` |
| `No module named 'timm'` | `pip install timm` |
| `QApplication` hatasi | PySide6'yi yukle: `pip install PySide6` |
| Ilk calistirmada yavas baslangi | EfficientNet-B0 modeli internetten indiriliyor (~21 MB) |
| `PermissionError` (Windows) | Veritabani dosyasini baska bir uygulama kilitledi; uygulamayi kapat ve tekrar ac |
