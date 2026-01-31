"""
مدیریت دیتابیس SQLAlchemy
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
import config
from .models import Base
from ..utils.logger import logger



class DatabaseManager:
    """مدیریت اتصال و session دیتابیس"""
    
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self._initialized = False
    
    def initialize(self):
        """راه‌اندازی دیتابیس"""
        if self._initialized:
            return
        
        try:
            # ایجاد engine
            self.engine = create_engine(
                config.DATABASE_URL,
                connect_args={"check_same_thread": False},  # برای SQLite
                echo=False  # True برای debug
            )
            
            # ایجاد session factory
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            # ایجاد جداول
            Base.metadata.create_all(bind=self.engine)
            
            self._initialized = True
            logger.info(f"Database initialized: {config.DATABASE_URL}")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    @contextmanager
    def get_session(self):
        """Context manager برای session دیتابیس"""
        if not self._initialized:
            self.initialize()
        
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    def get_session_direct(self) -> Session:
        """دریافت مستقیم session (بدون context manager)"""
        if not self._initialized:
            self.initialize()
        
        return self.SessionLocal()
    
    def close(self):
        """بستن اتصال دیتابیس"""
        if self.engine:
            self.engine.dispose()
            self._initialized = False
            logger.info("Database connection closed")


# Instance سراسری
db_manager = DatabaseManager()

