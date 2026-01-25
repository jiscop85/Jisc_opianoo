"""
ثوابت و مقادیر ثابت برنامه
"""
import config

# MIDI Note Numbers
MIDI_NOTES = {
    'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3,
    'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8,
    'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11
}

# نام نت‌ها
NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

# نقش انگشتان
FINGER_MAPPING = {
    'thumb': 1,
    'index': 2,
    'middle': 3,
    'ring': 4,
    'pinky': 5
}

# MediaPipe Hand Landmarks
HAND_LANDMARKS = {
    'WRIST': 0,
    'THUMB_CMC': 1,
    'THUMB_MCP': 2,
    'THUMB_IP': 3,
    'THUMB_TIP': 4,
    'INDEX_MCP': 5,
    'INDEX_PIP': 6,
    'INDEX_DIP': 7,
    'INDEX_TIP': 8,
    'MIDDLE_MCP': 9,
    'MIDDLE_PIP': 10,
    'MIDDLE_DIP': 11,
    'MIDDLE_TIP': 12,
    'RING_MCP': 13,
    'RING_PIP': 14,
    'RING_DIP': 15,
    'RING_TIP': 16,
    'PINKY_MCP': 17,
    'PINKY_PIP': 18,
    'PINKY_DIP': 19,
    'PINKY_TIP': 20
}

# کلیدهای سفید و سیاه در یک اکتاو
WHITE_KEYS_PER_OCTAVE = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
BLACK_KEYS_PER_OCTAVE = ['C#', 'D#', 'F#', 'G#', 'A#']

# تعداد کلیدهای سفید و سیاه در پیانو 88 کلاویه
TOTAL_WHITE_KEYS = 52
TOTAL_BLACK_KEYS = 36

# محدوده MIDI برای پیانو استاندارد
PIANO_MIDI_RANGE = (21, 108)  # A0 تا C8

# رنگ‌ها
COLORS = config.COLORS

# تنظیمات پیش‌فرض
DEFAULT_SETTINGS = {
    'tempo': config.DEFAULT_TEMPO,
    'volume': 0.7,
    'metronome_enabled': True,
    'hand_tracking_enabled': True,
    'show_landmarks': True,
    'show_sheet_music': True
}

