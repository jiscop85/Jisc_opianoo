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
                    # تبدیل ticks به ثانیه
            ticks_per_beat = mid.ticks_per_beat
            tempo = 500000  # microseconds per beat (default 120 BPM)
            
            current_time = 0.0
            track_notes = []
            
            # پردازش تمام track‌ها
            for track in mid.tracks:
                current_time = 0.0
                for msg in track:
                    # به‌روزرسانی زمان
                    delta_seconds = mido.tick2second(
                        msg.time,
                        ticks_per_beat,
                        tempo
                    )
                    current_time += delta_seconds
                    
                    # به‌روزرسانی tempo
                    if msg.type == 'set_tempo':
                        tempo = msg.tempo
                    
                    # پردازش note on
                    if msg.type == 'note_on' and msg.velocity > 0:
                        # پیدا کردن note off مربوطه
                        duration = self._find_note_off_duration(track, msg, current_time, ticks_per_beat, tempo)
                        
                        lesson_note = LessonNote(
                            midi_note=msg.note,
                            start_time=current_time,
                            duration=duration,
                            velocity=msg.velocity
                        )
                        track_notes.append(lesson_note)
            
            # مرتب‌سازی بر اساس زمان
            self.lesson_notes = sorted(track_notes, key=lambda n: n.start_time)
            self.stats['total_notes'] = len(self.lesson_notes)
            
            logger.info(f"Loaded {len(self.lesson_notes)} notes from {self.midi_file_path}")
            
        except Exception as e:
            logger.error(f"Error loading MIDI file: {e}")
            self.lesson_notes = []
    
    def _find_note_off_duration(
        self,
        track,
        note_on_msg,
        start_time: float,
        ticks_per_beat: int,
        tempo: int
    ) -> float:
        """پیدا کردن مدت زمان نت با جستجوی note off"""
        current_time = start_time
        for msg in track:
            if msg == note_on_msg:
                continue
            
            delta_seconds = mido.tick2second(msg.time, ticks_per_beat, tempo)
            current_time += delta_seconds
            
            if (msg.type == 'note_off' or
                (msg.type == 'note_on' and msg.velocity == 0)):
                if msg.note == note_on_msg.note:
                    return current_time - start_time
        
        # اگر note off پیدا نشد، مدت زمان پیش‌فرض
        return 0.5
    
    def start_lesson(self):
        """شروع درس"""
        self.lesson_start_time = time.time()
        self.current_note_index = 0
        self.played_notes = []
        self.is_playing = True
        self.is_paused = False
        
        # ریست آمار
        self.stats = {
            'total_notes': len(self.lesson_notes),
            'correct_notes': 0,
            'wrong_notes': 0,
            'missed_notes': 0,
            'extra_notes': 0
        }
        
        # ریست وضعیت نت‌ها
        for note in self.lesson_notes:
            note.status = NoteStatus.PENDING
        
        # ریست زمان توقف
        self.total_pause_time = 0.0
        self.pause_start_time = None
        
        logger.info("Lesson started")
    
    def pause_lesson(self):
        """توقف موقت درس"""
        if not self.is_paused:
            self.is_paused = True
            self.pause_start_time = time.time()
            logger.info("Lesson paused")
    
    def resume_lesson(self):
        """ادامه درس"""
        if self.is_paused and self.pause_start_time:
            # محاسبه زمان توقف
            pause_duration = time.time() - self.pause_start_time
            self.total_pause_time += pause_duration
            self.pause_start_time = None
            self.is_paused = False
            logger.info("Lesson resumed")
    
    def stop_lesson(self):
        """توقف درس"""
        self.is_playing = False
        self.is_paused = False
        
        # بررسی نت‌های از دست رفته
        self._check_missed_notes()
        
        logger.info("Lesson stopped")
    
    def get_current_time(self) -> float:
        """دریافت زمان فعلی در درس (ثانیه)"""
        if not self.lesson_start_time:
            return 0.0
        
        if self.is_paused:
            # زمان قبل از pause
            if self.pause_start_time:
                return (self.pause_start_time - self.lesson_start_time) - self.total_pause_time
            return (time.time() - self.lesson_start_time) - self.total_pause_time
        
        return (time.time() - self.lesson_start_time) - self.total_pause_time
    
    def register_played_note(
        self,
        midi_note: int,
        velocity: int = 100,
        finger: Optional[int] = None,
        expected_finger: Optional[int] = None
    ):
        """
        ثبت یک نت که توسط کاربر نواخته شده
        
        Args:
            midi_note: شماره MIDI نت نواخته شده
            velocity: شدت صدا
            finger: شماره انگشت استفاده شده (1-5)
            expected_finger: شماره انگشت مورد انتظار (1-5)
        
        Returns:
            Tuple[bool, str, Dict]: (success, message, details)
        """
        if not self.is_playing or self.is_paused:
            return False, "Lesson is not active", {}
        
        current_time = self.get_current_time()
        
        played_note = PlayedNote(
            midi_note=midi_note,
            timestamp=current_time,
            velocity=velocity
        )
        self.played_notes.append(played_note)
 
