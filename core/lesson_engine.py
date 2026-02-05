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
        
        # پیدا کردن نزدیک‌ترین نت در درس
        result = self._match_note(played_note)
        
        details = {
            'finger_used': finger,
            'expected_finger': expected_finger,
            'finger_correct': (finger == expected_finger) if (finger and expected_finger) else None
        }
        
        if result[0]:
            logger.debug(f"Note matched: {midi_to_note_name(midi_note)}")
        else:
            logger.debug(f"Note not matched: {midi_to_note_name(midi_note)} - {result[1]}")
        
        return result[0], result[1], details
    
    def _match_note(self, played_note: PlayedNote) -> Tuple[bool, str]:
        """
        تطبیق نت نواخته شده با نت‌های درس
        
        Returns:
            Tuple[bool, str]: (matched, message)
        """
        current_time = played_note.timestamp
        
        # پیدا کردن نت‌های نزدیک در زمان
        candidates = []
        for i, lesson_note in enumerate(self.lesson_notes):
            time_diff = abs(lesson_note.start_time - current_time)
                      # بررسی تحمل زمانی
            if time_diff <= (config.TOLERANCE_MS / 1000.0):
                candidates.append((i, lesson_note, time_diff))
        
        if not candidates:
            # نت اضافی
            self.stats['extra_notes'] += 1
            return False, "Extra note"
        
        # انتخاب نزدیک‌ترین نت
        candidates.sort(key=lambda x: x[2])
        best_match_idx, best_match_note, _ = candidates[0]
        
        # بررسی تطابق نت
        note_diff = abs(best_match_note.midi_note - played_note.midi_note)
        
        if note_diff <= config.TOLERANCE_SEMITONE:
            # نت صحیح
            if best_match_note.status == NoteStatus.PENDING:
                best_match_note.status = NoteStatus.CORRECT
                self.stats['correct_notes'] += 1
                self.current_note_index = max(self.current_note_index, best_match_idx + 1)
                return True, "Correct"
            else:
                # این نت قبلاً نواخته شده
                return False, "Already played"
        else:
            # نت اشتباه
            best_match_note.status = NoteStatus.WRONG
            self.stats['wrong_notes'] += 1
            return False, f"Wrong note (expected {midi_to_note_name(best_match_note.midi_note)})"
    
    def _check_missed_notes(self):
        """بررسی نت‌های از دست رفته"""
        current_time = self.get_current_time()
        
        for note in self.lesson_notes:
            if note.status == NoteStatus.PENDING:
                # اگر زمان نت گذشته باشد
                if note.start_time < current_time - (config.TOLERANCE_MS / 1000.0):
                    note.status = NoteStatus.MISSED
                    self.stats['missed_notes'] += 1
    
    def get_next_notes(self, count: int = 5) -> List[LessonNote]:
        """دریافت نت‌های بعدی"""
        current_time = self.get_current_time()
        
        upcoming = []
        for note in self.lesson_notes:
            if note.start_time > current_time and len(upcoming) < count:
                upcoming.append(note)
        
        return upcoming
    
    def get_progress(self) -> Dict:
        """دریافت پیشرفت درس"""
        if self.stats['total_notes'] == 0:
            return {
                'accuracy': 0.0,
                'progress': 0.0,
                'stats': self.stats.copy()
            }
               accuracy = (self.stats['correct_notes'] / self.stats['total_notes']) * 100.0
        progress = (self.current_note_index / len(self.lesson_notes)) * 100.0
        
        return {
            'accuracy': accuracy,
            'progress': progress,
            'stats': self.stats.copy()
        }
    
    def get_error_logs(self) -> List[Dict]:
        """دریافت لاگ اشتباهات"""
        error_logs = []
        
        for note in self.lesson_notes:
            if note.status in [NoteStatus.WRONG, NoteStatus.MISSED]:
                error_logs.append({
                    'expected_note': note.midi_note,
                    'played_note': None,
                    'error_type': note.status.value,
                    'timestamp': note.start_time
                })
        
        # اضافه کردن نت‌های اضافی
        for played_note in self.played_notes:
            # بررسی اینکه آیا این نت تطبیق شده یا نه
            matched = False
            for lesson_note in self.lesson_notes:
                if (abs(lesson_note.start_time - played_note.timestamp) <= 
                    config.TOLERANCE_MS / 1000.0 and
                    abs(lesson_note.midi_note - played_note.midi_note) <= 
                    config.TOLERANCE_SEMITONE):
                    matched = True
                    break
            
            if not matched:
                error_logs.append({
                    'expected_note': None,
                    'played_note': played_note.midi_note,
                    'error_type': 'extra_note',
                    'timestamp': played_note.timestamp
                })
        
        return error_logs


    

 
  





