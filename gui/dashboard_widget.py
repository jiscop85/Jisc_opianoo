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

