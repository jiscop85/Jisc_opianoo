"""
ضبط و پخش جلسه تمرین
"""
import json
import time
from typing import List, Dict, Optional
from pathlib import Path
from datetime import datetime
import config
from ..utils.logger import logger

class SessionRecorder:
    """ضبط کننده جلسه تمرین"""
    
    def __init__(self, user_id: int, lesson_id: int):
        self.user_id = user_id
        self.lesson_id = lesson_id
        self.recording = False
        self.events: List[Dict] = []
        self.start_time: Optional[float] = None
        self.video_frames: List = []  # برای ذخیره فریم‌های ویدیو (اگر نیاز باشد)
    
    def start_recording(self):
        """شروع ضبط"""
        self.recording = True
        self.start_time = time.time()
        self.events = []
        self.video_frames = []
        logger.info("Session recording started")
    
    def stop_recording(self):
        """توقف ضبط"""
        self.recording = False
        logger.info("Session recording stopped")
    
    def record_event(
        self,
        event_type: str,
        data: Dict,
        timestamp: Optional[float] = None
    ):
        """ثبت یک رویداد"""
        if not self.recording:
            return
        
        if timestamp is None:
            timestamp = time.time() - (self.start_time or time.time())
        
        event = {
            'type': event_type,
            'timestamp': timestamp,
            'data': data
        }
        
        self.events.append(event)
    
    def record_note_press(
        self,
        midi_note: int,
        expected_note: Optional[int],
        finger: Optional[int],
        correct: bool
    ):
        """ثبت فشردن کلاویه"""
        self.record_event('note_press', {
            'midi_note': midi_note,
            'expected_note': expected_note,
            'finger': finger,
            'correct': correct
        })
    
 

