fd"""
نمایش نت‌های موسیقی
"""
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QScrollArea
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor, QPen, QFont
from typing import List, Optional
from ..core.lesson_engine import LessonNote, NoteStatus
from ..utils.helpers import midi_to_note_name



