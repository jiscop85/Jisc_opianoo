"""
مدل‌های دیتابیس SQLAlchemy
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    """مدل کاربر"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # روابط
    lesson_progresses = relationship("LessonProgress", back_populates="user", cascade="all, delete-orphan")
    error_logs = relationship("ErrorLog", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"


class Lesson(Base):
    """مدل درس"""
    __tablename__ = 'lessons'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    file_path = Column(String(255), nullable=False)
    difficulty = Column(String(20), nullable=False)  # beginner, intermediate, advanced
    description = Column(Text, nullable=True)
    tempo = Column(Integer, default=120)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # روابط
    progresses = relationship("LessonProgress", back_populates="lesson", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Lesson(id={self.id}, name='{self.name}', difficulty='{self.difficulty}')>"


class LessonProgress(Base):
    """پیشرفت کاربر در یک درس"""
    __tablename__ = 'lesson_progress'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    lesson_id = Column(Integer, ForeignKey('lessons.id'), nullable=False)
    
    # آمار
    total_notes = Column(Integer, default=0)
    correct_notes = Column(Integer, default=0)
    wrong_notes = Column(Integer, default=0)
    missed_notes = Column(Integer, default=0)
    
    # امتیاز و دقت
    accuracy = Column(Float, default=0.0)  # درصد
    score = Column(Float, default=0.0)
    
    # زمان
    time_spent = Column(Float, default=0.0)  # ثانیه
    best_time = Column(Float, nullable=True)
    attempts = Column(Integer, default=0)
    
    # وضعیت
    completed = Column(Boolean, default=False)
    last_played = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # روابط
    user = relationship("User", back_populates="lesson_progresses")
    lesson = relationship("Lesson", back_populates="progresses")
    error_logs = relationship("ErrorLog", back_populates="lesson_progress", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<LessonProgress(id={self.id}, user_id={self.user_id}, lesson_id={self.lesson_id}, accuracy={self.accuracy}%)>"


class ErrorLog(Base):
    """لاگ اشتباهات کاربر"""
    __tablename__ = 'error_logs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    lesson_progress_id = Column(Integer, ForeignKey('lesson_progress.id'), nullable=True)
    
    # اطلاعات اشتباه
    expected_note = Column(Integer, nullable=False)  # MIDI note number
    played_note = Column(Integer, nullable=True)  # MIDI note number (None اگر missed)
    error_type = Column(String(20), nullable=False)  # wrong_note, missed_note, extra_note
    
    # زمان
    timestamp = Column(Float, nullable=False)  # زمان در درس (ثانیه)
    occurred_at = Column(DateTime, default=datetime.utcnow)
    
    # اطلاعات اضافی
    hand_position = Column(String(50), nullable=True)  # left, right, both
    finger_used = Column(Integer, nullable=True)  # 1-5
    
   
 # روابط
    user = relationship("User", back_populates="error_logs")
    lesson_progress = relationship("LessonProgress", back_populates="error_logs")
    
    def __repr__(self):
        return f"<ErrorLog(id={self.id}, error_type='{self.error_type}', expected={self.expected_note}, played={self.played_note})>"


class CalibrationData(Base):
    """داده‌های کالیبراسیون کاربر"""
    __tablename__ = 'calibration_data'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # نقاط کالیبراسیون (به صورت JSON string ذخیره می‌شود)
    calibration_points = Column(Text, nullable=False)  # JSON array of [x, y] points
    
    # تنظیمات
    webcam_width = Column(Integer, default=640)
    webcam_height = Column(Integer, default=480)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<CalibrationData(id={self.id}, user_id={self.user_id})>"



