"""
پنجره گزارش بعد از درس
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QScrollArea, QWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from pathlib import Path
from ..analysis.error_analyzer import ErrorAnalyzer
from ..analysis.report_generator import ReportGenerator
from ..utils.logger import logger





