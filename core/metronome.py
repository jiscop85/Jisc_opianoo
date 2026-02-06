"""
مترونوم قابل تنظیم
"""
import time
import threading
from typing import Optional, Callable
import config
from ..utils.logger import logger


class Metronome:
    """مترونوم"""
    
    def __init__(self, tempo: int = None, beats_per_bar: int = None):
        self.tempo = tempo or config.DEFAULT_TEMPO
        self.beats_per_bar = beats_per_bar or config.METRONOME_BEATS_PER_BAR
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.callback: Optional[Callable[[int], None]] = None  # beat_number callback
        
        # برای صدا (می‌تواند با audio_engine یکپارچه شود)
        self.audio_engine = None
    
    def set_tempo(self, tempo: int):
        """تنظیم سرعت (BPM)"""
        self.tempo = max(30, min(300, tempo))  # محدود به 30-300 BPM
    
    def set_beats_per_bar(self, beats: int):
        """تنظیم تعداد ضرب در هر میزان"""
        self.beats_per_bar = max(1, beats)
    
    def set_callback(self, callback: Callable[[int], None]):
        """تنظیم callback برای هر ضرب"""
        self.callback = callback
    
    def set_audio_engine(self, audio_engine):
        """تنظیم audio engine برای پخش صدا"""
        self.audio_engine = audio_engine
    
    def start(self):
        """شروع مترونوم"""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        logger.info(f"Metronome started at {self.tempo} BPM")
    

    def stop(self):
        """توقف مترونوم"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
        logger.info("Metronome stopped")
    
    def _run(self):
        """Thread اصلی مترونوم"""
        beat_interval = 60.0 / self.tempo  # ثانیه بین هر ضرب
        beat_number = 0
        
        while self.running:
            start_time = time.time()
            
            # فراخوانی callback
            if self.callback:
                self.callback(beat_number)
            
            # پخش صدا (اگر audio engine تنظیم شده)
            if self.audio_engine:
                # ضرب اول (downbeat) با نت بالاتر
                if beat_number == 0:
                    # می‌توان از یک نت بالاتر استفاده کرد
                    pass  # می‌توان با audio_engine یک صدای tick پخش کرد
            
            beat_number = (beat_number + 1) % self.beats_per_bar
            
            # انتظار تا ضرب بعدی
            elapsed = time.time() - start_time
            sleep_time = max(0, beat_interval - elapsed)
            time.sleep(sleep_time)
    
    def is_running(self) -> bool:
        """بررسی اینکه مترونوم در حال اجرا است"""
        return self.running


