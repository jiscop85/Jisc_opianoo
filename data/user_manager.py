""""" 

مدیریت کاربران :ثبت نام ، لاگین ، ذخیره/ لود پیشرفت
"""""

import hashlib
import json
from typing import Optional, Dict, List
from datetime import datetime
from sqlalchemy.orm import Session
from .database import db_manager
from .models import User, Lesson, LessonProgress, ErrorLog, CalibrationData
from ..utils.logger import logger



class UserManager:
    """مدیریت کاربران"""
    
    def __init__(self):
        db_manager.initialize()
    
    @staticmethod
    def _hash_password(password: str) -> str:
        """هش کردن رمز عبور"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(
        self,
        username: str,
        email: str,
        password: str
    ) -> Optional[User]:
        """
        ثبت‌نام کاربر جدید
        
        Returns:
            User object در صورت موفقیت، None در صورت خطا
        """
