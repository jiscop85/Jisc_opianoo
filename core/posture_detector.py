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
        
        flat_count = 0
        for tip_idx, mcp_idx in zip(finger_tips, finger_mcps):
            if tip_idx >= len(landmarks) or mcp_idx >= len(landmarks):
                continue
            
            tip = landmarks[tip_idx]
            mcp = landmarks[mcp_idx]
            
            # اگر فاصله عمودی بین tip و mcp خیلی کم باشد، انگشت صاف است
            vertical_diff = abs(tip['y'] - mcp['y'])
            if vertical_diff < 0.05:  # threshold
                flat_count += 1
        
        # اگر بیشتر از 2 انگشت صاف باشند
        return flat_count >= 2
    
    def _check_hand_height(self, landmarks: List[Dict]) -> Dict:
        """بررسی ارتفاع دست"""
        wrist = landmarks[HAND_LANDMARKS['WRIST']]
        
        # محاسبه میانگین ارتفاع نوک انگشتان
        finger_tips = [
            HAND_LANDMARKS['INDEX_TIP'],
            HAND_LANDMARKS['MIDDLE_TIP'],
            HAND_LANDMARKS['RING_TIP'],
            HAND_LANDMARKS['PINKY_TIP']
        ]
        
        tip_y_positions = []
        for tip_idx in finger_tips:
            if tip_idx < len(landmarks):
                tip_y_positions.append(landmarks[tip_idx]['y'])
        
        if not tip_y_positions:
            return {'too_low': False, 'too_high': False}
        
        avg_tip_y = np.mean(tip_y_positions)
        wrist_y = wrist['y']
        
        # اگر مچ دست خیلی پایین‌تر از نوک انگشتان باشد
        height_diff = wrist_y - avg_tip_y
        too_low = height_diff > 0.15  # threshold
        
        return {'too_low': too_low, 'too_high': False}
    
    def _check_finger_spacing(self, landmarks: List[Dict]) -> Dict:
        """بررسی فاصله بین انگشتان"""
        mcp_positions = [
            (HAND_LANDMARKS['INDEX_MCP'], landmarks[HAND_LANDMARKS['INDEX_MCP']]),
            (HAND_LANDMARKS['MIDDLE_MCP'], landmarks[HAND_LANDMARKS['MIDDLE_MCP']]),
            (HAND_LANDMARKS['RING_MCP'], landmarks[HAND_LANDMARKS['RING_MCP']]),
            (HAND_LANDMARKS['PINKY_MCP'], landmarks[HAND_LANDMARKS['PINKY_MCP']])
        ]
        
        distances = []
        for i in range(len(mcp_positions) - 1):
            pos1 = mcp_positions[i][1]
            pos2 = mcp_positions[i + 1][1]
            dist = calculate_distance(
                (pos1['x'], pos1['y']),
                (pos2['x'], pos2['y'])
            )
            distances.append(dist)
        
        if not distances:
            return {'too_close': False, 'too_far': False}
        
