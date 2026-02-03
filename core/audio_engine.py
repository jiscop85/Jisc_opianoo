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

