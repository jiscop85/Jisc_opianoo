"""
نقطه ورود برنامه Piano Master Tutor
"""
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from src.gui.main_window import MainWindow
from src.utils.logger import logger

def main():
    """تابع اصلی"""
    # ایجاد application
    app = QApplication(sys.argv)
    app.setApplicationName("Piano Master Tutor")
    
    # تنظیمات کلی
    app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
    
    try:
        # ایجاد و نمایش پنجره اصلی
        window = MainWindow()
        window.show()
        
        logger.info("Application started")
        
        # اجرای event loop
        sys.exit(app.exec())
        
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()


