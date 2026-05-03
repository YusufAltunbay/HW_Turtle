from fpdf import FPDF
from fpdf.enums import XPos, YPos
import os

OUT    = "RAPOR_TurtleID.pdf"
MARGIN = 25
W      = 210 - 2 * MARGIN
FONTS  = "C:/Windows/Fonts/"

class PDF(FPDF):
    def setup(self):
        self.add_font("R", fname=FONTS + "arial.ttf")
        self.add_font("B", fname=FONTS + "arialbd.ttf")
        self.add_font("I", fname=FONTS + "ariali.ttf")
        self.add_font("M", fname=FONTS + "consola.ttf")

    def footer(self):
        self.set_y(-12)
        self.set_font("I", size=8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 5, f"Sayfa {self.page_no()}", align="C")

    def baslik(self, txt):
        self.ln(5)
        self.set_font("B", size=12)
        self.set_text_color(30, 30, 30)
        self.cell(W, 7, txt, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_draw_color(100, 100, 100)
        self.set_line_width(0.4)
        self.line(MARGIN, self.get_y(), MARGIN + W, self.get_y())
        self.ln(3)

    def yazi(self, txt):
        self.set_font("R", size=10.5)
        self.set_text_color(30, 30, 30)
        self.multi_cell(W, 6, txt, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(1)

    def madde(self, txt):
        self.set_font("R", size=10.5)
        self.set_text_color(30, 30, 30)
        self.set_x(MARGIN + 4)
        self.cell(5, 6, "-")
        self.multi_cell(W - 9, 6, txt, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def kod(self, txt):
        self.ln(1)
        lines = txt.strip().split("\n")
        h = len(lines) * 5 + 6
        if self.get_y() + h > 272:
            self.add_page()
        y0 = self.get_y()
        self.set_fill_color(245, 245, 245)
        self.set_draw_color(200, 200, 200)
        self.set_line_width(0.2)
        self.rect(MARGIN, y0, W, h, style="FD")
        self.set_y(y0 + 3)
        self.set_font("M", size=8.5)
        self.set_text_color(40, 40, 40)
        for line in lines:
            self.set_x(MARGIN + 4)
            self.cell(W - 4, 5, line, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(3)
        self.set_text_color(30, 30, 30)

    def tablo(self, basliklar, satirlar, genislikler=None):
        n = len(basliklar)
        if not genislikler:
            genislikler = [W / n] * n
        rh = 6.5
        self.set_font("B", size=9.5)
        self.set_fill_color(220, 220, 220)
        self.set_text_color(30, 30, 30)
        self.set_draw_color(180, 180, 180)
        self.set_line_width(0.2)
        for h, g in zip(basliklar, genislikler):
            self.cell(g, rh, "  " + h, border=1, fill=True)
        self.ln()
        self.set_font("R", size=9.5)
        self.set_fill_color(250, 250, 250)
        for i, satir in enumerate(satirlar):
            fill = (i % 2 == 0)
            for hucre, g in zip(satir, genislikler):
                x0, y0 = self.get_x(), self.get_y()
                self.multi_cell(g, rh, "  " + str(hucre), border=1, fill=fill,
                                new_x=XPos.RIGHT, new_y=YPos.TOP)
                self.set_xy(x0 + g, y0)
            self.ln(rh)
        self.ln(3)


def olustur(pdf: PDF):

    # ── KAPAK ──
    pdf.add_page()

    pdf.set_y(60)
    pdf.set_font("B", size=20)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 12, "Turtle ID", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_font("R", size=12)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 8, "Kaplumbaga Fotograf Tanim Sistemi", align="C",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.ln(10)
    pdf.set_font("R", size=11)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 7, "Yusuf Altunbay - 22253072", align="C",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.ln(20)
    pdf.set_draw_color(180, 180, 180)
    pdf.set_line_width(0.3)
    pdf.line(MARGIN + 20, pdf.get_y(), 210 - MARGIN - 20, pdf.get_y())

    pdf.ln(10)
    pdf.set_font("I", size=10)
    pdf.set_text_color(100, 100, 100)
    icindekiler = [
        "1. Projenin Amaci",
        "2. Coklu Ajan Mimarisi",
        "3. SOLID Prensipleri",
        "4. Clean Code",
        "5. Testler",
    ]
    for m in icindekiler:
        pdf.cell(0, 7, m, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # ── 1. AMAC ──
    pdf.add_page()
    pdf.baslik("1. Projenin Amaci")
    pdf.yazi(
        "Bu proje, kaplumbagalari fotograftan taniyan bir masaustu uygulamasidir. "
        "Farkli zamanlarda, farkli isik kosullarinda cekilen iki fotografin ayni "
        "kaplumbagaya ait olup olmadigini benzerlik skoru uzerinden tespit eder."
    )
    pdf.yazi(
        "EfficientNet-B0 modeli her fotograftan 1280 sayilik bir parmak izi "
        "(embedding vektoru) cikarir. Iki vektorun cosine benzerligi 0.82 esigini "
        "gecerse esleme basarili sayilir."
    )

    pdf.baslik("Kullanilan Teknolojiler")
    pdf.tablo(
        ["Teknoloji", "Kullanim Amaci"],
        [
            ["Python 3.11",          "Ana programlama dili"],
            ["PySide6",              "Masaustu kullanici arayuzu"],
            ["EfficientNet-B0",      "Fotograftan ozellik vektoru cikarma"],
            ["OpenCV",               "Goruntu on isleme"],
            ["SQLite / SQLAlchemy",  "Veri saklama"],
            ["pytest",               "Otomatik testler (41 test)"],
        ],
        genislikler=[50, W - 50]
    )

    # ── 2. MULTI-AGENT ──
    pdf.add_page()
    pdf.baslik("2. Coklu Ajan Mimarisi")
    pdf.yazi(
        "Sistem 6 ajandan olusur. Her ajan tek bir isi yapar ve "
        "EventBus araciligiyla diger ajanlarla haberlesir. "
        "Ajanlar birbirini dogrudan cagirmaz, bu da kodu bagimsiz ve test edilebilir kilar."
    )

    pdf.tablo(
        ["Ajan", "Gorevi"],
        [
            ["ConfigAgent",          "Ayarlari (esik degeri, top-k) okur ve yazar"],
            ["PhotoValidationAgent", "Fotografin net ve gecerli oldugunu kontrol eder"],
            ["ImageAgent",           "Fotograftan embedding vektoru uretir"],
            ["MatchingAgent",        "Sorgu vektorunu veritabaniyla karsilastirir"],
            ["DataAgent",            "Kaplumbaga kayit ve listeleme islemleri"],
            ["UIAgent",              "Ekranlari yonetir, butonlari is akislarina baglar"],
        ],
        genislikler=[48, W - 48]
    )

    pdf.baslik("EventBus Ornegi")
    pdf.yazi(
        "Ajanlar birbirine mesaj gonderir. Asagida esleme tamamlandiginda "
        "dogrulama logunun otomatik olarak kaydedilmesi gosterilmistir:"
    )
    pdf.kod(
"""# MatchingAgent eslemeyi tamamlayinca mesaj yayimlar:
self.event_bus.publish(ESLEME_BULUNDU, sonuc)

# DataAgent bu mesaji dinler, kendisi otomatik log kaydeder:
class DataAgent:
    def baslarken(self):
        self.event_bus.subscribe(ESLEME_BULUNDU, self.log_kaydet)

    def log_kaydet(self, sonuc):
        veritabani.dogrulama_logu_kaydet(sonuc)""")

    # ── 3. SOLID ──
    pdf.add_page()
    pdf.baslik("3. SOLID Prensipleri")

    pdf.set_font("B", size=10.5)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(W, 6, "S — Tek Sorumluluk (Single Responsibility)",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(1)
    pdf.yazi(
        "Her sinif tek bir isi yapar. PhotoValidationAgent sadece fotograf "
        "kontrolu yapar; veritabanina yazmaz, esleme yapmaz."
    )
    pdf.kod(
"""class PhotoValidationAgent:
    def validate(self, fotograf_yolu):
        self._dosya_var_mi(yol)
        self._uzanti_uygun_mu(yol)
        self._bulanik_mi(goruntu)
        self._karanlık_mi(goruntu)
        return ValidationResult(...)""")

    pdf.set_font("B", size=10.5)
    pdf.cell(W, 6, "O — Acik/Kapali (Open/Closed)",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(1)
    pdf.yazi(
        "Yeni ozellik eklemek icin mevcut kodu degistirmek gerekmez. "
        "Ornegin farkli bir esleme algoritmasi kullanmak istersek "
        "sadece container.py'da tek satir degisir."
    )
    pdf.kod(
"""# Mevcut:  eslestirici = CosineMatcher()
# Yeni algoritma icin:
eslestirici = FAISSMatcher()   # Baska hicbir dosya degismez""")

    pdf.set_font("B", size=10.5)
    pdf.cell(W, 6, "D — Bagimlilik Tersine Cevrilmesi (Dependency Inversion)",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(1)
    pdf.yazi(
        "Ajanlar somut siniflar yerine soyut arayuzlere bagimlidir. "
        "Bu sayede testlerde gercek model yerine sahte bir nesne kullanilabilir."
    )
    pdf.kod(
"""# Kotu: ajan somut sinifi olusturuyor
class ImageAgent:
    def __init__(self):
        self.model = TimmEfficientNetExtractor()

# Iyi: arayuz disaridan enjekte ediliyor
class ImageAgent:
    def __init__(self, model: IEmbeddingExtractor):
        self.model = model""")

    # ── 4. CLEAN CODE ──
    pdf.add_page()
    pdf.baslik("4. Clean Code")

    pdf.set_font("B", size=10.5)
    pdf.cell(W, 6, "Anlamli Isimler", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(1)
    pdf.yazi("Her sinif ve metod ismi ne yaptigini dogrudan anlatir.")
    pdf.kod(
"""PhotoValidationAgent   # Fotograflari dogrular
CosineMatcher          # Cosine benzerligi ile eslestirir
find_best_match()      # En iyi eslemeyi bulur
has_embeddings()       # "Embedding var mi?" sorusunu sorar""")

    pdf.set_font("B", size=10.5)
    pdf.cell(W, 6, "Kucuk Fonksiyonlar", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(1)
    pdf.yazi(
        "Uzun bir fonksiyon yerine, her biri tek isi yapan kucuk fonksiyonlar tercih edilir."
    )
    pdf.kod(
"""# Kotu: her seyi yapan tek buyuk fonksiyon
def isle(yol):
    # 80 satir ...

# Iyi: her kontrolun kendi fonksiyonu var
def validate(self, yol):
    self._dosya_var_mi(yol, sonuc)
    self._uzanti_kontrol(yol, sonuc)
    self._bulaniklik_kontrol(goruntu, sonuc)
    return sonuc""")

    pdf.set_font("B", size=10.5)
    pdf.cell(W, 6, "Hata Yonetimi", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(1)
    pdf.yazi(
        "Hatalar exception firlatmak yerine sonuc nesnesiyle kullaniciya iletilir. "
        "EventBus'ta bir abonenin hatasi diger aboneleri durdurmaz."
    )
    pdf.kod(
"""if not dogrulama.gecerli:
    return KayitSonucu(basarili=False, hatalar=dogrulama.hatalar)

# EventBus'ta hata izolasyonu:
for abone in aboneler:
    try:
        abone(olay, veri)
    except Exception as hata:
        logger.error(hata)   # Diger aboneler calismaya devam eder""")

    # ── 5. TEST ──
    pdf.add_page()
    pdf.baslik("5. Testler")
    pdf.yazi("Proje 41 otomatik testle dogrulanmistir, tamami gecmektedir.")

    pdf.tablo(
        ["Test Dosyasi", "Kapsam", "Adet"],
        [
            ["test_event_bus.py",        "Pub/sub, thread guvenligi",     "7"],
            ["test_matcher.py",          "Cosine esleme, esik mantigi",   "7"],
            ["test_models.py",           "Veri modelleri",                "13"],
            ["test_validation_agent.py", "Fotograf dogrulama",            "4"],
            ["test_repository.py",       "Veritabani CRUD",               "10"],
            ["Toplam",                   "",                              "41"],
        ],
        genislikler=[55, W - 75, 20]
    )

    pdf.yazi("Ornek test:")
    pdf.kod(
"""def test_ayni_vektor_eslesmeli(matcher):
    v = normalize(random_vector(128))
    sonuc = matcher.find_best_match(v, [Embedding(vector=v)], threshold=0.9)
    assert sonuc.is_match == True
    assert sonuc.score == pytest.approx(1.0)

def test_bos_liste_eslememeli(matcher):
    sonuc = matcher.find_best_match(v, [], threshold=0.75)
    assert sonuc.is_match == False""")

    pdf.baslik("Pipeline Testi Sonuclari")
    pdf.yazi("Sentetik fotograflar uzerinde yapilan testte:")
    pdf.madde("Ayni kaplumbaga (karanlik fotograf): benzerlik 0.875 — esleme basarili")
    pdf.madde("Ayni kaplumbaga (parlak fotograf):   benzerlik 0.962 — esleme basarili")
    pdf.madde("Farkli kaplumbaga:                   benzerlik 0.414 — esleme yok")
    pdf.ln(3)
    pdf.yazi("Yanlis pozitif esleme: 0 / 10 karsilastirma")


def main():
    pdf = PDF(orientation="P", unit="mm", format="A4")
    pdf.set_margins(MARGIN, 18, MARGIN)
    pdf.set_auto_page_break(auto=True, margin=16)
    pdf.setup()
    olustur(pdf)
    pdf.output(OUT)
    print(f"Olusturuldu: {OUT}  ({os.path.getsize(OUT)//1024} KB, {pdf.page} sayfa)")

if __name__ == "__main__":
    main()
