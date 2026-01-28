"""
پنجره اصلی برنامه
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QMessageBox, QStatusBar, QSplitter, QFrame
)
from PyQt6.QtCore import Qt, Signal, QTimer
from PyQt6.QtGui import QIcon
import numpy as np
from typing import Optional
import config

from .auth_dialog import AuthDialog
from .piano_widget import PianoWidget
from .webcam_view import WebcamView
from .sheet_music_view import SheetMusicView
from .lesson_selector import LessonSelector
from .report_dialog import ReportDialog

from ..core.hand_tracker import HandTracker
from ..core.audio_engine import AudioEngine
from ..core.lesson_engine import LessonEngine
from ..core.metronome import Metronome
from ..core.calibration import CalibrationDialog
from ..core.posture_detector import PostureDetector
from ..core.session_recorder import SessionRecorder

from ..data.user_manager import UserManager
from ..data.models import User
from ..data.gamification import GamificationManager

from ..gui.theme_manager import ThemeManager
from ..gui.dashboard_widget import DashboardWidget

from ..utils.logger import logger



class MainWindow(QMainWindow):
    """پنجره اصلی"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Piano Master Tutor")
        self.setGeometry(100, 100, config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
        
        # کاربر فعلی
        self.current_user: Optional[User] = None
        self.user_manager = UserManager()
        
        # کامپوننت‌های اصلی
        self.hand_tracker: Optional[HandTracker] = None
        self.audio_engine: Optional[AudioEngine] = None
        self.lesson_engine: Optional[LessonEngine] = None
        self.metronome: Optional[Metronome] = None
        self.posture_detector = PostureDetector()
        self.session_recorder: Optional[SessionRecorder] = None
        self.gamification = GamificationManager()
        self.theme_manager = ThemeManager()
        
        # UI components
        self.piano_widget: Optional[PianoWidget] = None
        self.webcam_view: Optional[WebcamView] = None
        self.sheet_music_view: Optional[SheetMusicView] = None
        self.lesson_selector: Optional[LessonSelector] = None
        self.dashboard_widget: Optional[DashboardWidget] = None
        
        # وضعیت
        self.is_lesson_active = False
        self.is_recording = False
        self.calibration_points: Optional[np.ndarray] = None
        
        # اعمال تم
        self.apply_theme()
        
        self.setup_ui()
        self.setup_audio()
        self.show_auth_dialog()
    
    def setup_ui(self):
        """راه‌اندازی رابط کاربری"""
        central_widget = QWidget()
        main_layout = QHBoxLayout()
        
        # Splitter برای تقسیم صفحه
        splitter = QSplitter(Qt.Horizontal)
        
        # پنل چپ: انتخاب درس و کنترل‌ها
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # پنل وسط: پیانو و وبکم
        center_panel = self.create_center_panel()
        splitter.addWidget(center_panel)
        
        # پنل راست: نت‌های موسیقی
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
    
