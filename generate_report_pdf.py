"""
Turtle ID — Teknik Rapor PDF Uretici
Calistirmak icin: python generate_report_pdf.py
"""
from __future__ import annotations
from fpdf import FPDF
from fpdf.enums import XPos, YPos
import os

OUT = "RAPOR_TurtleID.pdf"

# ─── Renkler ────────────────────────────────────────────────────────────────
C_TITLE      = (15,  55, 100)   # koyu lacivert  — baslik
C_H1         = (15,  55, 100)   # lacivert       — bolum basligi
C_H2         = (30,  90, 160)   # orta mavi      — alt baslik
C_H3         = (60, 130, 190)   # acik mavi      — madde basligi
C_CODE_BG    = (245, 247, 250)  # cok acik gri   — kod arka plani
C_CODE_FG    = ( 40,  60,  80)  # koyu lacivert  — kod metni
C_TABLE_HEAD = ( 30,  80, 150)  # mavi           — tablo baslik
C_TABLE_ALT  = (235, 242, 252)  # cok acik mavi  — tablo satirlari
C_ACCENT     = (  0, 130, 100)  # yesil          — vurgu kutulari
C_ACCENT_BG  = (235, 252, 245)  # acik yesil     — vurgu arka plani
C_BODY       = ( 30,  30,  30)  # koyu gri       — normal metin
C_SUBTLE     = (110, 120, 130)  # acik gri       — ikincil metin
C_BORDER     = (200, 210, 225)  # cok acik       — cizgi/kenar

W_PAGE  = 210
MARGIN  = 18
W_TEXT  = W_PAGE - 2 * MARGIN


