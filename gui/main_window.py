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
