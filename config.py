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

# تنظیمات کالیبراسیون
CALIBRATION_POINTS = 4  # تعداد نقاط برای perspective transform
KEYBOARD_REGION_MARGIN = 20  # حاشیه منطقه کیبورد (پیکسل)

# تنظیمات پیانو
PIANO_OCTAVES = 7  # از C2 تا C8
LOWEST_NOTE = 36  # MIDI note number (C2)
HIGHEST_NOTE = 96  # MIDI note number (C7)
TOTAL_KEYS = 88

# تنظیمات تشخیص نت
NOTE_DETECTION_THRESHOLD = 0.3  # حداقل فاصله از مرکز کلاویه برای تشخیص
VELOCITY_SENSITIVITY = 0.5  # حساسیت velocity (0-1)
NOTE_OFF_DELAY = 0.1  # تاخیر قبل از note off (ثانیه)

# تنظیمات درس
DEFAULT_TEMPO = 120  # BPM
TOLERANCE_MS = 200  # تحمل زمانی برای تشخیص نت (میلی‌ثانیه)
TOLERANCE_SEMITONE = 1  # تحمل نیم‌پرده برای تشخیص نت

# تنظیمات مترونوم
METRONOME_VOLUME = 0.7
METRONOME_BEATS_PER_BAR = 4

# تنظیمات دیتابیس
DATABASE_PATH = DATA_DIR / "piano_tutor.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# تنظیمات لاگینگ
LOG_LEVEL = "INFO"
LOG_FILE = DATA_DIR / "piano_tutor.log"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# رنگ‌ها (RGB)
COLORS = {
    "white_key": (255, 255, 255),
    "black_key": (0, 0, 0),
    "white_key_pressed": (200, 200, 255),
    "black_key_pressed": (100, 100, 200),
    "hand_landmark": (0, 255, 0),
    "hand_connection": (255, 255, 0),
    "correct_note": (0, 255, 0),
    "wrong_note": (255, 0, 0),
    "missed_note": (255, 165, 0),
}

# تنظیمات MediaPipe
MEDIAPIPE_MODEL_COMPLEXITY = 1  # 0, 1, or 2
MEDIAPIPE_MAX_NUM_HANDS = 2

# تنظیمات UI
FONT_FAMILY = "Arial"
FONT_SIZE_LARGE = 18
FONT_SIZE_MEDIUM = 14
FONT_SIZE_SMALL = 12



