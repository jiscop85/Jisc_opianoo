"""
ویجت داشبورد برای نمایش آمار و دستاوردها
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar,
    QScrollArea, QFrame
)
from PyQt6.QtCore import Qt
from typing import Optional, Dict
from ..data.gamification import GamificationManager
from ..utils.logger import logger


class DashboardWidget(QWidget):
    """ویجت داشبورد"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.gamification = GamificationManager()
        self.user_id: Optional[int] = None
        self.setup_ui()
    
    def setup_ui(self):
        """راه‌اندازی رابط کاربری"""
        layout = QVBoxLayout()
        
        # عنوان
        title = QLabel("داشبورد")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMaximumHeight(300)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout()
        
        # آمار کاربر
        self.stats_label = QLabel("لطفاً وارد شوید")
        content_layout.addWidget(self.stats_label)
        
        # نوار پیشرفت سطح
        self.level_label = QLabel("سطح: -")
        content_layout.addWidget(self.level_label)
        
        self.level_progress = QProgressBar()
        self.level_progress.setVisible(False)
        content_layout.addWidget(self.level_progress)
        
        # امتیاز
        self.points_label = QLabel("امتیاز: -")
        content_layout.addWidget(self.points_label)
        
        # Streak
        self.streak_label = QLabel("Streak: -")
        content_layout.addWidget(self.streak_label)
        
    
