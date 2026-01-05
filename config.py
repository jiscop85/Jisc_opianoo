"""
تنظیمات جهانی برنامه Piano Master Tutor
"""
import os
from pathlib import Path

# مسیرهای اصلی
BASE_DIR = Path(__file__).parent
ASSETS_DIR = BASE_DIR / "assets"
DATA_DIR = BASE_DIR / "data"
SOUNDFONTS_DIR = ASSETS_DIR / "soundfonts"
MIDI_DIR = ASSETS_DIR / "midi_files"
ICONS_DIR = ASSETS_DIR / "icons"

# اطمینان از وجود دایرکتوری‌ها
DATA_DIR.mkdir(exist_ok=True)
SOUNDFONTS_DIR.mkdir(exist_ok=True)
MIDI_DIR.mkdir(exist_ok=True)
ICONS_DIR.mkdir(exist_ok=True)

# تنظیمات SoundFont
DEFAULT_SOUNDFONT = SOUNDFONTS_DIR / "SalamanderGrandPiano.sf2"
SOUNDFONT_PATH = os.getenv("SOUNDFONT_PATH", str(DEFAULT_SOUNDFONT))

# تنظیمات رزولوشن
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080
WEBCAM_WIDTH = 640
WEBCAM_HEIGHT = 480

# تنظیمات تشخیص دست
HAND_DETECTION_CONFIDENCE = 0.7
HAND_TRACKING_CONFIDENCE = 0.5
MIN_HAND_VISIBILITY = 0.5

