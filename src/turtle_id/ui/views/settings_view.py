"""
SettingsView: Uygulama ayarları ekranı.

Eşleşme eşiği, top-k sonuç sayısı gibi parametreler
buradan değiştirilebilir. Değişiklikler anında ConfigAgent'a
iletilir ve CONFIG_CHANGED olayı ile MatchingAgent güncellenir.
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from turtle_id.agents.config_agent import ConfigAgent


class SettingsView(QWidget):
    """Eşleşme parametrelerini yönetme ekranı."""

    def __init__(self, config_agent: ConfigAgent, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._config = config_agent
        self._setup_ui()
        self._load_current_values()

    # ------------------------------------------------------------------ #
    #  UI kurulumu                                                          #
    # ------------------------------------------------------------------ #

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("Ayarlar")
        title.setObjectName("page_title")
        layout.addWidget(title)

        subtitle = QLabel("Eşleşme ve tanıma parametrelerini buradan ayarlayın.")
        subtitle.setObjectName("status_label")
        layout.addWidget(subtitle)

        layout.addWidget(self._divider())

        # --- Eşleşme eşiği ---
        layout.addWidget(self._section("EŞLEŞMEEŞİĞİ (Similarity Threshold)"))

        threshold_desc = QLabel(
            "İki fotoğrafın aynı kaplumbağaya ait sayılabilmesi için gereken\n"
            "minimum benzerlik skoru. Yüksek değer → daha katı eşleşme."
        )
        threshold_desc.setObjectName("status_label")
        threshold_desc.setWordWrap(True)
        layout.addWidget(threshold_desc)

        threshold_row = QHBoxLayout()
        self._threshold_slider = QSlider(Qt.Horizontal)
        self._threshold_slider.setRange(50, 99)   # 0.50 – 0.99
        self._threshold_slider.setTickInterval(5)
        self._threshold_slider.setTickPosition(QSlider.TicksBelow)
        self._threshold_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                background: #37474f; height: 6px; border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #4fc3f7; width: 18px; height: 18px;
                margin: -6px 0; border-radius: 9px;
            }
            QSlider::sub-page:horizontal {
                background: #1565c0; border-radius: 3px;
            }
        """)
        threshold_row.addWidget(self._threshold_slider, stretch=1)

        self._threshold_label = QLabel("0.82")
        self._threshold_label.setFixedWidth(40)
        self._threshold_label.setAlignment(Qt.AlignCenter)
        self._threshold_label.setStyleSheet("color: #4fc3f7; font-weight: bold; font-size: 15px;")
        threshold_row.addWidget(self._threshold_label)
        layout.addLayout(threshold_row)

        hint_row = QHBoxLayout()
        hint_row.addWidget(QLabel("Gevşek (0.50)"))
        hint_row.addStretch()
        hint_row.addWidget(QLabel("Katı (0.99)"))
        for w in [hint_row.itemAt(0).widget(), hint_row.itemAt(2).widget()]:
            w.setObjectName("info_key")
        layout.addLayout(hint_row)

        layout.addWidget(self._divider())

        # --- Top-K sonuç sayısı ---
        layout.addWidget(self._section("ADAY SONUÇ SAYISI (Top-K)"))

        topk_desc = QLabel(
            "Doğrulama sırasında değerlendirilen en iyi aday sayısı.\n"
            "Artırmak doğruluğu hafifçe iyileştirebilir."
        )
        topk_desc.setObjectName("status_label")
        topk_desc.setWordWrap(True)
        layout.addWidget(topk_desc)

        topk_row = QHBoxLayout()
        topk_label = QLabel("Top-K değeri:")
        topk_label.setObjectName("info_key")
        topk_row.addWidget(topk_label)
        self._topk_spin = QSpinBox()
        self._topk_spin.setRange(1, 10)
        self._topk_spin.setFixedWidth(80)
        self._topk_spin.setStyleSheet("""
            QSpinBox {
                background: #1e2128; color: #e0e6f0;
                border: 1px solid #37474f; border-radius: 6px;
                padding: 4px 8px; font-size: 14px;
            }
        """)
        topk_row.addWidget(self._topk_spin)
        topk_row.addStretch()
        layout.addLayout(topk_row)

        layout.addWidget(self._divider())

        # --- Model bilgisi ---
        layout.addWidget(self._section("MODEL BİLGİSİ"))
        self._model_label = QLabel()
        self._model_label.setObjectName("info_value")
        layout.addWidget(self._model_label)

        layout.addWidget(self._divider())

        # --- Kaydet butonu ---
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        save_btn = QPushButton("Ayarları Kaydet")
        save_btn.setObjectName("primary_button")
        save_btn.clicked.connect(self._save)
        btn_row.addWidget(save_btn)

        reset_btn = QPushButton("Varsayılanlara Dön")
        reset_btn.setObjectName("secondary_button")
        reset_btn.clicked.connect(self._reset_defaults)
        btn_row.addWidget(reset_btn)
        layout.addLayout(btn_row)

        self._status_label = QLabel("")
        self._status_label.setObjectName("status_label")
        self._status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._status_label)

        layout.addStretch()

        # Sinyal bağlantıları
        self._threshold_slider.valueChanged.connect(self._on_threshold_changed)

    # ------------------------------------------------------------------ #
    #  Slot'lar                                                            #
    # ------------------------------------------------------------------ #

    def _on_threshold_changed(self, value: int) -> None:
        self._threshold_label.setText(f"{value / 100:.2f}")

    def _save(self) -> None:
        threshold = self._threshold_slider.value() / 100
        top_k = self._topk_spin.value()
        self._config.set("similarity_threshold", threshold)
        self._config.set("top_k_results", top_k)
        self._config.save()
        self._status_label.setStyleSheet("color: #a5d6a7;")
        self._status_label.setText("✓  Ayarlar kaydedildi.")

    def _reset_defaults(self) -> None:
        self._threshold_slider.setValue(82)
        self._topk_spin.setValue(3)
        self._status_label.setStyleSheet("color: #ffcc80;")
        self._status_label.setText("Varsayılan değerler yüklendi — kaydetmek için 'Ayarları Kaydet'e tıklayın.")

    # ------------------------------------------------------------------ #
    #  Private                                                             #
    # ------------------------------------------------------------------ #

    def _load_current_values(self) -> None:
        threshold_int = int(self._config.similarity_threshold * 100)
        self._threshold_slider.setValue(threshold_int)
        self._topk_spin.setValue(self._config.top_k_results)
        model = self._config.get("model_name", "efficientnet_b0")
        self._model_label.setText(
            f"Aktif model: {model}\n"
            f"Embedding boyutu: 1280\n"
            f"Çıkarım cihazı: CPU"
        )

    @staticmethod
    def _section(text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setObjectName("section_label")
        return lbl

    @staticmethod
    def _divider() -> QFrame:
        f = QFrame()
        f.setFrameShape(QFrame.HLine)
        return f
