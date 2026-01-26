"""
نمایش زنده وبکم با overlay landmarks
"""
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap
import cv2
import numpy as np
from typing import Optional


class WebcamView(QWidget):
    """ویجت نمایش وبکم"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(640, 480)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet("border: 2px solid gray; background-color: black;")
        self.video_label.setText("در انتظار وبکم...")
        
        layout.addWidget(self.video_label)
        self.setLayout(layout)
    
    def update_frame(self, frame: np.ndarray):
        """به‌روزرسانی فریم"""
        if frame is None or frame.size == 0:
            return
        
        # تبدیل BGR به RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # تبدیل به QImage
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        
        # تبدیل به QPixmap و نمایش
        pixmap = QPixmap.fromImage(qt_image)
        
        # تغییر اندازه برای fit کردن در label
        scaled_pixmap = pixmap.scaled(
            self.video_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        
        self.video_label.setPixmap(scaled_pixmap)
    
    def clear(self):
        """پاک کردن نمایش"""
        self.video_label.clear()
        self.video_label.setText("در انتظار وبکم...")

