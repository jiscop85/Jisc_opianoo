"""
موتور مدیریت درس‌ها: مقایسه نت‌ها، تشخیص اشتباهات
"""
import mido
import time
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import config
from ..utils.helpers import midi_to_note_name
from ..utils.logger import logger


class NoteStatus(Enum):
    """وضعیت یک نت"""
    PENDING = "pending"
    CORRECT = "correct"
    WRONG = "wrong"
    MISSED = "missed"
    EXTRA = "extra"


@dataclass
class LessonNote:
    """یک نت در درس"""
    midi_note: int
    start_time: float  # زمان شروع در درس (ثانیه)
    duration: float  # مدت زمان (ثانیه)
    velocity: int
    status: NoteStatus = NoteStatus.PENDING


@dataclass
class PlayedNote:
    """یک نت که توسط کاربر نواخته شده"""
    midi_note: int
    timestamp: float  # زمان نواختن (ثانیه)
    velocity: int = 100


class LessonEngine:
    """موتور مدیریت درس"""
    
    def __init__(self, midi_file_path: str):
        self.midi_file_path = midi_file_path
        self.lesson_notes: List[LessonNote] = []
        self.played_notes: List[PlayedNote] = []
        self.current_note_index = 0
        self.lesson_start_time: Optional[float] = None
        self.is_playing = False
        self.is_paused = False
        self.pause_start_time: Optional[float] = None
        self.total_pause_time = 0.0
        
        # آمار
        self.stats = {
            'total_notes': 0,
            'correct_notes': 0,
            'wrong_notes': 0,
            'missed_notes': 0,
            'extra_notes': 0
        }
        
        self._load_midi_file()
    
    def _load_midi_file(self):
        """بارگذاری فایل MIDI"""
        try:
            mid = mido.MidiFile(self.midi_file_path)
            
    
