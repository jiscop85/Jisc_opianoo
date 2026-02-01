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


class GamificationManager:
    """مدیریت Gamification"""
    
    # تعریف دستاوردهای پیش‌فرض
    DEFAULT_ACHIEVEMENTS = [
        {
            'name': 'first_lesson',
            'description': 'اولین درس را تکمیل کردید',
            'points': 10,
            'condition_type': 'lesson_completed',
            'condition_value': 1
        },
        {
            'name': 'perfect_score',
            'description': 'یک درس را با دقت 100% تکمیل کردید',
            'points': 50,
            'condition_type': 'accuracy',
            'condition_value': 100.0
        },
        {
            'name': 'week_warrior',
            'description': '7 روز متوالی تمرین کردید',
            'points': 100,
            'condition_type': 'streak',
            'condition_value': 7
        },
        {
            'name': 'master_pianist',
            'description': '50 درس را تکمیل کردید',
            'points': 500,
            'condition_type': 'lesson_completed',
            'condition_value': 50
        },
        {
            'name': 'speed_demon',
            'description': 'یک درس را در زمان رکورد تکمیل کردید',
            'points': 75,
            'condition_type': 'best_time',
            'condition_value': 1  # 1 = هر زمان رکورد
        }
    ]
    
    def __init__(self):
        db_manager.initialize()
        self._initialize_achievements()
    
    def _initialize_achievements(self):
        """راه‌اندازی دستاوردهای پیش‌فرض"""
        try:
            with db_manager.get_session() as session:
                for ach_data in self.DEFAULT_ACHIEVEMENTS:
                    existing = session.query(Achievement).filter(
                        Achievement.name == ach_data['name']
                    ).first()
                    
                    if not existing:
                        achievement = Achievement(**ach_data)
                        session.add(achievement)
                        logger.info(f"Created achievement: {ach_data['name']}")
        except Exception as e:
            logger.error(f"Error initializing achievements: {e}")
    
    def add_points(self, user_id: int, points: int, reason: str = ""):
        """اضافه کردن امتیاز به کاربر"""
        try:
            with db_manager.get_session() as session:
                stats = session.query(UserStats).filter(
                    UserStats.user_id == user_id
                ).first()
                
                if not stats:
                    stats = UserStats(user_id=user_id)
                    session.add(stats)
                
                stats.total_points += points
                stats.experience += points
                
                # محاسبه سطح (هر 1000 experience = 1 level)
                new_level = (stats.experience // 1000) + 1
                if new_level > stats.level:
                    stats.level = new_level
                    logger.info(f"User {user_id} leveled up to {new_level}")
                
                session.commit()
                logger.info(f"Added {points} points to user {user_id}: {reason}")
                
        except Exception as e:
            logger.error(f"Error adding points: {e}")
    
    def check_achievements(self, user_id: int, stats_update: Dict):
        """بررسی و اعطای دستاوردها"""
        try:
            with db_manager.get_session() as session:
                # دریافت آمار کاربر
                user_stats = session.query(UserStats).filter(
                    UserStats.user_id == user_id
                ).first()
                
                if not user_stats:
                    user_stats = UserStats(user_id=user_id)
                    session.add(user_stats)
                
                # به‌روزرسانی آمار
                if 'lessons_completed' in stats_update:
                    user_stats.total_lessons_completed = stats_update['lessons_completed']
                
                if 'practice_time' in stats_update:
                    user_stats.total_practice_time += stats_update['practice_time']
                
                if 'streak' in stats_update:
                    user_stats.current_streak = stats_update['streak']
                    if stats_update['streak'] > user_stats.longest_streak:
                        user_stats.longest_streak = stats_update['streak']
                
                # بررسی دستاوردها
                achievements = session.query(Achievement).all()
                unlocked = []
                
                for achievement in achievements:
                    # بررسی اینکه آیا کاربر قبلاً این دستاورد را دریافت کرده
                    existing = session.query(UserAchievement).filter(
                        UserAchievement.user_id == user_id,
                        UserAchievement.achievement_id == achievement.id
                    ).first()
                    
                    if existing:
                        continue
                    
                    # بررسی شرط دستاورد
                    if self._check_achievement_condition(achievement, user_stats, stats_update):
                        # اعطای دستاورد
                        user_achievement = UserAchievement(
                            user_id=user_id,
                            achievement_id=achievement.id
                        )
                        session.add(user_achievement)
                        
                        # اضافه کردن امتیاز
                        self.add_points(user_id, achievement.points, f"Achievement: {achievement.name}")
                        
                        unlocked.append(achievement)
                        logger.info(f"User {user_id} unlocked achievement: {achievement.name}")
                
                session.commit()
                return unlocked
                
        except Exception as e:
            logger.error(f"Error checking achievements: {e}")
            return []
    
    def _check_achievement_condition(
        self,
        achievement: Achievement,
        user_stats: UserStats,
        stats_update: Dict
    ) -> bool:
        """بررسی شرط دستاورد"""
        condition_type = achievement.condition_type
        condition_value = achievement.condition_value
        
        if condition_type == 'lesson_completed':
            return user_stats.total_lessons_completed >= condition_value
        
        elif condition_type == 'accuracy':
            return stats_update.get('accuracy', 0) >= condition_value
        
        elif condition_type == 'streak':
            return user_stats.current_streak >= condition_value
        
        elif condition_type == 'best_time':
            return stats_update.get('is_best_time', False)
        
        return False
    
    def get_user_stats(self, user_id: int) -> Optional[Dict]:
        """دریافت آمار کاربر"""
        try:
            with db_manager.get_session() as session:
                stats = session.query(UserStats).filter(
                    UserStats.user_id == user_id
                ).first()
                
                if not stats:
                    return None
                
  


