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

class AuthDialog(QDialog):
    """دیالوگ احراز هویت"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ورود / ثبت‌نام")
        self.setModal(True)
        self.resize(400, 300)
        
        self.user_manager = UserManager()
        self.current_user = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """راه‌اندازی رابط کاربری"""
        layout = QVBoxLayout()
        
        # Tab widget برای لاگین و ثبت‌نام
        tabs = QTabWidget()
        
        # Tab لاگین
        login_tab = self.create_login_tab()
        tabs.addTab(login_tab, "ورود")
        
        # Tab ثبت‌نام
        register_tab = self.create_register_tab()
        tabs.addTab(register_tab, "ثبت‌نام")
        
        layout.addWidget(tabs)
        self.setLayout(layout)
    
    def create_login_tab(self) -> QWidget:
        """ایجاد تب لاگین"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Username
        username_label = QLabel("نام کاربری:")
        self.login_username = QLineEdit()
        layout.addWidget(username_label)
        layout.addWidget(self.login_username)
        



