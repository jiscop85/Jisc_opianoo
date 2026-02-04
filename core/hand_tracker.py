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
     
   
        Returns:
            لیست دیکشنری‌ها با کلیدهای: x, y, z, visibility
        """
        result = []
        for landmark in landmarks.landmark:
            result.append({
                'x': landmark.x,
                'y': landmark.y,
                'z': landmark.z,
                'visibility': landmark.visibility
            })
        return result
    
    def transform_landmarks(
        self,
        landmarks: List[Dict],
        frame_width: int,
        frame_height: int
    ) -> List[Tuple[float, float]]:
        """
        تبدیل landmarks به مختصات صفحه پیانو (در صورت وجود کالیبراسیون)
        
        Returns:
            لیست tuple های (x, y) در مختصات صفحه پیانو
        """
        if self.calibration_points is None:
            # بدون کالیبراسیون، برگرداندن مختصات نرمال شده
            return [(lm['x'], lm['y']) for lm in landmarks]
        
        # تبدیل با perspective transform
        # نقاط مقصد برای صفحه پیانو (مستطیل کامل)
        dst_points = np.array([
            [0, 0],
            [config.WINDOW_WIDTH, 0],
            [config.WINDOW_WIDTH, config.WINDOW_HEIGHT],
            [0, config.WINDOW_HEIGHT]
        ], dtype=np.float32)
        
        transformed = []
        for lm in landmarks:
            # تبدیل از مختصات نرمال به پیکسل
            pixel_x = lm['x'] * frame_width
            pixel_y = lm['y'] * frame_height
            
            # اعمال perspective transform
            transformed_point = map_coordinates(
                (pixel_x, pixel_y),
                self.calibration_points,
                dst_points
            )
            
            transformed.append(transformed_point)
        
        return transformed
    
    def detect_pressed_keys(
        self,
        landmarks: List[Tuple[float, float]],
        piano_keys: Dict[int, Tuple[float, float, float, float]],  # midi_note: (x, y, width, height)
        raw_landmarks: Optional[List[Dict]] = None
    ) -> List[Tuple[int, Optional[int]]]:
        """
        تشخیص کلاویه‌های فشرده شده بر اساس موقعیت landmarks
        
        Args:
            landmarks: لیست موقعیت‌های انگشتان (x, y)
            piano_keys: دیکشنری کلاویه‌ها با موقعیت و اندازه
            raw_landmarks: لیست landmarks خام برای تشخیص انگشت
        
        Returns:
            لیست tuple های (midi_note, finger_number) - finger_number می‌تواند None باشد
        """
        pressed_keys = []
        
    

