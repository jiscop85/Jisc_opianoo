"""
ویجت پیانو مجازی 88 کلاویه
"""
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, Signal
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush
from typing import Dict, Set
import config
from ..utils.helpers import calculate_key_position
from ..utils.constants import LOWEST_NOTE, HIGHEST_NOTE, TOTAL_KEYS


