"""
سیستم Gamification: امتیاز، نشان، دستاورد
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import List, Dict, Optional
from ..data.models import Base
from ..data.database import db_manager
from ..utils.logger import logger



class Achievement(Base):
    """مدل دستاورد"""
    __tablename__ = 'achievements'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(255), nullable=False)
    icon = Column(String(100), nullable=True)  # نام آیکون
    points = Column(Integer, default=0)
    condition_type = Column(String(50), nullable=False)  # 'lesson_completed', 'accuracy', 'streak', etc.
    condition_value = Column(Float, nullable=False)  # مقدار شرط
    
    # روابط
    user_achievements = relationship("UserAchievement", back_populates="achievement")


class UserAchievement(Base):
    """دستاوردهای کاربر"""
    __tablename__ = 'user_achievements'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    achievement_id = Column(Integer, ForeignKey('achievements.id'), nullable=False)
    unlocked_at = Column(DateTime, default=datetime.utcnow)
    
    # روابط
    achievement = relationship("Achievement", back_populates="user_achievements")


class UserStats(Base):
    """آمار کاربر"""
    __tablename__ = 'user_stats'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True, nullable=False)
    
    # امتیاز و سطح
    total_points = Column(Integer, default=0)
    level = Column(Integer, default=1)
    experience = Column(Integer, default=0)
    
    # آمار کلی
    total_lessons_completed = Column(Integer, default=0)
    total_practice_time = Column(Float, default=0.0)  # ثانیه
    current_streak = Column(Integer, default=0)  # روزهای متوالی تمرین
    longest_streak = Column(Integer, default=0)
    last_practice_date = Column(DateTime, nullable=True)
    
    # به‌روزرسانی
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

