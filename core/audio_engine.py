"""
موتور صوتی با FluidSynth برای پخش نت‌های پیانو
"""
import fluidsynth
import threading
import time
from typing import Dict, Optional
import config
from ..utils.logger import logger

class AudioEngine:
    """موتور صوتی با FluidSynth"""
    
    def __init__(self, soundfont_path: Optional[str] = None):
        self.soundfont_path = soundfont_path or config.SOUNDFONT_PATH
        self.fs = None
        self.sfont_id = None
        self.initialized = False
        
        # مدیریت note off
        self.active_notes: Dict[int, float] = {}  # midi_note: start_time
        self.note_off_thread = None
        self.running = False
    
    def initialize(self) -> bool:
        """راه‌اندازی FluidSynth"""
        try:
            self.fs = fluidsynth.Synth()
            self.fs.start(driver="directsound")  # Windows
            
            # بارگذاری SoundFont
            if self.soundfont_path and self._file_exists(self.soundfont_path):
                self.sfont_id = self.fs.sfload(self.soundfont_path)
                if self.sfont_id == -1:
                    logger.warning(f"Failed to load SoundFont: {self.soundfont_path}")
                    logger.warning("Continuing without SoundFont - using default sound")
                    self.sfont_id = None
            else:
                logger.warning(f"SoundFont not found: {self.soundfont_path}")
                logger.warning("Using default FluidSynth sound")
                self.sfont_id = None
            
            # انتخاب preset (پیانو) - فقط اگر SoundFont لود شده باشد
            if self.sfont_id is not None:
                self.fs.program_select(0, self.sfont_id, 0, 0)  # channel, sfont_id, bank, program
            
            self.initialized = True
            logger.info("Audio engine initialized")
            
            # شروع thread مدیریت note off
            self.running = True
            self.note_off_thread = threading.Thread(target=self._note_off_manager, daemon=True)
            self.note_off_thread.start()
            
            return True
            
        except Exception as e:
            logger.error(f"Error initializing audio engine: {e}")
            return False
    
    def _file_exists(self, path: str) -> bool:
        """بررسی وجود فایل"""
        import os
        return os.path.exists(path)
    
    def play_note(
        self,
        midi_note: int,
        velocity: int = 100,
        channel: int = 0,
        duration: Optional[float] = None
    ):
 
       """
        پخش یک نت
        
        Args:
            midi_note: شماره MIDI (0-127)
            velocity: شدت صدا (0-127)
            channel: کانال MIDI (0-15)
            duration: مدت زمان پخش (ثانیه). اگر None باشد، باید note_off صدا زده شود
        """
        if not self.initialized or self.fs is None:
            return
        
        try:
            # محدود کردن velocity
            velocity = max(0, min(127, velocity))
            
            # پخش نت
            self.fs.noteon(channel, midi_note, velocity)
            
            # ثبت زمان شروع
            self.active_notes[midi_note] = time.time()
            
            # اگر duration مشخص شده، note off را زمان‌بندی کن
            if duration is not None:
                threading.Timer(duration, self.note_off, args=[midi_note, channel]).start()
            
        except Exception as e:
            logger.error(f"Error playing note {midi_note}: {e}")
    
    def note_off(self, midi_note: int, channel: int = 0):
        """قطع یک نت"""
        if not self.initialized or self.fs is None:
            return
        
        try:
            self.fs.noteoff(channel, midi_note)
            if midi_note in self.active_notes:
                del self.active_notes[midi_note]
        except Exception as e:
            logger.error(f"Error stopping note {midi_note}: {e}")
    
    def _note_off_manager(self):
        """مدیریت خودکار note off برای نت‌های فعال"""
        while self.running:
            current_time = time.time()
            notes_to_remove = []
            
            for midi_note, start_time in self.active_notes.items():
                # اگر نت بیشتر از delay مشخص شده فعال باشد، آن را قطع کن
                if current_time - start_time > config.NOTE_OFF_DELAY:
                    self.note_off(midi_note)
                    notes_to_remove.append(midi_note)
            
            for note in notes_to_remove:
                if note in self.active_notes:
                    del self.active_notes[note]
            
            time.sleep(0.05)  # بررسی هر 50ms
    
    def stop_all_notes(self, channel: int = 0):
        """قطع تمام نت‌ها"""
        if not self.initialized or self.fs is None:
            return
        
        try:
            self.fs.all_notes_off(channel)
            self.active_notes.clear()
        except Exception as e:
            logger.error(f"Error stopping all notes: {e}")
    
    def set_volume(self, volume: float, channel: int = 0):
        """تنظیم حجم صدا (0.0 - 1.0)"""
        if not self.initialized or self.fs is None:
            return
        
        try:
            # تبدیل به مقدار MIDI (0-127)
            midi_volume = int(volume * 127)
            self.fs.cc(channel, 7, midi_volume)  # CC 7 = Volume
        except Exception as e:
            logger.error(f"Error setting volume: {e}")
    
    def close(self):
        """بستن موتور صوتی"""
        self.running = False
        if self.note_off_thread:
            self.note_off_thread.join(timeout=1.0)
        
        if self.fs:
            self.stop_all_notes()
            self.fs.delete()
            self.fs = None
        
        self.initialized = False
        logger.info("Audio engine closed")




