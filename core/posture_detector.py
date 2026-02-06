"""
تشخیص وضعیت دست (posture detection)
"""
from typing import List, Dict, Optional
import numpy as np
from ..utils.constants import HAND_LANDMARKS
from ..utils.helpers import calculate_distance
from ..utils.logger import logger


class PostureDetector:
    """تشخیص وضعیت دست"""
    
    def __init__(self):
        self.warnings = []
    
    def analyze_posture(
        self,
        landmarks: List[Dict],
        hand_label: str = "Unknown"
    ) -> Dict[str, any]:
        """
        تحلیل وضعیت دست
        
        Returns:
            دیکشنری شامل هشدارها و توصیه‌ها
        """
        if not landmarks or len(landmarks) < 21:
            return {'warnings': [], 'score': 100}
        
        warnings = []
        score = 100
        
        # 1. بررسی خمیدگی انگشتان (flat fingers)
        flat_fingers = self._check_flat_fingers(landmarks)
        if flat_fingers:
            warnings.append({
                'type': 'flat_fingers',
                'message': 'انگشتان شما خیلی صاف هستند. سعی کنید آنها را کمی خم کنید.',
                'severity': 'medium'
            })
            score -= 10
        
        # 2. بررسی ارتفاع دست (hand height)
        hand_height = self._check_hand_height(landmarks)
        if hand_height['too_low']:
            warnings.append({
                'type': 'hand_too_low',
                'message': 'دست شما خیلی پایین است. سعی کنید مچ دست را بالاتر نگه دارید.',
                'severity': 'medium'
            })
            score -= 5
        
        # 3. بررسی فاصله انگشتان (finger spacing)
        finger_spacing = self._check_finger_spacing(landmarks)
        if finger_spacing['too_close']:
            warnings.append({
                'type': 'fingers_too_close',
                'message': 'انگشتان شما خیلی به هم نزدیک هستند. سعی کنید فاصله مناسبی بین آنها حفظ کنید.',
                'severity': 'low'
            })
            score -= 5
        
        # 4. بررسی تنش دست (hand tension)
        tension = self._check_hand_tension(landmarks)
        if tension['too_tense']:
            warnings.append({
                'type': 'hand_too_tense',
                'message': 'دست شما خیلی سفت است. سعی کنید آرام باشید و دست را راحت نگه دارید.',
                'severity': 'high'
            })
            score -= 15
        
        return {
            'warnings': warnings,
            'score': max(0, score),
            'hand_label': hand_label
        }
    
    def _check_flat_fingers(self, landmarks: List[Dict]) -> bool:
        """بررسی اینکه آیا انگشتان خیلی صاف هستند"""
        # بررسی انگشتان index, middle, ring, pinky
        finger_tips = [
            HAND_LANDMARKS['INDEX_TIP'],
            HAND_LANDMARKS['MIDDLE_TIP'],
            HAND_LANDMARKS['RING_TIP'],
            HAND_LANDMARKS['PINKY_TIP']
        ]
        
        finger_mcps = [
            HAND_LANDMARKS['INDEX_MCP'],
            HAND_LANDMARKS['MIDDLE_MCP'],
            HAND_LANDMARKS['RING_MCP'],
            HAND_LANDMARKS['PINKY_MCP']
        ]
        
   
