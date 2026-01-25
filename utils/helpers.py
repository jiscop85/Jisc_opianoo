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