class PDF(FPDF):
    """Ozel PDF sinifi: sayfa numarasi, altbilgi, font yonetimi."""

    # ------------------------------------------------------------------ #
    #  Font Yukleme                                                        #
    # ------------------------------------------------------------------ #
    def setup_fonts(self):
        """Windows sistem fontlari — Arial (sans) + Consolas (mono), Turkce tam destek."""
        win_fonts = "C:/Windows/Fonts/"
        font_map = {
            "DejaVu":      win_fonts + "arial.ttf",
            "DejaVuB":     win_fonts + "arialbd.ttf",
            "DejaVuI":     win_fonts + "ariali.ttf",
            "DejaVuBI":    win_fonts + "arialbi.ttf",
            "DejaVuMono":  win_fonts + "consola.ttf",
            "DejaVuMonoB": win_fonts + "consolab.ttf",
        }
        for alias, fpath in font_map.items():
            self.add_font(alias, fname=fpath)

    # ------------------------------------------------------------------ #
    #  Uygulama Font Kestirmeleri                                          #
    # ------------------------------------------------------------------ #
    def _body(self, size=10):
        self.set_font("DejaVu", size=size)
        self.set_text_color(*C_BODY)

    def _bold(self, size=10):
        self.set_font("DejaVuB", size=size)
        self.set_text_color(*C_BODY)

    def _italic(self, size=10):
        self.set_font("DejaVuI", size=size)
        self.set_text_color(*C_SUBTLE)

    def _mono(self, size=9):
        self.set_font("DejaVuMono", size=size)
        self.set_text_color(*C_CODE_FG)

    def _mono_bold(self, size=9):
        self.set_font("DejaVuMonoB", size=size)
        self.set_text_color(*C_CODE_FG)

    # ------------------------------------------------------------------ #
    #  Sayfa Ustu / Alti                                                   #
    # ------------------------------------------------------------------ #
    def header(self):
        if self.page_no() == 1:
            return
        self.set_y(8)
        self.set_draw_color(*C_BORDER)
        self.set_line_width(0.3)
        self._italic(8)
        self.set_text_color(*C_SUBTLE)
        self.cell(0, 6, "Turtle ID — Clean Code · SOLID · Multi-Agent Mimari Raporu",
                  align="L", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.line(MARGIN, self.get_y(), W_PAGE - MARGIN, self.get_y())
        self.ln(3)

    def footer(self):
        self.set_y(-14)
        self.set_draw_color(*C_BORDER)
        self.line(MARGIN, self.get_y(), W_PAGE - MARGIN, self.get_y())
        self.ln(1)
        self._italic(8)
        self.set_text_color(*C_SUBTLE)
        self.cell(0, 6,
                  f"github.com/YusufAltunbay/HW_Turtle      Sayfa {self.page_no()}",
                  align="C")

    # ------------------------------------------------------------------ #
    #  Bolum Baslik Yardimcilari                                           #
    # ------------------------------------------------------------------ #
    def h1(self, text: str):
        """Buyuk bolum basligi — numarali, tam genislik renkli bar."""
        self.ln(4)
        self.set_fill_color(*C_H1)
        self.set_text_color(255, 255, 255)
        self.set_font("DejaVuB", size=13)
        self.cell(W_TEXT, 9, "  " + text, fill=True,
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(3)
        self._body()

    def h2(self, text: str):
        """Alt bolum basligi — mavi alt cizgi."""
        self.ln(3)
        self.set_text_color(*C_H2)
        self.set_font("DejaVuB", size=11)
        self.cell(W_TEXT, 7, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_draw_color(*C_H2)
        self.set_line_width(0.5)
        self.line(MARGIN, self.get_y(), MARGIN + W_TEXT * 0.45, self.get_y())
        self.ln(3)
        self._body()

    def h3(self, text: str):
        """Madde basligi."""
        self.ln(2)
        self.set_text_color(*C_H3)
        self.set_font("DejaVuB", size=10)
        self.cell(W_TEXT, 6, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(1)
        self._body()

    # ------------------------------------------------------------------ #
    #  Icerik Yardimcilari                                                 #
    # ------------------------------------------------------------------ #
    def para(self, text: str, indent: float = 0):
        """Normal paragraf."""
        self._body(10)
        self.set_x(MARGIN + indent)
        self.multi_cell(W_TEXT - indent, 5.5, text,
                        new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(1)

    def bullet(self, text: str, indent: float = 4):
        """Madde isareti ile satir."""
        self._body(10)
        bx = MARGIN + indent
        self.set_x(bx)
        self.set_text_color(*C_H2)
        self.cell(5, 5.5, chr(0x2022))   # •
        self.set_text_color(*C_BODY)
        self.multi_cell(W_TEXT - indent - 5, 5.5, text,
                        new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def sub_bullet(self, text: str):
        """Alt madde."""
        bx = MARGIN + 10
        self.set_x(bx)
        self.set_text_color(*C_SUBTLE)
        self.set_font("DejaVuMono", size=8)
        self.cell(5, 5, "→")
        self._body(9)
        self.set_text_color(*C_BODY)
        self.multi_cell(W_TEXT - 15, 5, text,
                        new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def code_block(self, code: str, title: str = ""):
        """Kod blogu — gri arka plan, monospace font."""
        self.ln(1)
        if title:
            self._italic(8)
            self.set_text_color(*C_SUBTLE)
            self.cell(W_TEXT, 5, "  " + title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        lines = code.strip().split("\n")
        line_h = 4.8
        total_h = len(lines) * line_h + 6
        # Sayfa tasmasini onle
        if self.get_y() + total_h > 270:
            self.add_page()

        # Arka plan kutusu
        self.set_fill_color(*C_CODE_BG)
        self.set_draw_color(*C_BORDER)
        self.set_line_width(0.2)
        bx = MARGIN
        by = self.get_y()
        self.rect(bx, by, W_TEXT, total_h, style="FD")

        # Sol kenara ince renkli bar
        self.set_fill_color(*C_H2)
        self.rect(bx, by, 2, total_h, style="F")

        self.set_y(by + 3)
        self._mono(8.5)
        for line in lines:
            self.set_x(MARGIN + 5)
            self.cell(W_TEXT - 5, line_h, line,
                      new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        self.ln(3)
        self._body()

    def accent_box(self, title: str, text: str):
        """Vurgu kutusu — yesil kenar."""
        self.ln(1)
        lines = text.strip().split("\n")
        line_h = 5.2
        title_h = 6
        total_h = title_h + len(lines) * line_h + 6

        if self.get_y() + total_h > 270:
            self.add_page()

        bx = MARGIN
        by = self.get_y()
        self.set_fill_color(*C_ACCENT_BG)
        self.set_draw_color(*C_ACCENT)
        self.set_line_width(0.2)
        self.rect(bx, by, W_TEXT, total_h, style="FD")
        self.set_fill_color(*C_ACCENT)
        self.rect(bx, by, 3, total_h, style="F")

        # Baslik
        self.set_xy(bx + 6, by + 2)
        self.set_font("DejaVuB", size=9)
        self.set_text_color(*C_ACCENT)
        self.cell(W_TEXT - 10, title_h, title,
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        # Icerik
        self._body(9.5)
        for line in lines:
            self.set_x(bx + 6)
            self.multi_cell(W_TEXT - 10, line_h, line,
                            new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        self.ln(3)
        self._body()

    def table(self, headers: list[str], rows: list[list[str]],
              col_widths: list[float] | None = None):
        """Stil tablo — baslik satiri + alternatif satir rengi."""
        n = len(headers)
        if col_widths is None:
            col_widths = [W_TEXT / n] * n

        row_h = 6.5

        # Baslik
        self.set_fill_color(*C_TABLE_HEAD)
        self.set_text_color(255, 255, 255)
        self.set_font("DejaVuB", size=9)
        self.set_draw_color(*C_BORDER)
        self.set_line_width(0.2)
        for i, (h, w) in enumerate(zip(headers, col_widths)):
            self.cell(w, row_h, "  " + h, border=1, fill=True)
        self.ln()

        # Satirlar
        for ri, row in enumerate(rows):
            if self.get_y() + row_h > 272:
                self.add_page()
                # Basliği tekrar ciz
                self.set_fill_color(*C_TABLE_HEAD)
                self.set_text_color(255, 255, 255)
                self.set_font("DejaVuB", size=9)
                for h, w in zip(headers, col_widths):
                    self.cell(w, row_h, "  " + h, border=1, fill=True)
                self.ln()

            fill = ri % 2 == 1
            self.set_fill_color(*C_TABLE_ALT)
            self.set_text_color(*C_BODY)
            self._body(9)
            for cell_text, w in zip(row, col_widths):
                # Uzun metin: multi_cell ile sar
                x0 = self.get_x()
                y0 = self.get_y()
                self.multi_cell(w, row_h, "  " + str(cell_text),
                                border=1, fill=fill,
                                new_x=XPos.RIGHT, new_y=YPos.TOP)
                self.set_xy(x0 + w, y0)
            self.ln(row_h)

        self.ln(3)
        self._body()

    def divider(self):
        self.ln(2)
        self.set_draw_color(*C_BORDER)
        self.set_line_width(0.3)
        self.line(MARGIN, self.get_y(), W_PAGE - MARGIN, self.get_y())
        self.ln(3)


# ═══════════════════════════════════════════════════════════════════════════
#  RAPOR ICERIGI
# ═══════════════════════════════════════════════════════════════════════════

def build_report(pdf: PDF):

    # ──────────────────────────────────────────────────────────────────────
    #  KAPAK SAYFASI
    # ──────────────────────────────────────────────────────────────────────
    pdf.add_page()

    # Arka plan blogu
    pdf.set_fill_color(*C_H1)
    pdf.rect(0, 0, W_PAGE, 80, style="F")

    pdf.set_y(18)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("DejaVuB", size=26)
    pdf.cell(0, 14, "Turtle ID", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_font("DejaVuB", size=14)
    pdf.cell(0, 8, "Kaplumbaga Fotograf Tanim Sistemi",
             align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_font("DejaVu", size=10)
    pdf.set_text_color(180, 210, 240)
    pdf.cell(0, 6, "Clean Code  ·  SOLID  ·  Multi-Agent Mimari  ·  Teknik Rapor",
             align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_y(88)
    pdf.set_text_color(*C_BODY)

    # Ozet bilgi kutusu
    pdf.set_fill_color(*C_TABLE_ALT)
    pdf.set_draw_color(*C_BORDER)
    pdf.rect(MARGIN, 88, W_TEXT, 52, style="FD")
    pdf.set_y(94)

    info_rows = [
        ("Proje",       "HW_Turtle — Kaplumbaga Re-Identification Sistemi"),
        ("Dil",         "Python 3.11+"),
        ("Mimari",      "Multi-Agent + Hexagonal (Port/Adapter)"),
        ("Arayuz",      "PySide6 (Qt 6)"),
        ("Veritabani",  "SQLite + SQLAlchemy 2.0 (WAL modu)"),
        ("Model",       "EfficientNet-B0 (timm) — 1280 boyutlu embedding"),
        ("Esleme",      "Cosine Similarity (scikit-learn)"),
        ("GitHub",      "github.com/YusufAltunbay/HW_Turtle"),
    ]
    for label, value in info_rows:
        pdf.set_x(MARGIN + 6)
        pdf.set_font("DejaVuB", size=9.5)
        pdf.set_text_color(*C_H2)
        pdf.cell(38, 5.5, label + ":")
        pdf.set_font("DejaVu", size=9.5)
        pdf.set_text_color(*C_BODY)
        pdf.cell(W_TEXT - 44, 5.5, value, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_y(148)
    pdf._body()

    # Istatistik satirlari
    stats = [
        ("3.974",  "satir kaynak kodu"),
        ("6",      "ajan"),
        ("4",      "port arayuzu"),
        ("41",     "test — %100 gecme"),
        ("21",     "git commit"),
    ]
    box_w = W_TEXT / len(stats)
    bx = MARGIN
    by = 150

    pdf.set_draw_color(*C_BORDER)
    for num, label in stats:
        pdf.set_fill_color(*C_H1)
        pdf.rect(bx, by, box_w - 2, 20, style="F")
        pdf.set_xy(bx, by + 2)
        pdf.set_font("DejaVuB", size=16)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(box_w - 2, 10, num, align="C",
                 new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.set_xy(bx, by + 11)
        pdf.set_font("DejaVu", size=7.5)
        pdf.set_text_color(180, 210, 240)
        pdf.cell(box_w - 2, 6, label, align="C")
        bx += box_w

    # ICERIK TABLOSU
    pdf.set_y(185)
    pdf.set_fill_color(*C_TABLE_HEAD)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("DejaVuB", size=11)
    pdf.cell(W_TEXT, 8, "  ICERIK", fill=True,
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    toc = [
        ("1", "Proje Ozeti ve Mimari Genel Bakis"),
        ("2", "SOLID Prensipleri — Somut Kod Ornekleri"),
        ("3", "Clean Code Prensipleri"),
        ("4", "Multi-Agent Mimarisi"),
        ("5", "EventBus Mekanizmasi"),
        ("6", "Port / Adapter (Hexagonal) Mimarisi"),
        ("7", "Is Akislari (Kayit & Dogrulama)"),
        ("8", "Test Yapisi"),
        ("9", "Kod Istatistikleri ve Ozet"),
    ]
    pdf._body(10)
    for num, title in toc:
        pdf.set_x(MARGIN)
        pdf.set_font("DejaVuB", size=10)
        pdf.set_text_color(*C_H2)
        pdf.cell(10, 6.5, num + ".")
        pdf.set_font("DejaVu", size=10)
        pdf.set_text_color(*C_BODY)
        pdf.cell(W_TEXT - 10, 6.5, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # ──────────────────────────────────────────────────────────────────────
    #  1. PROJE OZETI
    # ──────────────────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.h1("1. Proje Ozeti ve Mimari Genel Bakis")

    pdf.para(
        "Turtle ID, farkli zamanlarda ve kosullarda cekilen kaplumbaga "
        "fotograflarindan ayni bireyi taniyan gorsel esleme sistemidir. "
        "EfficientNet-B0 sinir agi her fotograftan 1280 boyutlu L2-normalize "
        "bir ozellik vektoru cikarir; cosine benzerligi ile sorgu vektoru "
        "veritabanindaki tum vektorlerle karsilastirilarak en iyi eslesme bulunur."
    )

    pdf.h2("Teknoloji Yigini")
    pdf.table(
        ["Katman", "Teknoloji", "Gorevin Ozeti"],
        [
            ["Goruntu ozelligi", "EfficientNet-B0 (timm)", "1280-dim L2-normalize vektor"],
            ["On isleme", "OpenCV", "Letterbox + CLAHE + ImageNet normalize"],
            ["Esleme", "Cosine Similarity (sklearn)", "Matris carpimiyla toplu karsilastirma"],
            ["Veritabani", "SQLite + SQLAlchemy 2.0", "WAL modu, soft delete, BLOB vektor"],
            ["Kullanici arayuzu", "PySide6 (Qt 6)", "QThread worker'lar, Signal/Slot"],
            ["Ajan iletisimi", "Thread-safe EventBus", "Pub/sub, hata izolasyonu"],
            ["DI", "Manuel AppContainer", "Tum bagimliliklar tek noktada"],
        ],
        col_widths=[38, 48, W_TEXT - 86]
    )

    pdf.h2("Klasor Yapisi")
    pdf.code_block(
"""src/turtle_id/
  agents/           7 ajan (BaseAgent'tan turetilmis)
  core/
    models/         4 domain modeli (Turtle, Embedding, MatchResult)
    ports/          4 soyut arayuz (ITurtleRepository, IMatcher, ...)
    use_cases/      2 is akisi (Register, Verify)
  infrastructure/
    persistence/    SQLite + SQLAlchemy ORM
    vision/         EfficientNet-B0, OpenCV on isleme
    matching/       Cosine Similarity matcher
  ui/
    views/          5 gorsel sayfa
    widgets/        2 ozel widget
  shared/           EventBus + EventType enum (13 olay)
  app.py            Giris noktasi
  container.py      Bagimlilik enjeksiyon konteyneri""",
        title="Proje dizin agaci"
    )

    pdf.h2("Katmanli Mimari Diyagram")
    pdf.code_block(
"""UI KATMANI
  PySide6 MainWindow  ->  RegisterView / VerifyView
  QThread Workers     ->  RegisterWorker / VerifyWorker
         |
         | cagri (use case)
         v
USE CASE KATMANI
  RegisterTurtleUseCase    VerifyTurtleUseCase
  (frozen dataclass DTO'lar ile tip guvenligi)
         |
         | ajan cagrisi
         v
AJAN KATMANI
  PhotoValidationAgent  ImageAgent  MatchingAgent
  DataAgent             ConfigAgent
  ─────────── EventBus (pub/sub) ───────────
         |
         | port arayuzu (DIP)
         v
ALTYAPI KATMANI (Adapters)
  OpenCVPreprocessor        TimmEfficientNetExtractor
  CosineMatcher             SQLiteTurtleRepository""",
        title="Mimari katmanlari"
    )

    # ──────────────────────────────────────────────────────────────────────
    #  2. SOLID
    # ──────────────────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.h1("2. SOLID Prensipleri — Somut Kod Ornekleri")

    # SRP
    pdf.h2("2.1  SRP — Single Responsibility Principle")
    pdf.para(
        "Her sinif ve ajan yalnizca bir nedenden degisir. "
        "PhotoValidationAgent sadece fotograf kalitesini kontrol eder; "
        "embedding uretmez, veritabanina yazmaz, esleme yapmaz."
    )
    pdf.table(
        ["Sinif / Ajan", "Tek Sorumlulugu", "Yapmadigi"],
        [
            ["EventBus",               "Pub/sub mekanizmasi",           "Is mantigi, veri erisimi"],
            ["ConfigAgent",            "Ayar okuma / yazma",            "Esleme, embedding"],
            ["PhotoValidationAgent",   "Fotograf kalitesi kontrolu",    "Kayit, esleme"],
            ["ImageAgent",             "Embedding vektoru uretimi",     "Veritabani, esleme"],
            ["MatchingAgent",          "Cosine esleme",                 "Veri kaydetme, UI"],
            ["DataAgent",              "CRUD islemleri",                "Goruntu isleme"],
            ["OpenCVPreprocessor",     "Fotograf on isleme",            "Feature extraction"],
            ["TimmEfficientNetExtractor","Feature extraction",          "On isleme, esleme"],
            ["CosineMatcher",          "Benzerlik hesabi",              "Vektor cikartma"],
            ["SQLiteTurtleRepository", "SQLite erisimi",                "Is mantigi"],
            ["RegisterTurtleUseCase",  "Kayit akisi orkestrasyonu",     "Veri erisimi"],
            ["VerifyTurtleUseCase",    "Dogrulama akisi",               "Kayit, depolama"],
        ],
        col_widths=[52, 60, W_TEXT - 112]
    )

    pdf.h3("Somut Ornek — PhotoValidationAgent")
    pdf.code_block(
"""class PhotoValidationAgent(BaseAgent):
    # 7 kucuk, tek amacli metod:
    def _check_file_exists(self, path, result):    # ~10 satir
        ...
    def _check_extension(self, path, result):      # ~8 satir
        ...
    def _check_blur(self, img, result):            # Laplacian variance > 50
        ...
    def _check_brightness(self, img, result):      # 20 < ort. < 240
        ...

    # Ana metod sadece orkestre eder — is mantigi YOKTUR:
    def validate(self, image_path) -> ValidationResult:
        result = ValidationResult(is_valid=True)
        self._check_file_exists(path, result)
        self._check_extension(path, result)
        self._check_blur(img, result)
        self._check_brightness(img, result)
        return result""",
        title="SRP: PhotoValidationAgent — her metod tek is yapar"
    )

    # OCP
    pdf.h2("2.2  OCP — Open / Closed Principle")
    pdf.para(
        "Mevcut kod degistirilmeden genisletilebilir. Port arayuzleri "
        "sayesinde yeni bir esleme algoritmasi veya veritabani eklemek "
        "icin yalnizca container.py'da 1-2 satir degismesi yeterlidir."
    )
    pdf.code_block(
"""# Mevcut adapter:
class CosineMatcher(IMatcher):
    def find_best_match(self, query, candidates, threshold, top_k):
        scores = cosine_similarity([query], matrix)[0]
        ...

# Yeni adapter (MEVCUT KOD DEGISMEZ):
class FAISSMatcher(IMatcher):
    def find_best_match(self, query, candidates, threshold, top_k):
        # Milyonlarca embedding icin GPU hizli FAISS
        ...

# container.py'da TEK SATIR:
matcher = FAISSMatcher()   # onceki: CosineMatcher()""",
        title="OCP: Yeni esleme algoritmasi — tek satirlik degisiklik"
    )

    pdf.h3("Degistirilebilir Adapter'lar")
    pdf.table(
        ["Port (Soyut)", "Mevcut Adapter", "Alternatif Adapter"],
        [
            ["ITurtleRepository",  "SQLiteTurtleRepository",        "PostgreSQLRepository"],
            ["IImagePreprocessor", "OpenCVPreprocessor",             "PytorchPreprocessor"],
            ["IEmbeddingExtractor","TimmEfficientNetExtractor",      "ResNet50Extractor"],
            ["IMatcher",           "CosineMatcher",                  "FAISSMatcher"],
        ],
        col_widths=[52, 60, W_TEXT - 112]
    )

    # LSP
    pdf.h2("2.3  LSP — Liskov Substitution Principle")
    pdf.para(
        "Turetilmis siniflar temel sinifin yerine gececek sekilde tasarlanmistir. "
        "container.py'da tum ajanlar BaseAgent listesiyle yonetilir."
    )
    pdf.code_block(
"""# container.py — tum ajanlar BaseAgent listesiyle yonetilir:
agents: list[BaseAgent] = [
    self._validation_agent,   # PhotoValidationAgent
    self._image_agent,        # ImageAgent
    self._matching_agent,     # MatchingAgent
    self._data_agent,         # DataAgent
]

for agent in agents:
    agent.start()        # Her biri BaseAgent.start() sozlesmesini uygular
    agent.stop()         # Her biri BaseAgent.stop() uygular
    agent.health_check() # Polimorfik — tip bilmek gerekmez""",
        title="LSP: Polimorfik ajan yonetimi"
    )

    # ISP
    pdf.h2("2.4  ISP — Interface Segregation Principle")
    pdf.para(
        "Her port arayuzu minimal ve ozguldur. Bir sinif kullanmayacagi "
        "metotlari implement etmek zorunda kalmaz."
    )
    pdf.code_block(
"""class IImagePreprocessor(ABC):
    @abstractmethod
    def preprocess(self, image_path: str) -> np.ndarray: ...
    # TEK METOD — ImageAgent'in ihtiyaci olan tek sey

class IMatcher(ABC):
    @abstractmethod
    def find_best_match(self, query, candidates,
                        threshold, top_k) -> MatchResult: ...
    # TEK METOD — MatchingAgent baska bir sey bilmez""",
        title="ISP: Minimal port arayuzleri"
    )

    # DIP
    pdf.add_page()
    pdf.h2("2.5  DIP — Dependency Inversion Principle")
    pdf.para(
        "Yuksek seviyeli moduller dusuk seviyeli modullere bagimli degil; "
        "ikisi de soyutlamalara (port arayuzlerine) bagimlidir. "
        "Tum somut baglantilar AppContainer'da tek noktada toplanir."
    )
    pdf.code_block(
"""# KOTU — tight coupling (somut sinifa bagimlilik):
class ImageAgent:
    def __init__(self):
        self.preprocessor = OpenCVPreprocessor()         # concrete!
        self.extractor    = TimmEfficientNetExtractor()  # concrete!

# IYI — DIP (soyut arayuze bagimlilik):
class ImageAgent(BaseAgent):
    def __init__(self,
                 event_bus:    EventBus,
                 preprocessor: IImagePreprocessor,    # soyut port
                 extractor:    IEmbeddingExtractor):  # soyut port
        self._preprocessor = preprocessor
        self._extractor    = extractor

# AppContainer — TEK BIRLESIM NOKTASI:
preprocessor = OpenCVPreprocessor()          # concrete burada
extractor    = TimmEfficientNetExtractor()   # concrete burada
image_agent  = ImageAgent(event_bus,
                          preprocessor,      # enjekte edilir
                          extractor)         # enjekte edilir""",
        title="DIP: Constructor injection ornegi"
    )

    pdf.accent_box(
        "DIP'in Pratikte Yansimasi",
        "Unit testlerde OpenCV veya PyTorch yuklenmeden mock IImagePreprocessor\n"
        "enjekte edilebilir. Gercek model yerine sahte 1280-dim vektor donduren\n"
        "bir nesne tum test suiti hizli calistirir (41 test ~ 4 saniye)."
    )

    # ──────────────────────────────────────────────────────────────────────
    #  3. CLEAN CODE
    # ──────────────────────────────────────────────────────────────────────
    pdf.h1("3. Clean Code Prensipleri")

    pdf.h2("3.1  Anlamli Isimlendirme")
    pdf.para(
        "Her sinif, metod ve degisken ismi ne yaptigini ya da ne oldugunu "
        "dogrudan anlatir. Kisaltmalar ve muphemlikler kullanilmaz."
    )
    pdf.code_block(
"""# Sinif isimleri — ne yaptiklarini anlatir:
PhotoValidationAgent      # Fotograf dogrular
TimmEfficientNetExtractor # timm ile EfficientNet embedding cikarir
SQLiteTurtleRepository    # SQLite ile kaplumbaga verileri
RegisterTurtleUseCase     # Kaplumbagayi kaydeden is akisi
CosineMatcher             # Cosine benzerligi ile eslestirir

# Metod isimleri — fiil + nesne:
validate(image_path)      # ne yaptiyor: validate
find_best_match(query)    # ne yaptiyor: find + best match
add_embedding(embedding)  # ne yaptiyor: add
get_all_embeddings()      # ne dondurdugu belli
has_embeddings()          # bool — soru sorar
is_normalized()           # bool — soru sorar
health_check()            # ne kontrol ettigi belli

# Degisken isimleri:
similarity_score = 0.876  # magic number degil, isimlendirilmis
matched_turtle_id         # ne oldugu belli
top_candidates            # list, ne icerdigi belli""",
        title="Anlamli isimlendirme ornekleri"
    )

    pdf.h2("3.2  Kucuk Fonksiyonlar (Tek Is)")
    pdf.para(
        "Her metod tek bir isi yapar. PhotoValidationAgent'in validate() metodu "
        "sadece orkestre eder; asil is 7 kucuk private metoda dagitilmistir."
    )
    pdf.code_block(
"""def validate(self, image_path: str) -> ValidationResult:
    result = ValidationResult(is_valid=True)
    path   = Path(image_path)

    self._check_file_exists(path, result)    # 10 satir
    if not result.is_valid:
        return result                         # erken cikis — deep nesting yok

    self._check_extension(path, result)      # 8 satir
    self._check_image_readable(path, result) # 12 satir
    self._check_dimensions(img, result)      # 10 satir
    self._check_blur(img, result)            # 12 satir
    self._check_brightness(img, result)      # 12 satir

    return result  # Orkestrasyonun tek gorevi""",
        title="Kucuk fonksiyonlar: validate() sadece orkestre eder"
    )

    pdf.h2("3.3  Hata Yonetimi")
    pdf.code_block(
"""# 1. EventBus — hata IZOLASYONU:
for handler in handlers:
    try:
        handler(event_type, payload)
    except Exception as exc:
        logger.error(f"Handler hatasi: {exc}")
        # Diger handler'lar calismaya devam eder

# 2. Use Case — hatalar EXCEPTION degil DTO ile tasinir:
validation = self._validation_agent.validate(request.photo_path)
if not validation.is_valid:
    return RegisterTurtleResponse(
        success=False,
        errors=validation.errors,    # UI'a iletilir
        warnings=validation.warnings,
    )

# 3. Repository — transaction GUVENLIGI:
with self._session_factory() as session:
    session.add(orm_object)
    session.commit()
# Context manager hata durumunda otomatik rollback yapar""",
        title="Hata yonetimi stratejileri (3 farkli katman)"
    )

    pdf.h2("3.4  Type Hints ve Frozen DTO")
    pdf.code_block(
"""from __future__ import annotations  # PEP 563 — lazy evaluation

# Tum metodlarda tam tip notasyonu:
def match(self, query_vector: np.ndarray) -> MatchResult: ...
def get_turtle(self, turtle_id: UUID) -> Turtle | None: ...
def list_turtles(self) -> list[Turtle]: ...

# Frozen dataclass — immutable DTO (yanlislikla mutasyon engellenir):
@dataclass(frozen=True)
class RegisterTurtleRequest:
    name:       str
    photo_path: str
    species:    str = ""
    notes:      str = ""

@dataclass(frozen=True)
class VerifyTurtleRequest:
    photo_path: str""",
        title="Type hints ve frozen DTO ornekleri"
    )

    pdf.h2("3.5  DRY — Don't Repeat Yourself")
    pdf.code_block(
"""# Mapper metodu tek yerde tanimli, her yerde kullanilir:
@staticmethod
def _embedding_from_orm(row: EmbeddingORM) -> Embedding:
    vector = np.frombuffer(row.vector_blob, dtype=np.float32).copy()
    return Embedding(turtle_id=UUID(row.turtle_id), vector=vector, ...)

@staticmethod
def _turtle_from_orm(row: TurtleORM) -> Turtle:
    turtle = Turtle(id=UUID(row.id), name=row.name, ...)
    for emb_row in row.embeddings:
        turtle.add_embedding(
            SQLiteTurtleRepository._embedding_from_orm(emb_row)  # tekrar kullanim
        )
    return turtle

# BaseAgent kisa yollar — DRY:
def _publish(self, event_type, payload=None):
    self._event_bus.publish(event_type, payload)  # tek satirda sarmalanmis""",
        title="DRY: mapper ve kisa yol ornekleri"
    )

    # ──────────────────────────────────────────────────────────────────────
    #  4. MULTI-AGENT
    # ──────────────────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.h1("4. Multi-Agent Mimarisi")

    pdf.para(
        "Sistem 6 ozerk ajandan olusur. Her ajan BaseAgent'tan turetilir, "
        "kendi yasam dongusuyle yonetilir ve EventBus uzerinden haberlesir. "
        "Ajanlar birbirini dogrudan import etmez."
    )

    pdf.h2("4.1  Ajan Tanim Tablosu")
    pdf.table(
        ["Ajan", "Sorumluluk", "Dinledigi", "Yayimladigi"],
        [
            ["ConfigAgent",           "settings.json yonetimi",       "—",                "CONFIG_CHANGED"],
            ["PhotoValidationAgent",  "Fotograf kalite kontrolu",     "—",                "PHOTO_VALID\nPHOTO_INVALID"],
            ["ImageAgent",            "Embedding vektoru uretimi",    "—",                "EMBEDDING_READY\nEMBEDDING_FAILED"],
            ["MatchingAgent",         "Cosine esleme",                "CONFIG_CHANGED",   "MATCH_FOUND\nMATCH_NOT_FOUND"],
            ["DataAgent",             "CRUD + dogrulama logu",        "MATCH_FOUND\nMATCH_NOT_FOUND", "TURTLE_SAVED\nDATA_ERROR"],
            ["UIAgent",               "PySide6 sayfa yonetimi",       "—",                "—"],
        ],
        col_widths=[40, 50, 38, W_TEXT - 128]
    )

    pdf.h2("4.2  BaseAgent Sozlesmesi")
    pdf.code_block(
"""class AgentStatus(Enum):
    IDLE    = auto()
    BUSY    = auto()
    ERROR   = auto()
    STOPPED = auto()

class BaseAgent(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...          # Her ajanin benzersiz adi

    def start(self) -> None:            # Baslat + handler kaydet
        self._register_handlers()

    def stop(self) -> None: ...         # Durdur + kaynaklar serbest

    def health_check(self) -> bool:     # ERROR/STOPPED ise False
        return self._status not in (AgentStatus.ERROR, AgentStatus.STOPPED)

    def _register_handlers(self) -> None:
        # Alt siniflar override eder — Template Method Pattern
        pass

    def _publish(self, event_type, payload=None):
        self._event_bus.publish(event_type, payload)  # kisa yol

    def _subscribe(self, event_type, handler):
        self._event_bus.subscribe(event_type, handler)""",
        title="BaseAgent: Template Method Pattern ile temel sozlesme"
    )

    pdf.h2("4.3  Ajan Bagimliliklari")
    pdf.code_block(
"""AppContainer
    |
    +-- EventBus (paylasilir) ─────────────────────────┐
    |                                                    | pub/sub
    +-- ConfigAgent ─── CONFIG_CHANGED ─────────────────┤
    |                                                    |
    +-- PhotoValidationAgent ─ PHOTO_VALID ─────────────┤
    |                                                    |
    +-- ImageAgent                                       |
    |     +-- IImagePreprocessor (OpenCVPreprocessor)    |
    |     +-- IEmbeddingExtractor (TimmExtractor)        |
    |                       EMBEDDING_READY ─────────────┤
    |                                                    |
    +-- MatchingAgent                                    |
    |     +-- IMatcher (CosineMatcher)                   |
    |     +-- ITurtleRepository ── MATCH_FOUND ──────────┤
    |                                                    |
    +-- DataAgent                                        |
          +-- ITurtleRepository  ─── MATCH_FOUND ────────┘
                                     (otomatik audit log)""",
        title="Ajan bagimliliklari (yalnizca port arayuzleri)"
    )

    # ──────────────────────────────────────────────────────────────────────
    #  5. EVENTBUS
    # ──────────────────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.h1("5. EventBus Mekanizmasi")

    pdf.para(
        "EventBus, ajanlar arasi dogrudan import'u ortadan kaldiran "
        "merkezi iletisim katmanidir. Thread-safe pub/sub modeli uygular; "
        "bir handler'in hatasi diger handler'lari etkilemez."
    )

    pdf.h2("5.1  Thread-Safe Tasarim")
    pdf.code_block(
"""class EventBus:
    def __init__(self):
        self._handlers = defaultdict(list)
        self._lock      = threading.Lock()

    def subscribe(self, event_type, handler):
        with self._lock:                # Kritik bolge (KISA)
            self._handlers[event_type].append(handler)

    def publish(self, event_type, payload=None):
        with self._lock:
            handlers = list(self._handlers.get(event_type, []))
        # LOCK BURADA BITIYOR — handler cagrisi lock disinda
        # Neden? Handler baska bir olay publish ederse DEADLOCK olmaz

        for handler in handlers:
            try:
                handler(event_type, payload)
            except Exception as exc:
                logger.error(f"Handler hatasi: {exc}")
                # Diger handler'lar calismaya devam eder""",
        title="EventBus: Thread-safe implementasyon ve hata izolasyonu"
    )

    pdf.h2("5.2  Olay Tipleri (13 EventType)")
    pdf.table(
        ["Kategori", "Olay Tipleri", "Yayimlayan"],
        [
            ["Fotograf", "PHOTO_VALIDATION_STARTED\nPHOTO_VALID / PHOTO_INVALID", "PhotoValidationAgent"],
            ["Embedding", "EMBEDDING_STARTED\nEMBEDDING_READY / EMBEDDING_FAILED", "ImageAgent"],
            ["Esleme", "MATCHING_STARTED\nMATCH_FOUND / MATCH_NOT_FOUND", "MatchingAgent"],
            ["Veri", "TURTLE_SAVED / TURTLE_LOADED\nDATA_ERROR", "DataAgent"],
            ["Konfigurasyon", "CONFIG_CHANGED", "ConfigAgent"],
        ],
        col_widths=[35, 72, W_TEXT - 107]
    )

    pdf.h2("5.3  Tight Coupling vs EventBus")
    pdf.code_block(
"""# KOTU — Tight Coupling:
class DataAgent:
    def __init__(self, matching_agent: MatchingAgent):
        # DataAgent, MatchingAgent'i import etmek zorunda
        # -> Circular import riski
        # -> Test ederken her ikisini de hazirlamak gerekir
        self._matching = matching_agent

# IYI — EventBus ile Loose Coupling:
class MatchingAgent(BaseAgent):
    def match(self, query_vector):
        result = self._matcher.find_best_match(...)
        self._publish(EventType.MATCH_FOUND, result)  # Kime gidecegini bilmez

class DataAgent(BaseAgent):
    def _register_handlers(self):
        self._subscribe(EventType.MATCH_FOUND, self._on_match_found)

    def _on_match_found(self, event_type, result):
        self._save_verification_log(result)  # Otomatik audit log""",
        title="EventBus: Loose coupling vs tight coupling karsilastirmasi"
    )

    # ──────────────────────────────────────────────────────────────────────
    #  6. PORT/ADAPTER
    # ──────────────────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.h1("6. Port / Adapter (Hexagonal) Mimarisi")

    pdf.para(
        "Hexagonal mimaride ic katmanlar (domain, use cases) disaridaki "
        "sistemleri (SQLite, OpenCV, timm) dogrudan tanimaz. "
        "Port arayuzleri bu iki dunyayi birbirinden ayirir."
    )

    pdf.code_block(
"""UI KATMANI (PySide6)
       |
       v  cagri
USE CASE KATMANI (RegisterTurtle, VerifyTurtle)
       |
       v  port arayuzu (DIP)
CORE / DOMAIN (Turtle, Embedding, MatchResult)
       ^
       |  implement eder
ADAPTER KATMANI
       |
       v  kullanir
HARICI SISTEMLER (SQLite, OpenCV, timm, sklearn)""",
        title="Hexagonal mimaride katman bagimlilik kurali"
    )

    pdf.h2("6.1  Port Eslesme Tablosu")
    pdf.table(
        ["Port (ABC)", "Adapter", "Harici Sistem"],
        [
            ["ITurtleRepository",   "SQLiteTurtleRepository",        "SQLAlchemy + SQLite"],
            ["IImagePreprocessor",  "OpenCVPreprocessor",             "OpenCV + numpy"],
            ["IEmbeddingExtractor", "TimmEfficientNetExtractor",      "timm + PyTorch"],
            ["IMatcher",            "CosineMatcher",                  "scikit-learn"],
        ],
        col_widths=[50, 60, W_TEXT - 110]
    )

    pdf.h2("6.2  Adapter Degistirme Ornegi")
    pdf.code_block(
"""# Senaryo: SQLite yerine PostgreSQL kullanmak

# Adim 1 — Yeni adapter (ITurtleRepository implement et):
class PostgreSQLRepository(ITurtleRepository):
    def __init__(self, connection_string: str): ...
    def save(self, turtle: Turtle) -> Turtle: ...
    def find_by_id(self, turtle_id: UUID) -> Turtle | None: ...
    # ... diger metodlar

# Adim 2 — container.py'da TEK SATIRLIK degisiklik:
# repository = SQLiteTurtleRepository(session_factory)
repository = PostgreSQLRepository("postgresql://user:pass@host/db")

# Hicbir use case, ajan veya test degismez.""",
        title="OCP + DIP: Adapter degistirmek 1-2 satir"
    )

    pdf.h2("6.3  Repository Pattern")
    pdf.code_block(
"""# Domain katmani SQLite detayini hic gormez:
class RegisterTurtleUseCase:
    def execute(self, request):
        turtle = Turtle(name=request.name, ...)
        # Veritabani mi? Redis mi? PostgreSQL mi? Bilmez.
        saved = self._data_agent.save_turtle(turtle)
        return RegisterTurtleResponse(success=True, turtle=saved)

# Vektor BLOB serializasyonu yalnizca repository'de:
@staticmethod
def _embedding_to_orm(emb: Embedding) -> EmbeddingORM:
    return EmbeddingORM(
        vector_blob = emb.vector.astype(np.float32).tobytes(),  # BLOB
        vector_dim  = emb.dimension,
        ...
    )

@staticmethod
def _embedding_from_orm(row: EmbeddingORM) -> Embedding:
    vector = np.frombuffer(row.vector_blob, dtype=np.float32).copy()
    return Embedding(vector=vector, ...)  # Domain nesnesine donusturuluyor""",
        title="Repository pattern: Domain <-> ORM donusumu"
    )

    # ──────────────────────────────────────────────────────────────────────
    #  7. IS AKISLARI
    # ──────────────────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.h1("7. Is Akislari — Kayit ve Dogrulama")

    pdf.h2("7.1  Kaplumbaga Kayit Akisi")
    pdf.code_block(
"""Kullanici 'Kaydet' tiklar
    |
    v
RegisterWorker(QThread).run()       <- UI thread'i bloke etmez
    |
    v
RegisterTurtleUseCase.execute(RegisterTurtleRequest)
    |
    +-> 1. PhotoValidationAgent.validate(photo_path)
    |       +-- PHOTO_VALIDATION_STARTED yayimla
    |       +-- _check_file_exists(), _check_extension()
    |       +-- _check_dimensions(), _check_blur(), _check_brightness()
    |       +-- PHOTO_VALID yayimla (ya da PHOTO_INVALID -> erken donus)
    |
    +-> 2. Turtle nesnesi olustur (UUID otomatik, kayit tarihi otomatik)
    |
    +-> 3. ImageAgent.process(photo_path, turtle.id)
    |       +-- EMBEDDING_STARTED yayimla
    |       +-- OpenCVPreprocessor: letterbox + CLAHE + ImageNet normalize
    |       +-- TimmEfficientNetExtractor: EfficientNet-B0 -> (1280,)
    |       +-- L2 normalize -> norm ~= 1.0
    |       +-- EMBEDDING_READY yayimla -> Embedding nesnesi
    |
    +-> 4. turtle.add_embedding(embedding)
    |
    +-> 5. DataAgent.save_turtle(turtle)
            +-- SQLiteTurtleRepository.save()
            |     +-- TurtleORM olustur
            |     +-- EmbeddingORM olustur (vector -> float32 bytes BLOB)
            |     +-- session.commit()
            +-- TURTLE_SAVED yayimla

Qt Signal -> Ana thread -> UI: 'Alpha basariyla kaydedildi'""",
        title="RegisterTurtleUseCase akisi (adim adim)"
    )

    pdf.h2("7.2  Kaplumbaga Dogrulama Akisi")
    pdf.code_block(
"""Kullanici 'Dogrula' tiklar
    |
    v
VerifyWorker(QThread).run()
    |
    v
VerifyTurtleUseCase.execute(VerifyTurtleRequest)
    |
    +-> 1. PhotoValidationAgent.validate(photo_path)
    |       [ayni kontroller — PHOTO_VALID veya erken donus]
    |
    +-> 2. ImageAgent.process(photo_path, uuid4())  <- gecici UUID
    |       [ayni pipeline — EMBEDDING_READY]
    |
    +-> 3. MatchingAgent.match(query_embedding.vector)
    |       +-- MATCHING_STARTED yayimla
    |       +-- Repository.get_all_embeddings() -> N vektor
    |       +-- np.stack() -> (N, 1280) matris
    |       +-- cosine_similarity(query, matris) -> (N,) skorlar
    |       +-- argsort descending -> top-3 aday
    |       +-- best_score >= threshold (varsayilan 0.82)?
    |             Evet -> MATCH_FOUND yayimla  ----+
    |             Hayir -> MATCH_NOT_FOUND     ----+
    |                                             |
    |                    DataAgent dinler <--------+
    |                    VerificationLogORM: audit trail otomatik
    |
    +-> 4. Eslesme varsa DataAgent.get_turtle(matched_id)
    |       +-- TURTLE_LOADED yayimla
    |
    +-> 5. match_result.matched_turtle = turtle

Qt Signal -> Ana thread -> ResultView: eslesme rozeti + guven skoru""",
        title="VerifyTurtleUseCase akisi (adim adim)"
    )

    pdf.h2("7.3  Audit Trail — Otomatik Dogrulama Logu")
    pdf.para(
        "Her dogrulama islemi VerificationLogORM tablosuna otomatik yazilir. "
        "DataAgent, MATCH_FOUND ve MATCH_NOT_FOUND olaylarini dinler; "
        "use case bu logu hic bilmez — tamamen EventBus uzerinden saglanir."
    )
    pdf.code_block(
"""class DataAgent(BaseAgent):
    def _register_handlers(self):
        # Her dogrulamayi otomatik logla — use case bunu bilmez:
        self._subscribe(EventType.MATCH_FOUND,     self._on_match_found)
        self._subscribe(EventType.MATCH_NOT_FOUND, self._on_match_not_found)

    def _on_match_found(self, _event_type, result: MatchResult):
        self._save_verification_log(result)

    def _save_verification_log(self, result):
        log = VerificationLogORM(
            id               = str(uuid4()),
            matched_turtle_id= str(result.matched_turtle_id),
            similarity_score = result.similarity_score,
            confidence_score = result.confidence,
            threshold_used   = result.threshold_used,
            is_match         = result.is_match,
            verified_at      = datetime.now(timezone.utc),
        )
        session.add(log)
        session.commit()""",
        title="Otomatik audit trail — EventBus ile SRP korunur"
    )

    # ──────────────────────────────────────────────────────────────────────
    #  8. TEST YAPISI
    # ──────────────────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.h1("8. Test Yapisi")

    pdf.h2("8.1  Test Dosyalari")
    pdf.table(
        ["Dosya", "Tip", "Test Sayisi", "Kapsam"],
        [
            ["test_event_bus.py",        "Birim",       "7",  "Pub/sub, thread safety (20 thread), hata izolasyonu"],
            ["test_matcher.py",          "Birim",       "7",  "Cosine esleme, esik mantigi, top-k, edge cases"],
            ["test_models.py",           "Birim",       "13", "Turtle, Embedding, MatchResult, confidence hesabi"],
            ["test_validation_agent.py", "Birim",       "4",  "Fotograf dogrulama + EventBus entegrasyonu"],
            ["test_repository.py",       "Entegrasyon", "10", "SQLite CRUD, vektor saklama, soft delete"],
            ["TOPLAM",                   "",            "41", "%100 gecme orani"],
        ],
        col_widths=[48, 26, 22, W_TEXT - 96]
    )

    pdf.h2("8.2  Ornek Birim Test")
    pdf.code_block(
"""class TestCosineMatcher:
    def test_ayni_vektor_eslesir(self, matcher, make_embedding):
        vec = np.random.randn(128).astype(np.float32)
        vec /= np.linalg.norm(vec)          # L2 normalize
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
        assert result.is_match is False     # Edge case: bos liste""",
        title="test_matcher.py ornekleri"
    )

    pdf.h2("8.3  Entegrasyon Test Duzeni")
    pdf.code_block(
"""@pytest.fixture
def repo(tmp_path):
    \"\"\"In-memory SQLite — disk IO yok, hizli (< 4 sn toplam).\"\"\"
    engine  = build_engine(":memory:")
    factory = build_session_factory(engine)
    init_db(engine)
    return SQLiteTurtleRepository(factory)

def test_embedding_vektoru_bozulmadan_geri_gelir(repo, make_turtle):
    \"\"\"float32 BLOB saklama / geri yukleme duyarlilik testi.\"\"\"
    original = np.random.randn(1280).astype(np.float32)
    original /= np.linalg.norm(original)

    turtle    = make_turtle()
    embedding = Embedding(turtle_id=turtle.id, vector=original, ...)
    turtle.add_embedding(embedding)
    saved = repo.save(turtle)

    loaded  = repo.find_by_id(saved.id)
    restored = loaded.embeddings[0].vector

    np.testing.assert_array_almost_equal(original, restored, decimal=5)
    # 5 ondalik basamak hassasiyet — float32 BLOB'da kayip yok""",
        title="test_repository.py: Vektor BLOB duyarlilik testi"
    )

    pdf.h2("8.4  Thread-Safety Testi")
    pdf.code_block(
"""def test_thread_safe_publish(self, bus):
    \"\"\"20 thread ayni anda publish ediyor — kayip veya deadlock olmamali.\"\"\"
    results = []
    def handler(event_type, payload):
        results.append(payload)

    bus.subscribe(EventType.TURTLE_SAVED, handler)

    threads = [
        threading.Thread(
            target=bus.publish,
            args=(EventType.TURTLE_SAVED, i)
        )
        for i in range(20)
    ]
    for t in threads: t.start()
    for t in threads: t.join()

    assert len(results) == 20   # Hic kayip yok""",
        title="test_event_bus.py: 20 thread ile thread-safety dogrulamasi"
    )

    # ──────────────────────────────────────────────────────────────────────
    #  9. ISTATISTIKLER VE OZET
    # ──────────────────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.h1("9. Kod Istatistikleri ve Ozet")

    pdf.h2("9.1  Kod Istatistikleri")
    pdf.table(
        ["Metrik", "Deger"],
        [
            ["Kaynak kodu (src/)",          "3.974 satir"],
            ["Test kodu (tests/)",           "493 satir"],
            ["Toplam Python dosyasi",        "52 dosya"],
            ["Ajan sayisi",                  "6 ajan (BaseAgent haric)"],
            ["Port arayuzu (ABC)",           "4 arayuz"],
            ["Adapter implementasyonu",      "4 adapter"],
            ["Use case",                     "2 (Register + Verify)"],
            ["ORM tablosu",                  "3 (turtles, embeddings, verification_log)"],
            ["UI sayfasi",                   "5 sayfa"],
            ["Birim testi",                  "31 test"],
            ["Entegrasyon testi",            "10 test"],
            ["Test basari orani",            "%100 (41/41)"],
            ["Test suresi",                  "~4 saniye (in-memory SQLite)"],
            ["Git commit",                   "21 commit"],
        ],
        col_widths=[90, W_TEXT - 90]
    )

    pdf.h2("9.2  Uygulanan Prensipler Ozeti")
    pdf.table(
        ["Prensip", "Uygulama", "Kanit"],
        [
            ["SRP",          "12 sinif/ajan tek sorumluluk",     "PhotoValidationAgent sadece dogrular"],
            ["OCP",          "Port arayuzleri",                  "Yeni adapter = 1-2 satir container"],
            ["LSP",          "BaseAgent hiyerarsisi",            "list[BaseAgent] polimorfik yonetim"],
            ["ISP",          "Minimal port arayuzleri",          "IImagePreprocessor: 1 metod"],
            ["DIP",          "Constructor injection",            "Tum ajanlar port arayuzune bagimli"],
            ["Anlamli isim", "Fiil+nesne metod isimleri",        "find_best_match, has_embeddings"],
            ["Kucuk fonksiyon","Tek is yapan metodlar",          "7 private _check_*() metodu"],
            ["Hata yonetimi","DTO + hata izolasyonu",            "EventBus handler hatalari izole"],
            ["DRY",          "Mapper + BaseAgent kisayollar",     "_embedding_from_orm tekrar kullanim"],
            ["Type hints",   "Tum metodlar notasyonlu",          "Python 3.11+ frozen dataclass DTO"],
            ["Pub/Sub",      "Thread-safe EventBus",             "Ajanlar birbirini import etmiyor"],
            ["Hexagonal",    "Port/Adapter ayirimi",             "Harici sistem swap edilebilir"],
        ],
        col_widths=[38, 54, W_TEXT - 92]
    )

    pdf.h2("9.3  Mimari Guclu Yonler")

    points = [
        ("Degistirilebilirlik",
         "Veritabani, model veya esleme algoritmasi degistirmek icin\n"
         "yalnizca container.py'da 1-2 satir degisiklik yeterlidir."),
        ("Test edilebilirlik",
         "Port arayuzleri sayesinde mock enjeksiyonu kolaydir.\n"
         "Entegrasyon testleri in-memory SQLite ile disk IO olmadan calisir."),
        ("Genisletilebilirlik",
         "Yeni ajan eklemek: BaseAgent'i turet, _register_handlers()\n"
         "override et, container.py'a ekle."),
        ("Hata yalitimi",
         "Bir EventBus handler hatasi sistemi durdurmaz.\n"
         "Use case hatalari exception degil DTO ile tasinir."),
        ("Dusuk baglilik",
         "Ajanlar birbirini import etmiyor; yalnizca EventBus\n"
         "ve port arayuzleri uzerinden haberlesiyorlar."),
        ("Thread safety",
         "EventBus Lock granularitesi optimize edilmistir.\n"
         "Uzun islemler QThread worker'larinda calisir."),
    ]
    for title, text in points:
        pdf.set_x(MARGIN)
        pdf.set_font("DejaVuB", size=10)
        pdf.set_text_color(*C_H2)
        pdf.cell(4, 6, ">>")
        pdf.cell(W_TEXT - 4, 6, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_x(MARGIN + 6)
        pdf._body(9.5)
        pdf.set_text_color(*C_BODY)
        for line in text.split("\n"):
            pdf.set_x(MARGIN + 8)
            pdf.cell(W_TEXT - 8, 5, line, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(1)

    pdf.divider()
    pdf._italic(9)
    pdf.set_text_color(*C_SUBTLE)
    pdf.cell(0, 6, "Kaynak: github.com/YusufAltunbay/HW_Turtle",
             align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)


# ═══════════════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════════════

def main():
    print("PDF raporu olusturuluyor...")
    pdf = PDF(orientation="P", unit="mm", format="A4")
    pdf.set_margins(MARGIN, 14, MARGIN)
    pdf.set_auto_page_break(auto=True, margin=16)
    pdf.setup_fonts()
    build_report(pdf)
    pdf.output(OUT)
    print(f"[TAMAM] {OUT} olusturuldu  ({os.path.getsize(OUT) // 1024} KB)")


if __name__ == "__main__":
    main()
