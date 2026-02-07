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
    
    def record_hand_position(self, landmarks: List[Dict], hand_label: str):
        """ثبت موقعیت دست"""
        # فقط هر چند فریم یکبار ثبت می‌کنیم (برای کاهش حجم)
        if len(self.events) > 0:
            last_event = self.events[-1]
            if last_event['type'] == 'hand_position':
                # اگر کمتر از 0.1 ثانیه از آخرین ثبت گذشته، ثبت نکن
                if time.time() - (self.start_time or time.time()) - last_event['timestamp'] < 0.1:
                    return
        
        self.record_event('hand_position', {
            'landmarks': landmarks,
            'hand_label': hand_label
        })
    
    def save_recording(self, output_path: Optional[str] = None) -> str:
        """ذخیره ضبط"""
        if output_path is None:
            output_dir = Path(config.DATA_DIR) / "recordings"
            output_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = output_dir / f"session_{self.user_id}_{self.lesson_id}_{timestamp}.json"
        
        recording_data = {
            'user_id': self.user_id,
            'lesson_id': self.lesson_id,
            'start_time': self.start_time,
            'duration': self.events[-1]['timestamp'] if self.events else 0,
            'events': self.events
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(recording_data, f, indent=2)
        
        logger.info(f"Recording saved to {output_path}")
        return str(output_path)
    
    def load_recording(self, file_path: str) -> bool:
        """لود ضبط"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                recording_data = json.load(f)
            
            self.user_id = recording_data.get('user_id', 0)
            self.lesson_id = recording_data.get('lesson_id', 0)
            self.start_time = recording_data.get('start_time')
            self.events = recording_data.get('events', [])
            
            logger.info(f"Recording loaded from {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading recording: {e}")
            return False





