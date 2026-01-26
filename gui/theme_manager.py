"""
مدیریت تم (روشن/تاریک)
"""
from PyQt6.QtCore import QSettings
from typing import Dict, Optional
import config
from ..utils.logger import logger


class ThemeManager:
    """مدیریت تم"""
    
    THEMES = {
        'light': {
            'name': 'روشن',
            'background': '#FFFFFF',
            'foreground': '#000000',
            'piano_white_key': '#FFFFFF',
            'piano_black_key': '#000000',
            'piano_white_key_pressed': '#E0E0FF',
            'piano_black_key_pressed': '#4040A0',
            'button': '#E0E0E0',
            'button_hover': '#D0D0D0',
            'text': '#000000',
            'accent': '#0078D4'
        },
        'dark': {
            'name': 'تاریک',
            'background': '#1E1E1E',
            'foreground': '#FFFFFF',
            'piano_white_key': '#F5F5F5',
            'piano_black_key': '#000000',
            'piano_white_key_pressed': '#4A4A8A',
            'piano_black_key_pressed': '#2A2A6A',
            'button': '#3C3C3C',
            'button_hover': '#4C4C4C',
            'text': '#FFFFFF',
            'accent': '#4A9EFF'
        }
    }
    
    def __init__(self):
        self.settings = QSettings('PianoMasterTutor', 'Theme')
        self.current_theme = self.settings.value('theme', 'light', type=str)
    
    def get_theme(self, theme_name: Optional[str] = None) -> Dict:
        """دریافت تم"""
        if theme_name is None:
            theme_name = self.current_theme
     

