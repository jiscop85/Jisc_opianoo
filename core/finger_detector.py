"""
تشخیص انگشت استفاده شده برای فشردن کلاویه
"""
from typing import List, Tuple, Optional, Dict
import numpy as np
from ..utils.constants import HAND_LANDMARKS
from ..utils.helpers import calculate_distance
from ..utils.logger import logger


class FingerDetector:
    """تشخیص انگشت استفاده شده"""
    
    # نوک انگشتان در MediaPipe
    FINGER_TIPS = {
        'thumb': HAND_LANDMARKS['THUMB_TIP'],
        'index': HAND_LANDMARKS['INDEX_TIP'],
        'middle': HAND_LANDMARKS['MIDDLE_TIP'],
        'ring': HAND_LANDMARKS['RING_TIP'],
        'pinky': HAND_LANDMARKS['PINKY_TIP']
    }
    
    # مفاصل MCP برای تشخیص خمیدگی
    FINGER_MCP = {
        'index': HAND_LANDMARKS['INDEX_MCP'],
        'middle': HAND_LANDMARKS['MIDDLE_MCP'],
        'ring': HAND_LANDMARKS['RING_MCP'],
        'pinky': HAND_LANDMARKS['PINKY_MCP']
    }
    
    def __init__(self):
        self.finger_names = ['thumb', 'index', 'middle', 'ring', 'pinky']
    
    def detect_finger(
        self,
        landmarks: List[Dict],
        key_position: Tuple[float, float],
        key_size: Tuple[float, float] = (20, 150)
    ) -> Optional[Tuple[str, int]]:
        """
        تشخیص انگشت استفاده شده برای فشردن کلاویه
        
        Args:
            landmarks: لیست landmarks دست
            key_position: موقعیت کلاویه (x, y)
            key_size: اندازه کلاویه (width, height)
        
        Returns:
            Tuple[finger_name, finger_number] یا None
        """
        if not landmarks or len(landmarks) < 21:
            return None
        
        key_x, key_y = key_position
        key_w, key_h = key_size
        key_center = (key_x + key_w / 2, key_y + key_h / 2)
        
        # پیدا کردن نزدیک‌ترین نوک انگشت
        min_distance = float('inf')
        closest_finger = None
        
        for finger_name, tip_idx in self.FINGER_TIPS.items():
            if tip_idx >= len(landmarks):
                continue
            
            tip = landmarks[tip_idx]
            tip_pos = (tip['x'], tip['y'])
            
            # بررسی اینکه آیا نوک انگشت در محدوده کلاویه است
            if (key_x <= tip_pos[0] <= key_x + key_w and
                key_y <= tip_pos[1] <= key_y + key_h):
                
                distance = calculate_distance(tip_pos, key_center)
                
                if distance < min_distance:
                    min_distance = distance
                    closest_finger = finger_name
        
        if closest_finger:
            finger_number = {
                'thumb': 1,
                'index': 2,
                'middle': 3,
                'ring': 4,
                'pinky': 5
            }[closest_finger]
            return (closest_finger, finger_number)
        
        return None
    
    def is_finger_extended(
        self,
        landmarks: List[Dict],
        finger_name: str
    ) -> bool:
        """
        بررسی اینکه آیا انگشت باز (extended) است
        
        Args:
            landmarks: لیست landmarks دست
            finger_name: نام انگشت ('index', 'middle', 'ring', 'pinky')
        
        Returns:
            True اگر انگشت باز باشد
        """
        if finger_name not in self.FINGER_TIPS or finger_name == 'thumb':
            return False
        
        tip_idx = self.FINGER_TIPS[finger_name]
        mcp_idx = self.FINGER_MCP.get(finger_name)
        
        if tip_idx >= len(landmarks) or mcp_idx is None or mcp_idx >= len(landmarks):
            return False
        
        tip = landmarks[tip_idx]
        mcp = landmarks[mcp_idx]
        
        # اگر نوک انگشت بالاتر از MCP باشد، انگشت باز است
        return tip['y'] < mcp['y']
    
    def detect_all_fingers_on_keys(
        self,
        landmarks: List[Dict],
        piano_keys: Dict[int, Tuple[float, float, float, float]]
    ) -> List[Tuple[int, str, int]]:
        """
        تشخیص تمام انگشتانی که روی کلاویه‌ها هستند
        
        Returns:
            لیست (midi_note, finger_name, finger_number)
        """
        results = []
        
        for midi_note, (key_x, key_y, key_w, key_h) in piano_keys.items():
            finger_info = self.detect_finger(
                landmarks,
                (key_x, key_y),
                (key_w, key_h)
            )
            
            if finger_info:
                finger_name, finger_number = finger_info
                results.append((midi_note, finger_name, finger_number))
        
        return results



