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
        
    
    # دستاوردها
        achievements_label = QLabel("دستاوردها:")
        achievements_label.setStyleSheet("font-weight: bold;")
        content_layout.addWidget(achievements_label)
        
        self.achievements_list = QLabel("هیچ دستاوردی دریافت نشده")
        self.achievements_list.setWordWrap(True)
        content_layout.addWidget(self.achievements_list)
        
        content_layout.addStretch()
        content_widget.setLayout(content_layout)
        scroll.setWidget(content_widget)
        
        layout.addWidget(scroll)
        self.setLayout(layout)
    
    def set_user(self, user_id: int):
        """تنظیم کاربر"""
        self.user_id = user_id
        self.update_dashboard()
    
    def update_dashboard(self):
        """به‌روزرسانی داشبورد"""
        if not self.user_id:
            return
        
        stats = self.gamification.get_user_stats(self.user_id)
        
        if not stats:
            self.stats_label.setText("هیچ آماری موجود نیست")
            return
        
        # نمایش آمار
        stats_text = f"""
        <b>آمار کلی:</b><br>
        درس‌های تکمیل شده: {stats['lessons_completed']}<br>
        زمان تمرین: {int(stats['practice_time'] // 60)} دقیقه<br>
        """
        self.stats_label.setText(stats_text)
        
        # نمایش سطح
        level = stats['level']
        experience = stats['experience']
        experience_for_next = (level * 1000) - experience
        progress = (experience % 1000) / 1000.0 * 100
        
        self.level_label.setText(f"سطح {level} | {experience_for_next} XP تا سطح بعدی")
        self.level_progress.setVisible(True)
        self.level_progress.setValue(int(progress))
        
        # نمایش امتیاز
        self.points_label.setText(f"امتیاز کل: {stats['total_points']}")
        
        # نمایش Streak
        self.streak_label.setText(
            f"Streak فعلی: {stats['current_streak']} روز | "
            f"رکورد: {stats['longest_streak']} روز"
        )
        
        # نمایش دستاوردها
        achievements_text = f"تعداد دستاوردها: {stats['achievements_count']}"
        self.achievements_list.setText(achievements_text)


