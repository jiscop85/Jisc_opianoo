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
             # تعیین رنگ
        if midi_note in self.pressed_keys:
            color = QColor(*config.COLORS['white_key_pressed' if is_white else 'black_key_pressed'])
        elif midi_note in self.highlighted_keys:
            color = QColor(*config.COLORS['correct_note'])
        else:
            color = QColor(*config.COLORS['white_key' if is_white else 'black_key'])
        
        # رسم مستطیل
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(QColor(100, 100, 100), 1))
        painter.drawRect(x, y, w, h)
        
        # رسم نام نت (فقط برای کلیدهای سفید)
        if is_white and midi_note % 12 == 0:  # فقط C
            from ..utils.helpers import midi_to_note_name
            note_name = midi_to_note_name(midi_note)
            painter.setPen(QPen(QColor(0, 0, 0)))
            painter.drawText(x, h - 5, w, 20, Qt.AlignCenter, note_name)
    
    def mousePressEvent(self, event):
        """هندل کردن کلیک ماوس"""
        clicked_note = self._get_note_at_position(event.pos().x(), event.pos().y())
        if clicked_note:
            self.press_key(clicked_note)
    
    def mouseReleaseEvent(self, event):
        """هندل کردن رها کردن ماوس"""
        clicked_note = self._get_note_at_position(event.pos().x(), event.pos().y())
        if clicked_note:
            self.release_key(clicked_note)
    
    def _get_note_at_position(self, x: int, y: int) -> int:
        """پیدا کردن نت در موقعیت مشخص"""
        # اول کلیدهای سیاه را بررسی می‌کنیم (چون بالاتر هستند)
        for midi_note in range(HIGHEST_NOTE, LOWEST_NOTE - 1, -1):
            if not check_white_key(midi_note) and midi_note in self.key_positions:
                kx, ky, kw, kh = self.key_positions[midi_note]
                if kx <= x <= kx + kw and ky <= y <= ky + kh:
                    return midi_note
        
        # سپس کلیدهای سفید
        for midi_note in range(LOWEST_NOTE, HIGHEST_NOTE + 1):
            if check_white_key(midi_note) and midi_note in self.key_positions:
                kx, ky, kw, kh = self.key_positions[midi_note]
                if kx <= x <= kx + kw and ky <= y <= ky + kh:
                    return midi_note
        
        return None
    
    def press_key(self, midi_note: int):
        """فشردن یک کلاویه"""
        if midi_note not in self.pressed_keys:
            self.pressed_keys.add(midi_note)
            self.update()
            self.key_pressed.emit(midi_note)
    
    def release_key(self, midi_note: int):
        """رها کردن یک کلاویه"""
        if midi_note in self.pressed_keys:
            self.pressed_keys.remove(midi_note)
            self.update()
            self.key_released.emit(midi_note)
    
    def highlight_key(self, midi_note: int):
        """هایلایت کردن یک کلاویه"""
        if midi_note not in self.highlighted_keys:
            self.highlighted_keys.add(midi_note)
            self.update()
    
    def unhighlight_key(self, midi_note: int):
        """حذف هایلایت از یک کلاویه"""
        if midi_note in self.highlighted_keys:
            self.highlighted_keys.remove(midi_note)
            self.update()
    
    def clear_highlights(self):
        """پاک کردن تمام هایلایت‌ها"""
        self.highlighted_keys.clear()
        self.update()
    
    def get_key_positions(self) -> Dict[int, tuple]:
        """دریافت موقعیت تمام کلاویه‌ها"""
        return self.key_positions.copy()


   


