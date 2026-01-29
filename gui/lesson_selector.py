"""
انتخابگر درس و نمایش پیشرفت
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QLabel,
    QPushButton, QListWidgetItem, QProgressBar
)
from PyQt6.QtCore import Qt, Signal
from pathlib import Path
import config
from ..data.database import db_manager
from ..data.models import Lesson
from ..utils.logger import logger


class LessonSelector(QWidget):
    """ویجت انتخاب درس"""
    
    # سیگنال‌ها
    lesson_selected = Signal(str)  # مسیر فایل MIDI
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_lessons()
    
    def setup_ui(self):
        """راه‌اندازی رابط کاربری"""
        layout = QVBoxLayout()
        
        # عنوان
        title = QLabel("انتخاب درس")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)
        
        # لیست درس‌ها
        self.lesson_list = QListWidget()
        self.lesson_list.itemDoubleClicked.connect(self.on_lesson_double_clicked)
        layout.addWidget(self.lesson_list)
        
        # اطلاعات درس انتخاب شده
        self.info_label = QLabel("هیچ درسی انتخاب نشده")
        layout.addWidget(self.info_label)
        
        # پیشرفت
        self.progress_label = QLabel("پیشرفت: -")
        layout.addWidget(self.progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # دکمه شروع
        self.start_button = QPushButton("شروع درس")
        self.start_button.setEnabled(False)
        self.start_button.clicked.connect(self.on_start_clicked)
        layout.addWidget(self.start_button)
        
        self.setLayout(layout)
    
    def load_lessons(self):
        """بارگذاری درس‌ها از پوشه‌ها"""
        self.lesson_list.clear()
        
        # بارگذاری از پوشه‌های difficulty
        difficulties = ['beginner', 'intermediate', 'advanced']
        
        for difficulty in difficulties:
            difficulty_path = config.MIDI_DIR / difficulty
            
            if not difficulty_path.exists():
                continue
            
