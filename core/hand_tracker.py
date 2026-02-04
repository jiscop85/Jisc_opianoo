"""
ردیابی دست با MediaPipe و OpenCV
"""
import cv2
import mediapipe as mp
import numpy as np
from PyQt6.QtCore import QThread, Signal
from typing import List, Tuple, Optional, Dict
import config
from ..utils.helpers import map_coordinates, calculate_distance
from ..utils.logger import logger
from .finger_detector import FingerDetector


class HandTracker(QThread):
    """Thread برای ردیابی دست با MediaPipe"""
    
    # سیگنال‌ها
    hands_detected = Signal(list)  # لیست دست‌های تشخیص داده شده
    frame_ready = Signal(np.ndarray)  # فریم پردازش شده برای نمایش
    
    def __init__(self, calibration_points: Optional[np.ndarray] = None):
        super().__init__()
        self.calibration_points = calibration_points
        self.running = False
        
        # راه‌اندازی MediaPipe
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=config.MEDIAPIPE_MAX_NUM_HANDS,
            min_detection_confidence=config.HAND_DETECTION_CONFIDENCE,
            min_tracking_confidence=config.HAND_TRACKING_CONFIDENCE,
            model_complexity=config.MEDIAPIPE_MODEL_COMPLEXITY
        )
        
        # Finger detector
        self.finger_detector = FingerDetector()
        
        # وبکم
        self.cap = None
        self.current_frame = None
    
    def start_tracking(self, camera_index: int = 0):
        """شروع ردیابی"""
        try:
            self.cap = cv2.VideoCapture(camera_index)
            if not self.cap.isOpened():
                logger.error("Failed to open camera")
                return False
            
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.WEBCAM_WIDTH)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.WEBCAM_HEIGHT)
            
            self.running = True
            self.start()
            logger.info("Hand tracking started")
            return True
            
        except Exception as e:
            logger.error(f"Error starting hand tracking: {e}")
            return False
    
    def stop_tracking(self):
        """توقف ردیابی"""
        self.running = False
        if self.cap:
            self.cap.release()
        self.hands.close()
        logger.info("Hand tracking stopped")
    
    def set_calibration_points(self, points: np.ndarray):
        """تنظیم نقاط کالیبراسیون"""
        self.calibration_points = points
    
    def get_hand_landmarks(self, landmarks) -> List[Dict]:
        """
        تبدیل landmarks MediaPipe به لیست دیکشنری
     
