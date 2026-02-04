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
  
