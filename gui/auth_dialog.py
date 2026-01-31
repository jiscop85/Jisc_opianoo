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
        

        # Password
        password_label = QLabel("رمز عبور:")
        self.login_password = QLineEdit()
        self.login_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(password_label)
        layout.addWidget(self.login_password)
        
        # دکمه لاگین
        login_button = QPushButton("ورود")
        login_button.clicked.connect(self.handle_login)
        layout.addWidget(login_button)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_register_tab(self) -> QWidget:
        """ایجاد تب ثبت‌نام"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Username
        username_label = QLabel("نام کاربری:")
        self.register_username = QLineEdit()
        layout.addWidget(username_label)
        layout.addWidget(self.register_username)
        
        # Email
        email_label = QLabel("ایمیل:")
        self.register_email = QLineEdit()
        layout.addWidget(email_label)
        layout.addWidget(self.register_email)
        
        # Password
        password_label = QLabel("رمز عبور:")
        self.register_password = QLineEdit()
        self.register_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(password_label)
        layout.addWidget(self.register_password)
        
        # Confirm Password
        confirm_label = QLabel("تکرار رمز عبور:")
        self.register_confirm = QLineEdit()
        self.register_confirm.setEchoMode(QLineEdit.Password)
        layout.addWidget(confirm_label)
        layout.addWidget(self.register_confirm)
        
        # دکمه ثبت‌نام
        register_button = QPushButton("ثبت‌نام")
        register_button.clicked.connect(self.handle_register)
        layout.addWidget(register_button)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def handle_login(self):
        """هندل کردن لاگین"""
        username = self.login_username.text().strip()
        password = self.login_password.text()
        
        if not username or not password:
            QMessageBox.warning(self, "خطا", "لطفاً تمام فیلدها را پر کنید")
            return
        
        user = self.user_manager.login_user(username, password)
        
        if user:
            self.current_user = user
            QMessageBox.information(self, "موفق", f"خوش آمدید {username}!")
            self.accept()
        else:
            QMessageBox.warning(self, "خطا", "نام کاربری یا رمز عبور اشتباه است")
    
 


