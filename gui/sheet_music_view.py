fd"""
نمایش نت‌های موسیقی
"""
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QScrollArea
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor, QPen, QFont
from typing import List, Optional
from ..core.lesson_engine import LessonNote, NoteStatus
from ..utils.helpers import midi_to_note_name


class SheetMusicView(QWidget):
    """ویجت نمایش نت‌های موسیقی"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 300)
        
        layout = QVBoxLayout()
        
        self.title_label = QLabel("نت‌های موسیقی")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.title_label)
        
        # Scroll area برای نت‌ها
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self)
        
        self.lesson_notes: List[LessonNote] = []
        self.current_note_index = 0
    
    def set_lesson_notes(self, notes: List[LessonNote]):
        """تنظیم نت‌های درس"""
        self.lesson_notes = notes
        self.current_note_index = 0
        self.update()
    
    def set_current_note(self, index: int):
        """تنظیم نت فعلی"""
        self.current_note_index = index
        self.update()
    
    def paintEvent(self, event):
        """رندر نت‌ها"""
        if not self.lesson_notes:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # نمایش ساده نت‌ها به صورت لیست
        y_offset = 30
        x_offset = 20
        
        # نمایش 10 نت بعدی
        upcoming_notes = self.lesson_notes[self.current_note_index:self.current_note_index + 10]
        
        for i, note in enumerate(upcoming_notes):
            y = y_offset + i * 30
            
            # رنگ بر اساس وضعیت
            if note.status == NoteStatus.CORRECT:
                color = QColor(0, 255, 0)
            elif note.status == NoteStatus.WRONG:
                color = QColor(255, 0, 0)
            elif note.status == NoteStatus.MISSED:
                color = QColor(255, 165, 0)
            elif i == 0:  # نت فعلی
                color = QColor(0, 0, 255)
            else:
                color = QColor(0, 0, 0)
            
            painter.setPen(QPen(color, 2))
            
            # نام نت
            note_name = midi_to_note_name(note.midi_note)
            painter.drawText(x_offset, y, f"{note_name} ({note.start_time:.2f}s)")
            
            # نشانگر وضعیت
            status_text = {
                NoteStatus.PENDING: "⏳",
                NoteStatus.CORRECT: "✓",
                NoteStatus.WRONG: "✗",
                NoteStatus.MISSED: "○"
            }.get(note.status, "")
            
            painter.drawText(x_offset + 150, y, status_text)
    
    def update_note_status(self, note_index: int, status: NoteStatus):
        """به‌روزرسانی وضعیت یک نت"""
        if 0 <= note_index < len(self.lesson_notes):
            self.lesson_notes[note_index].status = status
            self.update()


