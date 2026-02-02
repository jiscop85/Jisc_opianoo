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
try:
            with db_manager.get_session() as session:
                # بررسی تکراری نبودن username و email
                existing_user = session.query(User).filter(
                    (User.username == username) | (User.email == email)
                ).first()
                
                if existing_user:
                    logger.warning(f"User already exists: {username}")
                    return None
                
                # ایجاد کاربر جدید
                new_user = User(
                    username=username,
                    email=email,
                    password_hash=self._hash_password(password)
                )
                
                session.add(new_user)
                session.flush()  # برای دریافت ID
                
                logger.info(f"User registered: {username}")
                return new_user
                
        except Exception as e:
            logger.error(f"Error registering user: {e}")
            return None
    
    def login_user(self, username: str, password: str) -> Optional[User]:
        """
        لاگین کاربر
        
        Returns:
            User object در صورت موفقیت، None در صورت خطا
        """
        try:
            with db_manager.get_session() as session:
                user = session.query(User).filter(
                    User.username == username
                ).first()
                
                if not user:
                    logger.warning(f"User not found: {username}")
                    return None

# بررسی رمز عبور
                password_hash = self._hash_password(password)
                if user.password_hash != password_hash:
                    logger.warning(f"Invalid password for user: {username}")
                    return None
                
                # به‌روزرسانی last_login
                user.last_login = datetime.utcnow()
                session.commit()
                
                logger.info(f"User logged in: {username}")
                return user
                
        except Exception as e:
            logger.error(f"Error logging in user: {e}")
            return None
    
    def get_user_progress(self, user_id: int) -> List[Dict]:
        """
        دریافت پیشرفت کاربر در تمام درس‌ها
        
        Returns:
            لیست دیکشنری‌های پیشرفت
        """
        try:
            with db_manager.get_session() as session:
                progresses = session.query(LessonProgress).filter(
                    LessonProgress.user_id == user_id
                ).all()
                
                result = []
                for progress in progresses:
                    lesson = session.query(Lesson).filter(
                        Lesson.id == progress.lesson_id
                    ).first()
                    
                    result.append({
                        'lesson_id': progress.lesson_id,
                        'lesson_name': lesson.name if lesson else 'Unknown',
                        'difficulty': lesson.difficulty if lesson else 'unknown',
                        'accuracy': progress.accuracy,
                        'score': progress.score,
                        'attempts': progress.attempts,
                        'completed': progress.completed,
                        'best_time': progress.best_time,
                        'last_played': progress.last_played.isoformat() if progress.last_played else None
                    })
                
                return result
                
        except Exception as e:
            logger.error(f"Error getting user progress: {e}")
            return []
