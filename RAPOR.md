# Turtle ID — Kaplumbaga Fotograf Tanim Sistemi
## Clean Code · SOLID · Coklu Ajan Mimari Raporu

**Proje:** HW_Turtle  
**GitHub:** https://github.com/YusufAltunbay/HW_Turtle  
**Dil:** Python 3.11+  
**Tarih:** Mayis 2026

---

## ICERIK

1. Proje Ozeti
2. Mimari Genel Bakis
3. SOLID Prensipleri
4. Clean Code Prensipleri
5. Coklu Ajan (Multi-Agent) Mimarisi
6. EventBus Mekanizmasi
7. Port / Adapter (Hexagonal) Mimarisi
8. Test Yapisi
9. Kod Istatistikleri
10. Ozet

---

## 1. PROJE OZETI

Turtle ID, farkli zamanlarda cekilen kaplumbaga fotograflarindan ayni bireyi
taniyabilen bir gorsel esleme sistemidir. EfficientNet-B0 modeli her fotograftan
1280 boyutlu bir ozellik vektoru cikararak kaplumbagalari birbirinden ayirt eder.

**Temel Ozellikler**

| Ozellik | Teknoloji |
|---------|-----------|
| Goruntu ozelligi cikartma | EfficientNet-B0 (timm) — 1280 dim |
| Esleme algoritmasi | Cosine Similarity (scikit-learn) |
| Goruntu on isleme | OpenCV (letterbox + CLAHE + ImageNet normalize) |
| Veritabani | SQLite + SQLAlchemy 2.0 (WAL modu) |
| Kullanici arayuzu | PySide6 (Qt 6, QThread worker'lar) |
| Ajan iletisimi | Thread-safe EventBus (pub/sub) |
| Bagimlilik yonetimi | Manuel DI Konteyneri (AppContainer) |

---

## 2. MIMARI GENEL BAKIS

```
┌──────────────────────────────────────────────────────┐
│                    UI KATMANI                         │
│  PySide6 MainWindow  →  RegisterView / VerifyView    │
│  QThread Workers  →  RegisterWorker / VerifyWorker   │
└───────────────────────┬──────────────────────────────┘
                        │ cagri
┌───────────────────────▼──────────────────────────────┐
│               USE CASE KATMANI                        │
│  RegisterTurtleUseCase    VerifyTurtleUseCase         │
│  (frozen dataclass DTO'lar ile tip guvenligi)         │
└──────┬──────────────────────────────────┬────────────┘
       │ ajan cagrisi                      │
┌──────▼──────────────────────────────────▼────────────┐
│               AJAN KATMANI                            │
│  PhotoValidationAgent   ImageAgent   MatchingAgent   │
│  DataAgent              ConfigAgent  UIAgent          │
│  ────────────── EventBus (pub/sub) ──────────────    │
└──────┬──────────────────────────────────┬────────────┘
       │ port arayuzu                      │
┌──────▼──────────────────────────────────▼────────────┐
│              ALTYAPI KATMANI (Adapters)               │
│  OpenCVPreprocessor       TimmEfficientNetExtractor  │
│  CosineMatcher            SQLiteTurtleRepository     │
└──────────────────────────────────────────────────────┘
```

### Klasor Yapisi

```
src/turtle_id/
  agents/           7 ajan (BaseAgent'tan turetilmis)
  core/
    models/         4 domain modeli (Turtle, Embedding, MatchResult)
    ports/          4 soyut arayuz (ITurtleRepository, IMatcher, ...)
    use_cases/      2 is akisi (Register, Verify)
  infrastructure/
    persistence/    SQLite + SQLAlchemy ORM
    vision/         EfficientNet-B0, OpenCV
    matching/       Cosine Similarity
  ui/
    views/          5 gorsel sayfa
    widgets/        2 ozel widget
  shared/           EventBus + EventType enum
  app.py            Giris noktasi
  container.py      DI Konteyneri
tests/
  unit/             4 dosya, 31 test
  integration/      1 dosya, 10 test
```

---

## 3. SOLID PRENSİPLERİ

### 3.1 SRP — Tek Sorumluluk Prensibi

Her sinif ve ajan yalnizca bir nedenden degisir.

| Sinif / Ajan | Tek Sorumlulugu | Yapmadigi |
|---|---|---|
| `EventBus` | Pub/sub mekanizmasi | Is mantigi, veri erisimi |
| `ConfigAgent` | Ayar okuma / yazma | Esleme, embedding |
| `PhotoValidationAgent` | Fotograf kalitesi kontrolu | Kayit, esleme |
| `ImageAgent` | Embedding vektoru uretimi | Veritabani, esleme |
| `MatchingAgent` | Cosine esleme | Veri kaydetme, UI |
| `DataAgent` | CRUD islemleri | Goruntu isleme |
| `OpenCVPreprocessor` | Fotograf on isleme | Feature extraction |
| `TimmEfficientNetExtractor` | Feature extraction | On isleme, esleme |
| `CosineMatcher` | Benzerlik hesabi | Vektoru cikarma |
| `SQLiteTurtleRepository` | SQLite erisimi | Is mantigi |
| `RegisterTurtleUseCase` | Kayit akisi orkestrasyonu | Veri erisimi |
| `VerifyTurtleUseCase` | Dogrulama akisi | Kayit, veri depolama |

**Somut Ornek — PhotoValidationAgent:**

```python
class PhotoValidationAgent(BaseAgent):
    # Dosya varligini kontrol eder
    def _check_file_exists(self, path, result): ...
    # Uzantiyi kontrol eder
    def _check_extension(self, path, result): ...
    # Bulaniklik kontrolu (Laplacian variance)
    def _check_blur(self, img, result): ...
    # Parlaklik kontrolu
    def _check_brightness(self, img, result): ...

    # YAPMADIGI:
    # - Embedding uretme
    # - Veritabani yazma
    # - Esleme
```

### 3.2 OCP — Acik/Kapali Prensibi

Mevcut kod degistirilmeden genisletilebilir.

**Port Arayuzleri sayesinde yeni adapter eklemek:**

```python
# Mevcut:
class CosineMatcher(IMatcher): ...

# Yeni (mevcut kod DEGISMEZ):
class FAISSMatcher(IMatcher):
    def find_best_match(self, query, candidates, threshold, top_k):
        # Milyonlarca embedding icin cok daha hizli FAISS kullan
        ...

# container.py'da tek satirlik degisiklik:
matcher = FAISSMatcher()   # onceki: CosineMatcher()
```

Ayni sekilde:
- `OpenCVPreprocessor` → `PytorchPreprocessor` (IImagePreprocessor)
- `TimmEfficientNetExtractor` → `ResNet50Extractor` (IEmbeddingExtractor)
- `SQLiteTurtleRepository` → `PostgreSQLRepository` (ITurtleRepository)

**EventType genisletme:**

```python
class EventType(Enum):
    ...
    # Yeni olay eklemek: sadece buraya bir satir
    BATCH_PROCESSING_DONE = "batch.done"
```

Tum mevcut ajanlar bu olaydan habersiz; sadece dinlemek isteyen abone olur.

### 3.3 LSP — Liskov Yerine Gecme Prensibi

Turetilmis siniflar temel sinifin yerine kullanilabilir.

```python
# container.py'da tum ajanlar BaseAgent listesiyle yonetilir:
agents: list[BaseAgent] = [
    self._validation_agent,
    self._image_agent,
    self._matching_agent,
    self._data_agent,
]

for agent in agents:
    agent.start()      # Her biri BaseAgent.start() sozlesmesini uygular
    agent.stop()       # Her biri BaseAgent.stop() sozlesmesini uygular
    agent.health_check()  # Polimorfik, tip bilmek gerekmez
```

`AgentStatus` enum'u ile tutarli durum yonetimi:

```python
class AgentStatus(Enum):
    IDLE    = auto()
    BUSY    = auto()
    ERROR   = auto()
    STOPPED = auto()
```

Her ajan bu durumlardan birinde; `health_check()` ERROR veya STOPPED'da False doner.

### 3.4 ISP — Arayuz Ayirma Prensibi

Her port arayuzu minimal ve ozgul:

```python
class IImagePreprocessor(ABC):
    @abstractmethod
    def preprocess(self, image_path: str) -> np.ndarray: ...
    # Tek metod; ImageAgent'in ihtiyaci olan tek sey bu

class IMatcher(ABC):
    @abstractmethod
    def find_best_match(self, query, candidates,
                        threshold, top_k) -> MatchResult: ...
    # Tek metod; MatchingAgent baska bir sey bilmez
```

`ITurtleRepository` biraz daha genis ama her metod en az bir ajan tarafindan kullaniliyor:

| Metod | Kullanan Ajan |
|---|---|
| `save()` | DataAgent |
| `find_by_id()` | DataAgent |
| `find_all()` | DataAgent |
| `delete()` | DataAgent |
| `add_embedding()` | DataAgent |
| `get_all_embeddings()` | MatchingAgent |
| `get_embeddings_by_turtle()` | DataAgent |

### 3.5 DIP — Bagimlilik Tersine Cevrilmesi

Yuksek seviyeli moduller dusuk seviyeli modullere bagimli degil; ikisi de soyutlamalara bagimli.

```python
# KOTÜ (tight coupling):
class ImageAgent:
    def __init__(self):
        self.preprocessor = OpenCVPreprocessor()    # concrete
        self.extractor    = TimmEfficientNetExtractor()  # concrete

# IYI (DIP):
class ImageAgent(BaseAgent):
    def __init__(self,
                 event_bus:    EventBus,
                 preprocessor: IImagePreprocessor,   # soyut
                 extractor:    IEmbeddingExtractor):  # soyut
        self._preprocessor = preprocessor
        self._extractor    = extractor
```

Tum somut baglanti `container.py`'da tek noktada toplanir:

```python
# container.py — tek birlesim noktasi
preprocessor = OpenCVPreprocessor()         # concrete burada
extractor    = TimmEfficientNetExtractor()  # concrete burada
image_agent  = ImageAgent(event_bus,
                          preprocessor,     # enjekte et
                          extractor)        # enjekte et
```

Faydasi: Unit testlerde gercek model yerine mock enjekte edilebilir.

---

## 4. CLEAN CODE PRENSIPLERİ

### 4.1 Anlamli Isimlendirme

**Sinif isimleri** — ne yaptiklari isimden belli:

```
PhotoValidationAgent    → Fotograf dogrular
TimmEfficientNetExtractor → timm kullanarak EfficientNet ile cikan
SQLiteTurtleRepository  → SQLite ile kaplumbaga verileri
RegisterTurtleUseCase   → Kaplumbagayi kayit eden is akisi
CosineMatcher           → Cosine benzerligiyle eslestirir
```

**Metod isimleri** — fiil + nesne:

```python
validate(image_path)      # ne yaptiyor: validate
find_best_match(query)    # ne yaptiyor: find + best match
add_embedding(embedding)  # ne yaptiyor: add
get_all_embeddings()      # ne dondurdugu belli
has_embeddings()          # bool soru sorar
is_normalized()           # bool soru sorar
health_check()            # ne kontrol ettigi belli
```

**Degisken isimleri:**

```python
similarity_score = 0.876   # magic number degil, isimlendirilmis
matched_turtle_id          # ne oldugu belli
top_candidates             # list, ne icerdigi belli
query_vector               # sorgu vektoru, embedding'den ayri
```

### 4.2 Kucuk Fonksiyonlar

Her metod tek bir is yapar, 20-35 satir siniri:

```python
# PhotoValidationAgent: 7 kucuk ozel metod
def _check_file_exists(self, path, result):   # ~10 satir
def _check_extension(self, path, result):     # ~8 satir
def _check_image_readable(self, path, result): # ~12 satir
def _check_dimensions(self, img, result):     # ~10 satir
def _check_blur(self, img, result):           # ~12 satir
def _check_brightness(self, img, result):     # ~12 satir

# Ana metod sadece orkestre eder:
def validate(self, image_path) -> ValidationResult:
    result = ValidationResult(is_valid=True)
    self._check_file_exists(path, result)
    self._check_extension(path, result)
    ...
    return result
```

### 4.3 Hata Yonetimi

**EventBus — hata izolasyonu:**

```python
for handler in handlers:
    try:
        handler(event_type, payload)
    except Exception as exc:
        logger.error(f"EventBus handler hatasi: {exc}")
        # Diger handler'lar calmaya devam eder
```

**Use Case — hatalar DTO'ya tasiniyor:**

```python
validation = self._validation_agent.validate(request.photo_path)
if not validation.is_valid:
    return RegisterTurtleResponse(
        success=False,
        errors=validation.errors,      # Kullaniciya iletilir
        warnings=validation.warnings,
    )
    # Exception firlatimiyor — UI graceful handle ediyor
```

**Repository — transaction guvenligi:**

```python
with self._session_factory() as session:
    session.add(orm)
    session.commit()
# Context manager otomatik rollback yapar hata durumunda
```

### 4.4 Yorum ve Dokumantasyon

**Modul duzeyi docstring:**

```python
"""
DataAgent: Kaplumbaga kayitlarinin CRUD islemlerini yoneten ajan.

Sorumluluk:
  - Yeni kaplumbaga kaydet
  - ID ile kaplumbaga getir
  - Tum kaplumbagalari listele
  - Mevcut kaplumbagaya yeni embedding/fotograf ekle
  - Dogrulama logunu kaydet

ITurtleRepository arayuzu uzerinden calisir; SQLite detayi gormez.
"""
```

**Ornek — neden degil, ne acikladiginda kotu yorum:**
```python
# KOTU:
i += 1  # i'yi 1 arttir

# IYI (neden acikliyor):
# Lock SADECE dict okuma sirasinda; handler cagrisi lock disinda
# → deadlock riski elimine edildi
```

### 4.5 DRY (Don't Repeat Yourself)

**Mapper metodlari yeniden kullanilir:**

```python
@staticmethod
def _embedding_from_orm(row: EmbeddingORM) -> Embedding:
    vector = np.frombuffer(row.vector_blob, dtype=np.float32).copy()
    return Embedding(turtle_id=UUID(row.turtle_id), vector=vector, ...)

@staticmethod
def _turtle_from_orm(row: TurtleORM) -> Turtle:
    turtle = Turtle(...)
    for emb_row in row.embeddings:
        turtle.add_embedding(
            SQLiteTurtleRepository._embedding_from_orm(emb_row)  # ← tekrar kullanim
        )
    return turtle
```

**BaseAgent kisa yollar:**

```python
# BaseAgent._publish() ve _subscribe() metodlari
# tum ajanlar self._event_bus.publish(...) yerine
# self._publish(...) yazar → DRY
def _publish(self, event_type, payload=None):
    self._event_bus.publish(event_type, payload)

def _subscribe(self, event_type, handler):
    self._event_bus.subscribe(event_type, handler)
```

### 4.6 Type Hints

Projenin tum fonksiyonlari Python 3.11+ tip notasyonuna sahip:

```python
from __future__ import annotations  # PEP 563 — lazy evaluation

def match(self, query_vector: np.ndarray) -> MatchResult:
def find_best_match(
    self,
    query_vector: np.ndarray,
    candidates: list[Embedding],
    threshold: float,
    top_k: int,
) -> MatchResult: ...

def get_turtle(self, turtle_id: UUID) -> Turtle | None: ...
def list_turtles(self) -> list[Turtle]: ...
```

### 4.7 Frozen Dataclass ile Immutable DTO'lar

Use Case girdi/ciktilari degistirilemez (yanlislikla mutasyon engellenir):

```python
@dataclass(frozen=True)
class RegisterTurtleRequest:
    name: str
    photo_path: str
    species: str = ""
    notes: str = ""

@dataclass(frozen=True)
class VerifyTurtleRequest:
    photo_path: str
```

---

## 5. COKLU AJAN (MULTI-AGENT) MIMARISI

### 5.1 Ajan Tanimlari

**1. ConfigAgent**

```
Gorev   : Uygulama ayarlarini okur, yazar, yayimlar
Giris   : settings.json (JSON dosyasi)
Cikis   : In-memory dict + CONFIG_CHANGED olayi
Bagimli : Yok (dosya sistemi haric)
Dinledigi: Hicbir sey
Yayimladigi: CONFIG_CHANGED
```

**2. PhotoValidationAgent**

```
Gorev   : Fotografin kalitesini dogrular
Giris   : image_path: str
Cikis   : ValidationResult (is_valid, errors, warnings)
Kontroller:
  - Dosya varligini kontrol et
  - Uzanti kontrolu (.jpg .jpeg .png .bmp .tiff .webp)
  - OpenCV ile okuma testi
  - Minimum boyut: 100x100 piksel
  - Bulaniklik: Laplacian variance > 50.0
  - Parlaklik: 20 < ortalama < 240
```

**3. ImageAgent**

```
Gorev   : Fotograftan L2-normalize embedding vektoru uretir
Giris   : image_path, turtle_id
Cikis   : Embedding (1280 dim float32 ndarray)
Adimlar :
  1. OpenCVPreprocessor → (224,224,3) tensoru
  2. TimmEfficientNetExtractor → (1280,) raw features
  3. L2 normalize → norm ≈ 1.0
  4. Embedding nesnesi sarmalanir
Yayimladigi: EMBEDDING_STARTED, EMBEDDING_READY, EMBEDDING_FAILED
```

**4. MatchingAgent**

```
Gorev   : Sorgu embeddingini veritabanindaki tumuyle karsilastirir
Giris   : query_vector: np.ndarray (1280,)
Cikis   : MatchResult (is_match, score, matched_turtle_id, top_k)
Algoritma:
  1. Repository'den tum aktif embeddingleri cek
  2. (N, 1280) matrisi olustur
  3. cosine_similarity(query, matrix) → (N,) skorlar
  4. argsort descending → top-k adaylar
  5. best_score >= threshold ise MATCH_FOUND, degilse MATCH_NOT_FOUND
Dinamik esik: CONFIG_CHANGED olayini dinleyerek threshold gunceller
```

**5. DataAgent**

```
Gorev   : Kaplumbaga ve embedding CRUD islemleri + dogrulama logu
Public API :
  save_turtle(turtle)    → TURTLE_SAVED
  get_turtle(id)         → TURTLE_LOADED
  list_turtles()         → list[Turtle]
  add_embedding(emb)     → Embedding
Otomatik :
  MATCH_FOUND / MATCH_NOT_FOUND dinler
  → VerificationLogORM'a otomatik yazar (audit trail)
```

**6. UIAgent**

```
Gorev   : PySide6 Qt Signal/Slot ile UI aksiyonlarini is akislarina baglar
Sayfalar:
  - RegisterView  → RegisterWorker (QThread) → RegisterTurtleUseCase
  - VerifyView    → VerifyWorker  (QThread) → VerifyTurtleUseCase
  - HistoryView   → DataAgent.list_turtles() + verification log
  - SettingsView  → ConfigAgent.set()
  - ResultView    → MatchResult gorsellestirme
```

### 5.2 Ajan Bagimliliklari

```
AppContainer
    │
    ├── EventBus ──────────────────────────────────┐
    │                                               │ (pub/sub)
    ├── ConfigAgent ──────────── CONFIG_CHANGED ────┤
    │                                               │
    ├── PhotoValidationAgent ── PHOTO_VALID ────────┤
    │                                               │
    ├── ImageAgent                                  │
    │     ├── IImagePreprocessor (OpenCVPreprocessor)│
    │     └── IEmbeddingExtractor (TimmExtractor)   │
    │                            EMBEDDING_READY ───┤
    │                                               │
    ├── MatchingAgent                               │
    │     ├── IMatcher (CosineMatcher)              │
    │     └── ITurtleRepository ← MATCH_FOUND ──────┤
    │                                               │
    └── DataAgent                                   │
          └── ITurtleRepository  ← MATCH_FOUND ─────┘
                                    (otomatik log)
```

### 5.3 Is Akisi: Kaplumbaga Kaydı

```
Kullanici "Kaydet" tiklar
    │
    ▼
RegisterWorker(QThread).run()
    │
    ▼
RegisterTurtleUseCase.execute(RegisterTurtleRequest(name, photo_path))
    │
    ├─► PhotoValidationAgent.validate(photo_path)
    │       ├── PHOTO_VALIDATION_STARTED yayimla
    │       ├── _check_file_exists()
    │       ├── _check_extension()
    │       ├── _check_image_readable()
    │       ├── _check_dimensions()
    │       ├── _check_blur()
    │       ├── _check_brightness()
    │       └── PHOTO_VALID yayimla
    │
    ├─► Turtle nesnesi olustur (UUID otomatik)
    │
    ├─► ImageAgent.process(photo_path, turtle.id)
    │       ├── EMBEDDING_STARTED yayimla
    │       ├── OpenCVPreprocessor.preprocess() → (224,224,3) tensor
    │       ├── TimmEfficientNetExtractor.extract() → (1280,) vektor
    │       ├── L2 normalize
    │       └── EMBEDDING_READY yayimla → Embedding nesnesi
    │
    ├─► turtle.add_embedding(embedding)
    │
    └─► DataAgent.save_turtle(turtle)
            ├── SQLiteTurtleRepository.save()
            │     ├── TurtleORM olustur
            │     ├── EmbeddingORM olustur (vector_blob = float32 bytes)
            │     └── session.commit()
            └── TURTLE_SAVED yayimla

Sonuc: RegisterTurtleResponse(success=True, turtle=saved_turtle)
    │
    ▼
Qt Signal → Ana thread → UI guncellenir
```

### 5.4 Is Akisi: Kaplumbaga Dogrulama

```
Kullanici "Dogrula" tiklar
    │
    ▼
VerifyWorker(QThread).run()
    │
    ▼
VerifyTurtleUseCase.execute(VerifyTurtleRequest(photo_path))
    │
    ├─► PhotoValidationAgent.validate(photo_path)  [ayni kontroller]
    │
    ├─► ImageAgent.process(photo_path, uuid4())    [gecici UUID]
    │       └── Sorgu embedding'i
    │
    ├─► MatchingAgent.match(query_embedding.vector)
    │       ├── MATCHING_STARTED yayimla
    │       ├── Repository.get_all_embeddings()  → N adet vektor
    │       ├── np.stack() → (N, 1280) matris
    │       ├── cosine_similarity(query, matrix) → (N,) skorlar
    │       ├── argsort[::-1][:top_k]  → top-3 aday
    │       └── best_score >= threshold?
    │             Evet → MATCH_FOUND yayimla     ──┐
    │             Hayir → MATCH_NOT_FOUND yayimla ─┤
    │                                              │
    │                         DataAgent dinler ←──┘
    │                         VerificationLogORM kaydeder (otomatik)
    │
    ├─► Eslesme varsa: DataAgent.get_turtle(matched_id)
    │       └── TURTLE_LOADED yayimla
    │
    └─► match_result.matched_turtle = turtle

Sonuc: VerifyTurtleResponse(success=True, match_result, turtle)
    │
    ▼
Qt Signal → Ana thread → ResultView gosterilir
```

---

## 6. EVENTBUS MEKANIZMASI

### 6.1 Tasarim Kararlari

EventBus, ajanlar arasi dogrudan import'u ortadan kaldiran merkezi iletisim katmanidir.

```
KOTU (tight coupling):
  DataAgent → MatchingAgent.some_method()
  → DataAgent, MatchingAgent'i import etmek zorunda
  → Circular import riski
  → Test ederken her ikisini de hazirlamak gerekir

IYI (EventBus):
  MatchingAgent → EventBus.publish(MATCH_FOUND, result)
  DataAgent ← EventBus.subscribe(MATCH_FOUND, self._on_match_found)
  → Birbirini tanimiyorlar
  → Test ederken sadece EventBus gerekli
```

### 6.2 Thread Safety

```python
class EventBus:
    def __init__(self):
        self._handlers = defaultdict(list)
        self._lock = threading.Lock()

    def subscribe(self, event_type, handler):
        with self._lock:          # ← Kritik bolge (kisa)
            self._handlers[event_type].append(handler)

    def publish(self, event_type, payload=None):
        with self._lock:
            handlers = list(self._handlers.get(event_type, []))
        # Lock BURADA BITTI — handler cagrisinda deadlock riski yok

        for handler in handlers:
            try:
                handler(event_type, payload)
            except Exception as exc:
                logger.error(...)  # Hata izolasyonu
```

**Tasarim:** Lock yalnizca dict okuma/yazma icin alinir. Handler cagrisi lock disinda yapilir — bu sayede bir handler baska bir olay publish etse bile deadlock olusmuyor.

### 6.3 Olay Tipleri

```python
class EventType(Enum):
    # Fotograf dogrulama
    PHOTO_VALIDATION_STARTED = "photo.validation.started"
    PHOTO_VALID              = "photo.valid"
    PHOTO_INVALID            = "photo.invalid"

    # Embedding
    EMBEDDING_STARTED = "embedding.started"
    EMBEDDING_READY   = "embedding.ready"
    EMBEDDING_FAILED  = "embedding.failed"

    # Esleme
    MATCHING_STARTED  = "matching.started"
    MATCH_FOUND       = "match.found"
    MATCH_NOT_FOUND   = "match.not_found"

    # Veri
    TURTLE_SAVED      = "turtle.saved"
    TURTLE_LOADED     = "turtle.loaded"
    DATA_ERROR        = "data.error"

    # Konfigurasyon
    CONFIG_CHANGED    = "config.changed"
```

### 6.4 Abone Tablosu

| Olay | Yayimlayan | Dinleyen |
|------|-----------|---------|
| PHOTO_VALID | PhotoValidationAgent | — |
| EMBEDDING_READY | ImageAgent | — |
| MATCH_FOUND | MatchingAgent | DataAgent (otomatik log) |
| MATCH_NOT_FOUND | MatchingAgent | DataAgent (otomatik log) |
| CONFIG_CHANGED | ConfigAgent | AppContainer (→ MatchingAgent) |
| TURTLE_SAVED | DataAgent | — |

---

## 7. PORT / ADAPTER (HEXAGONAL) MIMARI

### 7.1 Katamanli Bagimlilik Kurali

```
UI Katmani
    ↓ (cagri)
Use Case Katmani
    ↓ (port arayuzu)
Core / Domain Katmani
    ↑ (implement eder)
Adapter Katmani
    ↓ (kullanir)
Harici Sistemler (SQLite, OpenCV, timm, sklearn)
```

Kural: icerideki katman, disdakini tanimaz. Disari acan kapi port arayuzleridir.

### 7.2 Port ↔ Adapter Eslesme

```
PORT (soyut)                  ADAPTER (somut)           Harici Sistem
─────────────────────────     ─────────────────────     ─────────────────
ITurtleRepository         ←→  SQLiteTurtleRepository    SQLAlchemy + SQLite
IImagePreprocessor        ←→  OpenCVPreprocessor         OpenCV + numpy
IEmbeddingExtractor       ←→  TimmEfficientNetExtractor  timm + PyTorch
IMatcher                  ←→  CosineMatcher              scikit-learn
```

### 7.3 Adapter Degistirme Ornegi

**Senaryo:** SQLite yerine PostgreSQL kullanmak

```python
# 1. Yeni adapter yaz:
class PostgreSQLRepository(ITurtleRepository):
    def __init__(self, connection_string: str): ...
    def save(self, turtle: Turtle) -> Turtle: ...
    # Diger metodlar...

# 2. container.py'da tek satirlik degisiklik:
# ONCEKI: repository = SQLiteTurtleRepository(session_factory)
repository = PostgreSQLRepository("postgresql://...")

# Hicbir use case, ajan veya test degismiyor.
```

**Senaryo:** EfficientNet yerine ResNet50 kullanmak

```python
class ResNet50Extractor(IEmbeddingExtractor):
    def extract(self, image: np.ndarray) -> np.ndarray:
        # ResNet50 ile 2048-dim vektor
        ...
    @property
    def model_name(self) -> str: return "resnet50"
    @property
    def embedding_dim(self) -> int: return 2048

# container.py:
extractor = ResNet50Extractor()
# Sistem otomatik adapte olur.
```

---

## 8. TEST YAPISI

### 8.1 Test Dosyalari

| Dosya | Tip | Test Sayisi | Kapsam |
|-------|-----|------------|--------|
| `test_event_bus.py` | Birim | 7 | Pub/sub, thread safety, hata izolasyonu |
| `test_matcher.py` | Birim | 7 | Cosine esleme, esik mantigi, top-k |
| `test_models.py` | Birim | 13 | Turtle, Embedding, MatchResult |
| `test_validation_agent.py` | Birim | 4 | Fotograf dogrulama + EventBus |
| `test_repository.py` | Entegrasyon | 10 | SQLite CRUD, vektor saklama |
| **TOPLAM** | | **41** | **%100 gecme** |

### 8.2 Ornek Birim Test

```python
class TestCosineMatcher:
    def test_ayni_vektor_eslesir(self, matcher, make_embedding):
        vec = np.random.randn(128).astype(np.float32)
        vec /= np.linalg.norm(vec)
        query     = vec.copy()
        candidate = make_embedding(vec)

        result = matcher.find_best_match(
            query, [candidate], threshold=0.9, top_k=1
        )

        assert result.is_match is True
        assert result.similarity_score == pytest.approx(1.0, abs=1e-5)

    def test_bos_aday_listesi(self, matcher):
        query  = np.ones(128) / np.sqrt(128)
        result = matcher.find_best_match(query, [], threshold=0.75, top_k=3)
        assert result.is_match is False
```

### 8.3 Entegrasyon Test Duzeni

```python
@pytest.fixture
def repo(tmp_path):
    """In-memory SQLite — disk IO yok, hizli."""
    engine  = build_engine(":memory:")
    factory = build_session_factory(engine)
    init_db(engine)
    return SQLiteTurtleRepository(factory)

def test_embedding_vektoru_bozulmadan_geri_gelir(repo, make_turtle):
    original = np.random.randn(1280).astype(np.float32)
    original /= np.linalg.norm(original)

    turtle = make_turtle()
    embedding = Embedding(turtle_id=turtle.id, vector=original, ...)
    turtle.add_embedding(embedding)
    saved = repo.save(turtle)

    loaded = repo.find_by_id(saved.id)
    restored = loaded.embeddings[0].vector

    np.testing.assert_array_almost_equal(original, restored, decimal=5)
```

---

## 9. KOD ISTATISTIKLERI

| Metrik | Deger |
|--------|-------|
| Kaynak kodu (src/) | **3.974 satir** |
| Test kodu (tests/) | **493 satir** |
| Toplam Python dosyasi | **52 dosya** |
| Ajan sayisi | **6 ajan** (BaseAgent haric) |
| Port arayuzu | **4 arayuz** |
| Adapter implementasyonu | **4 adapter** |
| Use case sayisi | **2 use case** |
| UI sayfasi | **5 sayfa** |
| Birim testi | **31 test** |
| Entegrasyon testi | **10 test** |
| Test basari orani | **%100 (41/41)** |
| Test suresi | **~4 saniye** |

### Katman Dagilimlari (satirla)

```
agents/          ~560  satir  — 6 ajan
core/models/     ~180  satir  — 4 domain modeli
core/ports/      ~170  satir  — 4 port arayuzu
core/use_cases/  ~240  satir  — 2 is akisi
infrastructure/  ~500  satir  — 4 adapter
ui/              ~1200 satir  — 5 sayfa + worker'lar
shared/          ~100  satir  — EventBus + EventType
container.py     ~196  satir  — DI konteyneri
app.py           ~40   satir  — Giris noktasi
```

---

## 10. OZET

### Uygulanan Prensipler

| Prensip | Uygulama Yeri | Kanit |
|---------|--------------|-------|
| **SRP** | Her ajan, her sinif | 12 farkli sorumluluk birbirinden ayrilmis |
| **OCP** | Port arayuzleri | Adapter degisimi 1-2 satir (container.py) |
| **LSP** | BaseAgent hiyerarsisi | `list[BaseAgent]` ile polimorfik yonetim |
| **ISP** | Port arayuzleri | IImagePreprocessor: 1 metod; IMatcher: 1 metod |
| **DIP** | Tum ajanlar | Constructor injection, port arayuzlerine bagli |
| **Anlamli isimler** | Tum kod | Her isim ne yaptigini anlatir |
| **Kucuk fonksiyonlar** | PhotoValidationAgent | 7 kucuk ozel metod |
| **Hata yonetimi** | EventBus, use cases | Hata izolasyonu; DTO hata tasiyor |
| **DRY** | Mapper metodlari | `_embedding_from_orm` tekrar kullaniliyor |
| **Type hints** | Tum metodlar | Python 3.11+ tam tip notasyonu |
| **Frozen DTO** | Use case I/O | `@dataclass(frozen=True)` |
| **Pub/Sub** | EventBus | Ajanlar birbirini import etmiyor |
| **Hexagonal** | Port/Adapter | Harici sistem swap edilebilir |
| **Thread safety** | EventBus, QThread | Lock granülarity optimize |
| **DI Container** | AppContainer | Tum bagimliliklar tek noktada |

### Mimari Guclu Yonler

1. **Degistirilebilirlik:** Veritabani, model veya esleme algoritmasi
   degistirmek icin yalnizca `container.py`'da 1-2 satir degisiklik yeterli

2. **Test edilebilirlik:** Port arayuzleri sayesinde mock enjeksiyonu kolay;
   entegrasyon testleri in-memory SQLite ile disk IO olmadan calisor

3. **Genisletilebilirlik:** Yeni ajan eklemek: `BaseAgent`'i turet,
   `_register_handlers()`'i override et, `container.py`'a ekle

4. **Hata yalitimi:** Bir handler hatasi EventBus'u durdurmaz;
   use case hatalari exception degil DTO ile tasinir

5. **Dusuk baglilik:** Ajanlar birbirini import etmiyor;
   sadece EventBus ve port arayuzleri uzerinden haberlesiyorlar

---

*Rapor GitHub deposundaki son commit durumunu yansitmaktadir.*  
*Repository: https://github.com/YusufAltunbay/HW_Turtle*
