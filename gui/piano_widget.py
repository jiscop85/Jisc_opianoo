"""
ویجت پیانو مجازی 88 کلاویه
"""
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, Signal
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush
from typing import Dict, Set
import config
from ..utils.helpers import calculate_key_position
from ..utils.constants import LOWEST_NOTE, HIGHEST_NOTE, TOTAL_KEYS

class PianoWidget(QWidget):
    """ویجت پیانو مجازی"""
    
    # سیگنال‌ها
    key_pressed = Signal(int)  # midi_note
    key_released = Signal(int)  # midi_note
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(1400, 200)
        
        # وضعیت کلاویه‌ها
        self.pressed_keys: Set[int] = set()
        self.highlighted_keys: Set[int] = set()  # برای نمایش نت‌های درس
        
        # محاسبه موقعیت کلاویه‌ها
        self.key_positions: Dict[int, tuple] = {}  # midi_note: (x, y, width, height)
        self._calculate_key_positions()
    
    def _calculate_key_positions(self):
        """محاسبه موقعیت تمام کلاویه‌ها"""
        white_key_width = 20
        black_key_width = 12
        white_key_height = 150
        black_key_height = 100
        
        white_key_count = 0
        
        for midi_note in range(LOWEST_NOTE, HIGHEST_NOTE + 1):
            if check_white_key(midi_note):
                x = white_key_count * white_key_width
                y = 0
                self.key_positions[midi_note] = (x, y, white_key_width, white_key_height)
                white_key_count += 1
            else:
                # کلید سیاه - قرار دادن بین کلیدهای سفید
                # پیدا کردن تعداد کلیدهای سفید قبل از این نت
                white_before = sum(1 for n in range(LOWEST_NOTE, midi_note) if check_white_key(n))
                x = white_before * white_key_width - black_key_width // 2
                y = 0
                self.key_positions[midi_note] = (x, y, black_key_width, black_key_height)
    
    def paintEvent(self, event):
        """رندر پیانو"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # پس‌زمینه
        painter.fillRect(self.rect(), QColor(240, 240, 240))
        
        # رسم کلیدهای سفید
        for midi_note in range(LOWEST_NOTE, HIGHEST_NOTE + 1):
            if check_white_key(midi_note):
                self._draw_key(painter, midi_note, is_white=True)
        
        # رسم کلیدهای سیاه
        for midi_note in range(LOWEST_NOTE, HIGHEST_NOTE + 1):
            if not check_white_key(midi_note):
                self._draw_key(painter, midi_note, is_white=False)
    
    def _draw_key(self, painter: QPainter, midi_note: int, is_white: bool):
        """رسم یک کلاویه"""
        if midi_note not in self.key_positions:
            return
        
        x, y, w, h = self.key_positions[midi_note]
        
   

