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
            
            # بارگذاری فایل‌های MIDI
            for midi_file in difficulty_path.glob("*.mid"):
                item = QListWidgetItem(f"[{difficulty.upper()}] {midi_file.stem}")
                item.setData(Qt.UserRole, str(midi_file))
                item.setData(Qt.UserRole + 1, difficulty)
                self.lesson_list.addItem(item)
        
        logger.info(f"Loaded {self.lesson_list.count()} lessons")
    
    def on_lesson_double_clicked(self, item: QListWidgetItem):
        """هندل کردن دابل کلیک روی درس"""
        self.start_lesson(item)
    
    def on_start_clicked(self):
        """هندل کردن کلیک روی دکمه شروع"""
        current_item = self.lesson_list.currentItem()
        if current_item:
            self.start_lesson(current_item)
    
    def start_lesson(self, item: QListWidgetItem):
        """شروع یک درس"""
        file_path = item.data(Qt.UserRole)
        if file_path:
            self.lesson_selected.emit(file_path)
    
    def get_selected_lesson(self) -> Optional[str]:
        """دریافت درس انتخاب شده"""
        current_item = self.lesson_list.currentItem()
        if current_item:
            return current_item.data(Qt.UserRole)
        return None
    
    def update_progress(self, user_id: int, lesson_path: str):
        """به‌روزرسانی پیشرفت کاربر"""
        # این می‌تواند از دیتابیس لود شود
        # در اینجا یک پیاده‌سازی ساده است
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)  # می‌توان از دیتابیس لود شود


