"""
Turtle ID — Odev Raporu PDF Uretici
Calistir: python generate_report_pdf.py
"""
from fpdf import FPDF
from fpdf.enums import XPos, YPos
import os

OUT    = "RAPOR_TurtleID.pdf"
MARGIN = 20
W      = 210 - 2 * MARGIN   # yazilabilir genislik

BLUE   = (30,  80, 150)
LBLUE  = (235, 242, 252)
GRAY   = (100, 100, 100)
LGRAY  = (245, 245, 245)
BLACK  = (30,  30,  30)
WHITE  = (255, 255, 255)
GREEN  = (20, 120, 80)
LGREEN = (230, 248, 238)

FONTS = "C:/Windows/Fonts/"


class PDF(FPDF):

    def setup(self):
        self.add_font("R",  fname=FONTS + "arial.ttf")
        self.add_font("B",  fname=FONTS + "arialbd.ttf")
        self.add_font("I",  fname=FONTS + "ariali.ttf")
        self.add_font("M",  fname=FONTS + "consola.ttf")   # monospace

    # ── sayfa altbilgisi ──────────────────────────────────────────────────
    def footer(self):
        self.set_y(-13)
        self.set_draw_color(*GRAY)
        self.set_line_width(0.3)
        self.line(MARGIN, self.get_y(), 210 - MARGIN, self.get_y())
        self.set_font("I", size=8)
        self.set_text_color(*GRAY)
        self.cell(0, 6, f"Turtle ID Projesi  |  Sayfa {self.page_no()}", align="C")

    # ── yardimci yazicilar ────────────────────────────────────────────────
    def title_text(self, txt, size=13, color=BLUE):
        self.set_font("B", size=size)
        self.set_text_color(*color)
        self.multi_cell(W, 7, txt, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_text_color(*BLACK)

    def body(self, txt, size=10.5, indent=0):
        self.set_font("R", size=size)
        self.set_text_color(*BLACK)
        if indent:
            self.set_x(MARGIN + indent)
        self.multi_cell(W - indent, 5.8, txt, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(0.5)

    def bullet(self, txt, size=10.5):
        self.set_font("R", size=size)
        self.set_text_color(*BLACK)
        self.set_x(MARGIN + 3)
        self.set_text_color(*BLUE)
        self.cell(5, 5.8, chr(0x2022))
        self.set_text_color(*BLACK)
        self.multi_cell(W - 8, 5.8, txt, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def code(self, txt):
        lines = txt.strip().split("\n")
        h     = len(lines) * 4.6 + 5
        if self.get_y() + h > 272:
            self.add_page()
        y0 = self.get_y()
        self.set_fill_color(*LGRAY)
        self.set_draw_color(210, 210, 210)
        self.set_line_width(0.2)
        self.rect(MARGIN, y0, W, h, style="FD")
        # sol mavi bar
        self.set_fill_color(*BLUE)
        self.rect(MARGIN, y0, 2.5, h, style="F")
        self.set_y(y0 + 2.5)
        self.set_font("M", size=8.2)
        self.set_text_color(40, 60, 80)
        for line in lines:
            self.set_x(MARGIN + 6)
            self.cell(W - 6, 4.6, line, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(3)
        self.set_text_color(*BLACK)

    def box(self, baslik, icerik):
        lines = icerik.strip().split("\n")
        h = len(lines) * 5.5 + 12
        if self.get_y() + h > 272:
            self.add_page()
        y0 = self.get_y()
        self.set_fill_color(*LGREEN)
        self.set_draw_color(*GREEN)
        self.set_line_width(0.3)
        self.rect(MARGIN, y0, W, h, style="FD")
        self.set_fill_color(*GREEN)
        self.rect(MARGIN, y0, 3, h, style="F")
        self.set_xy(MARGIN + 6, y0 + 3)
        self.set_font("B", size=9.5)
        self.set_text_color(*GREEN)
        self.cell(W - 6, 6, baslik, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font("R", size=9.5)
        self.set_text_color(*BLACK)
        for line in lines:
            self.set_x(MARGIN + 6)
            self.multi_cell(W - 10, 5.5, line, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(3)

    def section(self, no, txt):
        self.ln(4)
        self.set_fill_color(*BLUE)
        self.set_text_color(*WHITE)
        self.set_font("B", size=11.5)
        self.cell(W, 8.5, f"  {no}. {txt}", fill=True,
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(3)
        self.set_text_color(*BLACK)

    def sub(self, txt):
        self.ln(2)
        self.set_font("B", size=10.5)
        self.set_text_color(*BLUE)
        self.cell(W, 6.5, txt, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_draw_color(*BLUE)
        self.set_line_width(0.4)
        self.line(MARGIN, self.get_y(), MARGIN + W * 0.35, self.get_y())
        self.ln(3)
        self.set_text_color(*BLACK)

    def tablo(self, basliklar, satirlar, genislikler=None):
        n = len(basliklar)
        if not genislikler:
            genislikler = [W / n] * n
        rh = 6.5
        # baslik satiri
        self.set_fill_color(*BLUE)
        self.set_text_color(*WHITE)
        self.set_font("B", size=9)
        self.set_draw_color(200, 210, 225)
        self.set_line_width(0.15)
        for h, g in zip(basliklar, genislikler):
            self.cell(g, rh, "  " + h, border=1, fill=True)
        self.ln()
        # veri satirlari
        for i, satir in enumerate(satirlar):
            if self.get_y() + rh > 272:
                self.add_page()
                self.set_fill_color(*BLUE)
                self.set_text_color(*WHITE)
                self.set_font("B", size=9)
                for h, g in zip(basliklar, genislikler):
                    self.cell(g, rh, "  " + h, border=1, fill=True)
                self.ln()
            fill = (i % 2 == 1)
            self.set_fill_color(*LBLUE)
            self.set_text_color(*BLACK)
            self.set_font("R", size=9)
            for hucre, g in zip(satir, genislikler):
                x0, y0 = self.get_x(), self.get_y()
                self.multi_cell(g, rh, "  " + str(hucre),
                                border=1, fill=fill,
                                new_x=XPos.RIGHT, new_y=YPos.TOP)
                self.set_xy(x0 + g, y0)
            self.ln(rh)
        self.ln(3)

    def cizgi(self):
        self.ln(2)
        self.set_draw_color(200, 210, 225)
        self.set_line_width(0.3)
        self.line(MARGIN, self.get_y(), 210 - MARGIN, self.get_y())
        self.ln(4)


# ═══════════════════════════════════════════════════════════════════════════
def rapor_olustur(pdf: PDF):

    # ── KAPAK ────────────────────────────────────────────────────────────
    pdf.add_page()

    # Ust mavi blok
    pdf.set_fill_color(*BLUE)
    pdf.rect(0, 0, 210, 70, style="F")

    pdf.set_y(15)
    pdf.set_font("B", size=28)
    pdf.set_text_color(*WHITE)
    pdf.cell(0, 14, "Turtle ID", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_font("B", size=13)
    pdf.cell(0, 8, "Kaplumbaga Fotograf Tanim Sistemi", align="C",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_font("I", size=9.5)
    pdf.set_text_color(180, 210, 240)
    pdf.cell(0, 6, "Clean Code  |  SOLID  |  Multi-Agent  |  Odev Raporu",
             align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # Bilgi kutusu
    pdf.set_y(80)
    pdf.set_fill_color(*LBLUE)
    pdf.set_draw_color(200, 210, 225)
    pdf.set_line_width(0.2)
    pdf.rect(MARGIN, 80, W, 48, style="FD")

    bilgiler = [
        ("Proje Adi",       "Turtle ID — Kaplumbaga Fotograf Tanim Sistemi"),
        ("Ogrenci",         "Yusuf Altunbay"),
        ("GitHub",          "github.com/YusufAltunbay/HW_Turtle"),
        ("Programlama Dili","Python 3.11+"),
        ("Kullanici Arayuzu","PySide6 (Qt 6)"),
        ("Veritabani",      "SQLite + SQLAlchemy"),
    ]
    pdf.set_y(84)
    for k, v in bilgiler:
        pdf.set_x(MARGIN + 5)
        pdf.set_font("B", size=9.5)
        pdf.set_text_color(*BLUE)
        pdf.cell(40, 6, k + ":")
        pdf.set_font("R", size=9.5)
        pdf.set_text_color(*BLACK)
        pdf.cell(W - 45, 6, v, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # Ozet sayilar
    pdf.set_y(142)
    kareler = [
        ("3.974", "Satir Kod"),
        ("6",     "Ajan"),
        ("41",    "Test"),
        ("21",    "Git Commit"),
        ("%100",  "Test Basarisi"),
    ]
    kw = W / len(kareler)
    for num, etiket in kareler:
        bx = MARGIN + kareler.index((num, etiket)) * kw
        pdf.set_fill_color(*BLUE)
        pdf.rect(bx, 142, kw - 2, 22, style="F")
        pdf.set_xy(bx, 144)
        pdf.set_font("B", size=15)
        pdf.set_text_color(*WHITE)
        pdf.cell(kw - 2, 9, num, align="C", new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.set_xy(bx, 153)
        pdf.set_font("R", size=7.5)
        pdf.set_text_color(180, 210, 240)
        pdf.cell(kw - 2, 5, etiket, align="C")

    # Icerik listesi
    pdf.set_y(175)
    pdf.set_fill_color(*BLUE)
    pdf.set_text_color(*WHITE)
    pdf.set_font("B", size=10.5)
    pdf.cell(W, 8, "  I C E R I K", fill=True,
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(1)

    icindekiler = [
        ("1", "Projenin Amaci ve Genel Yapisi"),
        ("2", "Kullanilan Teknolojiler"),
        ("3", "Coklu Ajan (Multi-Agent) Mimarisi"),
        ("4", "SOLID Prensipleri"),
        ("5", "Clean Code Prensipleri"),
        ("6", "Temel Is Akislari"),
        ("7", "Test Sonuclari"),
        ("8", "Sonuc ve Degerlendirme"),
    ]
    for no, baslik in icindekiler:
        pdf.set_x(MARGIN + 3)
        pdf.set_font("B", size=10)
        pdf.set_text_color(*BLUE)
        pdf.cell(8, 6.5, no + ".")
        pdf.set_font("R", size=10)
        pdf.set_text_color(*BLACK)
        pdf.cell(W - 11, 6.5, baslik, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # ── 1. AMAC ──────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.section(1, "Projenin Amaci ve Genel Yapisi")

    pdf.body(
        "Bu proje, deniz kaplumbagalarini fotograftan taniyan ve kayit altina alan "
        "bir yazilim sistemidir. Temel problem sudur: farkli zamanlarda, farkli "
        "isik kosullarinda ya da farkli acidan cekilen iki fotograf, ayni "
        "kaplumbagaya mi ait yoksa farkli bireylere mi? Bu soruyu yapayzeka "
        "destekli goruntu isleme teknikleriyle cevaplar."
    )

    pdf.body(
        "Sistem iki temel islevi yerine getirir. Birincisi kayit: bir kaplumbaganin "
        "fotografini sisteme yukleyerek isim ve tur bilgisiyle birlikte veritabanina "
        "kaydeder. Ikincisi dogrulama: yeni cekilen bir fotografin, daha once "
        "kaydedilmis kaplumbagalardan hangisine ait oldugunu benzerlik skoru "
        "uzerinden tespit eder."
    )

    pdf.sub("Nasil Calisir?")
    pdf.body(
        "EfficientNet-B0 adli derin ogrenme modeli, her fotograftan 1280 sayidan "
        "olusan bir parmak izi (embedding vektoru) cikarir. Bu sayilar, kaplumbaganin "
        "kabuk deseni, rengi ve genel gorunumunu temsil eder. Iki fotografin "
        "parmak izleri birbirine ne kadar benziyorsa, benzerlik skoru o kadar "
        "yuksek cikar (0.0 ile 1.0 arasinda). Varsayilan esik 0.82'dir; bu degerin "
        "uzerinde esleme basarili sayilir."
    )

    pdf.box(
        "Ornek Senaryo",
        "Arastirmaci sabah sahile gelen bir kaplumbagayi fotograflar ve sisteme kaydeder.\n"
        "Uc ay sonra benzer bir kaplumbaga tekrar gorulur. Yeni fotograf sisteme yuklenir\n"
        "ve sistem '% 91 benzerlik — Alpha' diyerek bunun ayni birey oldugunu tespit eder."
    )

    pdf.sub("Mimari Ozet")
    pdf.body(
        "Proje, Clean Architecture prensipleriyle katmanlara ayrilmistir. "
        "Her katman yalnizca bir alttakini tanir; yukaridakilere bagimli degildir. "
        "Bu sayede herhangi bir parcayi degistirmek tum sistemi etkilemez."
    )
    pdf.code(
"""Kullanici Arayuzu  (PySide6 — gorsel pencereler)
        |
   Is Akislari       (Kayit ve Dogrulama mantigi)
        |
    Ajanlar          (her biri tek bir isi yapar)
        |
  Altyapi / DB       (SQLite, EfficientNet-B0, OpenCV)""")

    # ── 2. TEKNOLOJILER ───────────────────────────────────────────────────
    pdf.add_page()
    pdf.section(2, "Kullanilan Teknolojiler")

    pdf.tablo(
        ["Teknoloji", "Kullanim Amaci"],
        [
            ["Python 3.11+",          "Ana programlama dili"],
            ["PySide6 (Qt 6)",        "Masaustu kullanici arayuzu"],
            ["EfficientNet-B0 (timm)","Fotograftan 1280 boyutlu ozellik vektoru cikarma"],
            ["OpenCV",                "Goruntu on isleme: yeniden boyutlandirma, normalize"],
            ["Cosine Similarity",     "Iki vektoru karsilastirarak benzerlik skoru uretme"],
            ["SQLite + SQLAlchemy",   "Kaplumbaga ve embedding verilerini saklama"],
            ["EventBus (ozel)",       "Ajanlar arasi mesajlasma altyapisi"],
            ["pytest",                "Otomatik test (41 test, %100 gecme)"],
            ["loguru",                "Renkli ve dosyaya yazilabilen log sistemi"],
        ],
        genislikler=[55, W - 55]
    )

    pdf.sub("Proje Dizin Yapisi")
    pdf.code(
"""HW_Turtle/
  src/turtle_id/
    agents/        -> 6 ajan (her biri ayri sorumlu)
    core/
      models/      -> Turtle, Embedding, MatchResult (saf veri nesneleri)
      ports/       -> Soyut arayuzler (DIP icin)
      use_cases/   -> Kayit ve dogrulama is akislari
    infrastructure/
      vision/      -> EfficientNet-B0, OpenCV on isleme
      matching/    -> Cosine benzerligi
      persistence/ -> SQLite veritabani
    ui/            -> PySide6 ekranlar
    shared/        -> EventBus, EventType
    container.py   -> Tum bagimliliklar burada bir araya gelir
  tests/           -> 41 otomatik test
  data/            -> Veritabani ve test fotograflari
  run.bat          -> Cift tiklayarak baslat""")

    # ── 3. COKLU AJAN ────────────────────────────────────────────────────
    pdf.add_page()
    pdf.section(3, "Coklu Ajan (Multi-Agent) Mimarisi")

    pdf.body(
        "Sistem, her biri tek bir gorevi olan 6 ajandan olusur. Ajanlar birbirini "
        "dogrudan cagirmaz; mesajlarini EventBus uzerinden yayimlar. Bu yaklasim, "
        "bir ajandaki degisikligin diger ajanlari etkilemesini onler."
    )

    pdf.tablo(
        ["Ajan", "Gorevi"],
        [
            ["ConfigAgent",          "Uygulama ayarlarini (esik, top-k) okur ve yazar"],
            ["PhotoValidationAgent", "Fotografin net, aydinlik ve gecerli formatda oldugunu kontrol eder"],
            ["ImageAgent",           "Fotograftan EfficientNet-B0 ile embedding vektoru uretir"],
            ["MatchingAgent",        "Sorgu vektorunu veritabanindaki vektorlerle karsilastirir"],
            ["DataAgent",            "Kaplumbaga kayit, guncelleme, listeleme islemlerini yapar"],
            ["UIAgent",              "PySide6 ekranlarini yonetir, buton tiklamalarini is akislarina iletir"],
        ],
        genislikler=[45, W - 45]
    )

    pdf.sub("Ajanlar Nasil Haberlesir?")
    pdf.body(
        "Ajanlar arasi iletisim EventBus adli bir yayim/abone sistemiyle saglanir. "
        "Bir ajan islemi bitirdiginde mesaj yayimlar; ilgilenen diger ajanlar bu "
        "mesaji dinler ve geregini yapar. Boylece ajanlar birbirini tanimak zorunda "
        "kalmaz, bu da sistemi daha kolay test edilebilir ve genisletilebilir kilar."
    )

    pdf.code(
"""# Ornek: Esleme tamamlandiginda dogrulama logu otomatik kaydediliyor

class MatchingAgent:
    def match(self, sorgu_vektoru):
        sonuc = self.matcher.esles(...)
        self.yayimla(ESLEME_BULUNDU, sonuc)   # mesaji yayimla

class DataAgent:
    def baslarken(self):
        self.dinle(ESLEME_BULUNDU, self.log_kaydet)   # mesaji dinle

    def log_kaydet(self, sonuc):
        # MatchingAgent'i hic tanimadan logu yazar
        veritabani.kaydet(sonuc)""")

    pdf.sub("Ajan Yasam Dongusu")
    pdf.body(
        "Her ajan BaseAgent adli temel siniftan turetilir. "
        "Bu sinif; baslat, durdur ve saglik kontrol gibi ortak islevleri saglar. "
        "Her ajan kendi ozel gorevini _register_handlers() metodunda tanimlar."
    )

    # ── 4. SOLID ─────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.section(4, "SOLID Prensipleri")

    pdf.body(
        "SOLID, yazilim tasariminda bes temel prensibi ifade eder. "
        "Bu projede her biri bilerek uygulanmistir."
    )

    # SRP
    pdf.sub("S — Tek Sorumluluk (Single Responsibility)")
    pdf.body(
        "Her sinif yalnizca bir isi yapar. Ornegin PhotoValidationAgent "
        "sadece fotografin kalitesini kontrol eder; veritabanina yazmaz, "
        "esleme yapmaz. DataAgent sadece kayit islemleri yapar; goruntu islemez."
    )
    pdf.code(
"""# PhotoValidationAgent — tek gorevi fotografi kontrol etmek:
def validate(self, fotograf_yolu):
    self._dosya_var_mi_kontrol(yol)          # Dosya mevcut mu?
    self._uzanti_kontrolu(yol)               # .jpg, .png vs.
    self._bulaniklik_kontrolu(goruntu)       # Laplacian skoru > 50
    self._parlaklik_kontrolu(goruntu)        # Cok karanlik/acik degil
    return ValidationResult(...)""")

    # OCP
    pdf.sub("O — Acik/Kapali (Open/Closed)")
    pdf.body(
        "Mevcut kodu degistirmeden yeni ozellik eklenebilir. Ornegin "
        "cosine benzerligi yerine FAISS algoritmasi kullanmak istenseydi, "
        "sadece yeni bir sinif yazilip container.py'da tek satirda takilirdi."
    )
    pdf.code(
"""# Mevcut:
eslestirici = CosineMatcher()

# Yeni algoritma eklemek icin sadece su degisir:
eslestirici = FAISSMatcher()    # Diger hic bir kod degismez""")

    # LSP
    pdf.sub("L — Liskov Yerine Gecme (Liskov Substitution)")
    pdf.body(
        "Tum ajanlar BaseAgent sinifini dogru bicimiyle uygular. "
        "Bu sayede ajanlar bir liste icerisinde birbirleri yerine "
        "kullanilabilir ve sistem bunlari ayni sekilde yonetebilir."
    )
    pdf.code(
"""for ajan in [validation_agent, image_agent, matching_agent, data_agent]:
    ajan.baslat()        # Her biri ayni sozlesmeye uyar
    ajan.saglik_kontrol()
    ajan.durdur()""")

    # ISP
    pdf.sub("I — Arayuz Ayirma (Interface Segregation)")
    pdf.body(
        "Her arayuz yalnizca ihtiyac duyulan metodlari icerir. "
        "Ornegin IImagePreprocessor sadece preprocess() metoduna sahiptir. "
        "Hic kullanilmayacak metod tanimlamak zorunda kalinmaz."
    )

    # DIP
    pdf.sub("D — Bagimlilik Tersine Cevrilmesi (Dependency Inversion)")
    pdf.body(
        "Ajanlar somut siniflar yerine soyut arayuzlere bagimlidir. "
        "Bu sayede gercek model yerine test sirasinda sahte bir nesne "
        "enjekte edilebilir; testler hizlanir ve bagimsiz olur."
    )
    pdf.code(
"""# Kotü: Ajan somut sinifi dogrudan olusturuyor
class ImageAgent:
    def __init__(self):
        self.model = TimmEfficientNetExtractor()  # Degistirilmesi zor

# Iyi: Arayuz disaridan enjekte ediliyor (DIP)
class ImageAgent:
    def __init__(self, model: IEmbeddingExtractor):
        self.model = model  # Mock da, gercek model de olabilir""")

    # ── 5. CLEAN CODE ────────────────────────────────────────────────────
    pdf.add_page()
    pdf.section(5, "Clean Code Prensipleri")

    # Anlamli isim
    pdf.sub("Anlamli Isimler")
    pdf.body(
        "Her sinif, metod ve degisken ismi ne yaptigini dogrudan anlatir. "
        "Kisaltma veya belirsiz isimler kullanilmaz."
    )
    pdf.code(
"""# Sinif isimleri ne yaptiklarini anlatir:
PhotoValidationAgent       # Fotograflari dogrular
CosineMatcher              # Cosine benzerligi ile eslestirir
SQLiteTurtleRepository     # SQLite uzerinden kaplumbaga verileri
RegisterTurtleUseCase      # Kaplumbaga kayit is akisi

# Metod isimleri acik ve anlasilidir:
validate(fotograf_yolu)    # Dogrular
find_best_match(vektor)    # En iyi eslemeyi bulur
has_embeddings()           # "Embedding var mi?" sorusunu sorar
is_normalized()            # "Normalize mi?" sorusunu sorar""")

    # Kucuk fonksiyon
    pdf.sub("Kucuk ve Tek Amacli Fonksiyonlar")
    pdf.body(
        "Her fonksiyon tek bir isi yapar. Uzun bir fonksiyon yerine, "
        "her biri kendi isini yapan kucuk fonksiyonlar tercih edilir. "
        "Bu hem okunabilirlik hem de test edilebilirlik acisindan avantajlidir."
    )
    pdf.code(
"""# Kotu: Her seyi yapan buyuk bir fonksiyon
def isle(yol):
    if not os.path.exists(yol): return False
    if yol.split('.')[-1] not in [...]: return False
    img = cv2.imread(yol)
    if img.shape[0] < 100: return False
    # ... 80 satir devam ediyor

# Iyi: Her kontrolun kendi kucuk fonksiyonu var
def validate(self, yol):
    self._dosya_kontrolu(yol, sonuc)
    self._uzanti_kontrolu(yol, sonuc)
    self._boyut_kontrolu(goruntu, sonuc)
    self._bulaniklik_kontrolu(goruntu, sonuc)
    return sonuc""")

    # Hata yonetimi
    pdf.sub("Hatalar Exception Yerine DTO ile Tasinir")
    pdf.body(
        "Is akislari hata durumunda exception firlatmak yerine, "
        "basarili/basarisiz bilgisini icerek bir sonuc nesnesi doner. "
        "Bu, kullanici arayuzunun hataya zarif bir sekilde tepki vermesini saglar."
    )
    pdf.code(
"""def execute(self, istek):
    dogrulama = self.validation_agent.validate(istek.fotograf_yolu)

    if not dogrulama.is_valid:
        return KayitSonucu(
            basarili=False,
            hatalar=dogrulama.hatalar      # Hata mesajlari UI'a tasiniyor
        )

    # ... devam""")

    # EventBus hatasi izole
    pdf.sub("Hata Izolasyonu")
    pdf.body(
        "EventBus'ta bir abonenin hatasi diger aboneleri durdurmaz. "
        "Her abone ayri bir try-except blogunda cagrilir."
    )
    pdf.code(
"""for abone in aboneler:
    try:
        abone(olay_turu, veri)
    except Exception as hata:
        logger.error(f"Abone hatasi: {hata}")
        # Diger aboneler calismaya devam eder""")

    # ── 6. IS AKISLARI ───────────────────────────────────────────────────
    pdf.add_page()
    pdf.section(6, "Temel Is Akislari")

    pdf.sub("Kaplumbaga Kayit Akisi")
    pdf.body(
        "Kullanici arayuzunde fotograf secilip isim girildiginde asagidaki "
        "adimlar arka planda (QThread ile) calisir:"
    )
    pdf.bullet("Fotograf gecerliligi kontrol edilir (net, aydinlik, dogru format)")
    pdf.bullet("Gecerliyse EfficientNet-B0 modeli fotograftan 1280 sayilik bir vektör uretir")
    pdf.bullet("Kaplumbaga bilgileri (isim, tur, vektor) veritabanina kaydedilir")
    pdf.bullet("Kullaniciya basari mesaji gosterilir")
    pdf.ln(2)

    pdf.code(
"""Kullanici 'Kaydet' tiklar
    |
    +--> Fotograf kontrolu         [net mi, boyut uygun mu?]
    |
    +--> EfficientNet-B0           [1280 sayilik parmak izi]
    |
    +--> Veritabanina kaydet       [TurtleORM + EmbeddingORM]
    |
    --> Basari mesaji""")

    pdf.sub("Kaplumbaga Dogrulama Akisi")
    pdf.body(
        "Yeni fotograf yuklendikten sonra sistem, veritabanindaki "
        "tum kayitli kaplumbagalarla karsilastirma yapar:"
    )
    pdf.bullet("Yeni fotograftan embedding vektoru uretilir")
    pdf.bullet("Bu vektor, veritabanindaki tum vektorlerle cosine benzerligi hesaplanir")
    pdf.bullet("En yuksek skoru alan kaplumbaga aday gosterilir")
    pdf.bullet("Skor esigi (0.82) gececekse 'Esleme Bulundu', gecemezse 'Bulunamadi' yazilir")
    pdf.bullet("Her dogrulama otomatik olarak gecmis loguna yazilir")
    pdf.ln(2)

    pdf.code(
"""Kullanici 'Dogrula' tiklar
    |
    +--> Fotograf kontrolu
    |
    +--> Yeni fotograftan vektor uret
    |
    +--> Tum kayitli vektorlerle karsilastir    [cosine similarity]
    |
    +--> En iyi adayi sec
    |
    +--> Skor >= 0.82?
          Evet --> 'Esleme Bulundu — Fotograf: Alpha, Benzerlik: %91'
          Hayir -> 'Esleme Bulunamadi'""")

    pdf.box(
        "Audit Trail (Dogrulama Gecmisi)",
        "Her dogrulama islemi otomatik olarak verification_log tablosuna kaydedilir.\n"
        "Hangi fotograf, kac puanla, hangi kaplumbagayla eslesti bilgisi saklanir.\n"
        "Bu islem tamamen EventBus uzerinden gerceklesir; is akisi bunu bilmez."
    )

    # ── 7. TEST ───────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.section(7, "Test Sonuclari")

    pdf.body(
        "Proje, 41 otomatik testle dogrulanmistir. Testler iki kategoridedir: "
        "birim testleri her sinifi ayri ayri test ederken, entegrasyon testleri "
        "veritabani islemlerini gercek (bellek ici) SQLite uzerinde calistirir."
    )

    pdf.tablo(
        ["Test Dosyasi", "Kapsam", "Test Sayisi"],
        [
            ["test_event_bus.py",        "Pub/sub, thread guvenlik, hata izolasyonu", "7"],
            ["test_matcher.py",          "Cosine esleme, esik mantigi, bos liste",    "7"],
            ["test_models.py",           "Turtle, Embedding, MatchResult nesneleri",  "13"],
            ["test_validation_agent.py", "Fotograf dogrulama ve EventBus entegrasyonu","4"],
            ["test_repository.py",       "Veritabani CRUD, vektor saklama, silme",    "10"],
            ["TOPLAM",                   "",                                           "41 / 41 GECTI"],
        ],
        genislikler=[50, W - 70, 20]
    )

    pdf.sub("Ornek Test")
    pdf.code(
"""# Ayni vektorun kendisiyle eslesmesi 1.0 olmali:
def test_ayni_vektor_eslesmeli(matcher):
    vektor = rastgele_normalize_vektor(128)
    sonuc  = matcher.find_best_match(
        vektor, [Embedding(vector=vektor)], threshold=0.9
    )
    assert sonuc.is_match == True
    assert sonuc.similarity_score == pytest.approx(1.0, abs=1e-5)

# Bos liste eslememeli:
def test_bos_liste_eslememeli(matcher):
    sonuc = matcher.find_best_match(vektor, aday_listesi=[], threshold=0.75)
    assert sonuc.is_match == False""")

    pdf.sub("Gercek Fotograf Uzerinde Pipeline Testi")
    pdf.body(
        "Sentetik fotograflar uzerinde yapilan pipeline testinde:"
    )
    pdf.bullet("Ayni kaplumbaganin karanlik fotografiyla: 0.875 (esleme)")
    pdf.bullet("Ayni kaplumbaganin parlak fotografiyla: 0.962 (esleme)")
    pdf.bullet("Farkli kaplumbagayla karsilastirma: 0.414 (esleme yok)")
    pdf.ln(2)
    pdf.body("Sonuc: Hicbir yanlis pozitif esleme gozlemlenmedi (0 / 10 karsilan karsilastirmada).")

    # ── 8. SONUC ─────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.section(8, "Sonuc ve Degerlendirme")

    pdf.body(
        "Bu projede, kaplumbaga tanima problemini cozecek tam islevli bir masaustu "
        "uygulamasi gelistirilmistir. Proje boyunca yazilim muhendisligi prensipleri "
        "bilerek ve tutarli sekilde uygulanmaya calisilmistir."
    )

    pdf.sub("Kazanimlar")
    pdf.bullet(
        "SOLID prensipleri somut proje ornekleriyle uygulanmistir. "
        "Ornegin adapter degistirmek icin yalnizca container.py'da tek satirlik "
        "degisiklik yeterlidir (OCP)."
    )
    pdf.bullet(
        "Clean Code anlayisiyla her sinif ve metod tek bir isi yapacak sekilde "
        "tasarlanmistir; anlamli isimler, kucuk fonksiyonlar ve hata izolasyonu "
        "ozenle uygulanmistir."
    )
    pdf.bullet(
        "Multi-agent mimarisi, sistemi bagimsiz parcalara ayirarak hem "
        "test edilebilirlik hem de genisletilebilirlik saglamistir."
    )
    pdf.bullet(
        "EventBus mimarisi sayesinde ajanlar birbirini import etmeden haberlesir; "
        "bu da coupling'i en aza indirir."
    )
    pdf.bullet(
        "41 otomatik test yazilmis ve %100 gecme orani saglanmistir. "
        "Testler hizli calisir (4 saniye) cunku veritabani bellekte tutulur."
    )

    pdf.sub("Gozlemler ve Sinirlamalar")
    pdf.bullet(
        "EfficientNet-B0 genel amacli bir modeldir; kaplumbaga ozelinde "
        "egitilmemistir. Gercek fotograflarda esik degerinin 0.60-0.65'e "
        "dusurulmesi daha iyi sonuc verebilir."
    )
    pdf.bullet(
        "Sistem su an tum embeddingleri RAM'e yukleyerek karsilastirma yaptiginden, "
        "cok buyuk veritabanlarinda FAISS gibi hizli yaklasik arama algoritmasi "
        "kullanmak gerekebilir."
    )

    pdf.sub("Proje Buyuklugu")
    pdf.tablo(
        ["Metrik", "Deger"],
        [
            ["Toplam kaynak kodu",  "3.974 satir"],
            ["Test kodu",           "493 satir"],
            ["Ajan sayisi",         "6"],
            ["Veritabani tablosu",  "3 (turtles, embeddings, verification_log)"],
            ["UI sayfasi",          "5"],
            ["Git commit sayisi",   "22"],
            ["Test basari orani",   "%100 (41/41)"],
        ],
        genislikler=[65, W - 65]
    )

    pdf.cizgi()
    pdf.set_font("I", size=9)
    pdf.set_text_color(*GRAY)
    pdf.cell(0, 6, "github.com/YusufAltunbay/HW_Turtle", align="C")


# ═══════════════════════════════════════════════════════════════════════════
def main():
    print("PDF olusturuluyor...")
    pdf = PDF(orientation="P", unit="mm", format="A4")
    pdf.set_margins(MARGIN, 15, MARGIN)
    pdf.set_auto_page_break(auto=True, margin=16)
    pdf.setup()
    rapor_olustur(pdf)
    pdf.output(OUT)
    boyut = os.path.getsize(OUT) // 1024
    print(f"[TAMAM] {OUT}  ({boyut} KB, {pdf.page} sayfa)")


if __name__ == "__main__":
    main()
