"""
دیالوگ لاگین و ثبت‌نام
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QTabWidget, QWidget
)
from PyQt6.QtCore import Qt
from ..data.user_manager import UserManager
from ..utils.logger import logger


