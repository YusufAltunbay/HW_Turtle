"""
pytest konfigürasyonu — src/ dizinini Python path'e ekler.
"""
import sys
from pathlib import Path

# src/ klasörünü path'e ekle
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
