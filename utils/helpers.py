"""
توابع کمکی مشترک
"""
import numpy as np
import cv2
from typing import Tuple, List, Optional
import config



def map_coordinates(
    point: Tuple[float, float],
    src_points: np.ndarray,
    dst_points: np.ndarray
) -> Tuple[float, float]:
    """
    تبدیل مختصات یک نقطه با استفاده از perspective transform
    
    Args:
        point: نقطه ورودی (x, y)
        src_points: نقاط مبدا (4 نقطه)
        dst_points: نقاط مقصد (4 نقطه)
    
    Returns:
        نقطه تبدیل شده (x, y)
    """
    if src_points is None or dst_points is None:
        return point
    
    try:
        matrix = cv2.getPerspectiveTransform(src_points, dst_points)
        point_array = np.array([[[point[0], point[1]]]], dtype=np.float32)
        transformed = cv2.perspectiveTransform(point_array, matrix)
        return (float(transformed[0][0][0]), float(transformed[0][0][1]))
    except Exception:
        return point


def calculate_distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """محاسبه فاصله اقلیدسی بین دو نقطه"""
    return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)


def midi_to_note_name(midi_number: int) -> str:
    """تبدیل شماره MIDI به نام نت"""
    from .constants import NOTE_NAMES
    octave = (midi_number // 12) - 1
    note = NOTE_NAMES[midi_number % 12]
    return f"{note}{octave}"


def note_name_to_midi(note_name: str) -> Optional[int]:
    """تبدیل نام نت به شماره MIDI"""
    from .constants import MIDI_NOTES
    
    # حذف فاصله‌ها و تبدیل به حروف بزرگ
    note_name = note_name.strip().upper()
    
    # تشخیص نت و اکتاو
    if len(note_name) < 2:
        return None
    
    note = note_name[0]
    if len(note_name) > 2 and note_name[1] in ['#', 'B']:
        note = note_name[:2]
        octave_str = note_name[2:]
    else:
        octave_str = note_name[1:]
    
    # تبدیل B به b برای flat
    if note == 'B' and len(note_name) > 1 and note_name[1] == 'B':
        note = 'Bb'
        octave_str = note_name[2:] if len(note_name) > 2 else ''
    
    if note not in MIDI_NOTES:
        return None
    
    try:
        octave = int(octave_str)
        midi_number = (octave + 1) * 12 + MIDI_NOTES[note]
        return midi_number
    except ValueError:
        return None


def is_white_key(midi_number: int) -> bool:
    """بررسی اینکه آیا کلاویه سفید است"""
    from .constants import NOTE_NAMES, WHITE_KEYS_PER_OCTAVE
    note_name = NOTE_NAMES[midi_number % 12]
    return note_name in WHITE_KEYS_PER_OCTAVE


def clamp(value: float, min_val: float, max_val: float) -> float:
    """محدود کردن مقدار بین min و max"""
    return max(min_val, min(value, max_val))





