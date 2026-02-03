"""
Wizard کالیبراسیون برای perspective transform
"""
import cv2
import numpy as np
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QMessageBox
from PyQt6.QtCore import Qt, Signal
from PyQt6.QtGui import QImage, QPixmap
from typing import List, Tuple, Optional
import config
from ..utils.logger import logger


class CalibrationDialog(QDialog):
    """دیالوگ کالیبراسیون"""
    
    calibration_complete = Signal(np.ndarray)  # ارسال نقاط کالیبراسیون
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("کالیبراسیون")
        self.setModal(True)
        self.resize(800, 600)
        
        self.calibration_points = []
        self.current_frame = None
        self.cap = None
        
        self.setup_ui()
        self.start_camera()
    
    def setup_ui(self):
        """راه‌اندازی رابط کاربری"""
        layout = QVBoxLayout()
        
        # دستورالعمل
        instruction = QLabel(
            "لطفاً چهار نقطه گوشه کیبورد پیانو خود را به ترتیب مشخص کنید:\n"
            "1. نقطه بالا چپ\n"
            "2. نقطه بالا راست\n"
            "3. نقطه پایین راست\n"
            "4. نقطه پایین چپ"
        )
        instruction.setAlignment(Qt.AlignCenter)
        instruction.setWordWrap(True)
        layout.addWidget(instruction)
        
        # نمایش وبکم
        self.video_label = QLabel()
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet("border: 2px solid gray;")
        self.video_label.mousePressEvent = self.on_frame_clicked
        layout.addWidget(self.video_label)
        
        # دکمه‌ها
        button_layout = QVBoxLayout()
        
        self.reset_button = QPushButton("شروع مجدد")
        self.reset_button.clicked.connect(self.reset_points)
        button_layout.addWidget(self.reset_button)
        
        self.finish_button = QPushButton("اتمام کالیبراسیون")
        self.finish_button.clicked.connect(self.finish_calibration)
        self.finish_button.setEnabled(False)
        button_layout.addWidget(self.finish_button)
        
        self.cancel_button = QPushButton("لغو")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        # تایمر برای به‌روزرسانی فریم
        from PyQt6.QtCore import QTimer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # ~30 FPS
    
    def start_camera(self):
        """شروع وبکم"""
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                QMessageBox.critical(self, "خطا", "نمی‌توان وبکم را باز کرد")
                self.reject()
                return
            
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.WEBCAM_WIDTH)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.WEBCAM_HEIGHT)
            
        except Exception as e:
            logger.error(f"Error starting camera: {e}")
            QMessageBox.critical(self, "خطا", f"خطا در راه‌اندازی وبکم: {e}")
            self.reject()
    
    def update_frame(self):
        """به‌روزرسانی فریم وبکم"""
        if self.cap is None:
            return
        
        ret, frame = self.cap.read()
        if not ret:
            return
        
        # رسم نقاط کالیبراسیون
        display_frame = frame.copy()
        for i, point in enumerate(self.calibration_points):
            x, y = int(point[0]), int(point[1])
            cv2.circle(display_frame, (x, y), 10, (0, 255, 0), -1)
            cv2.putText(
                display_frame,
                str(i + 1),
                (x + 15, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )
        
        # رسم خطوط بین نقاط
        if len(self.calibration_points) >= 2:
            for i in range(len(self.calibration_points) - 1):
                pt1 = tuple(map(int, self.calibration_points[i]))
                pt2 = tuple(map(int, self.calibration_points[i + 1]))
                cv2.line(display_frame, pt1, pt2, (255, 0, 0), 2)
        
        # بستن مستطیل
        if len(self.calibration_points) == 4:
            pts = np.array(self.calibration_points, dtype=np.int32)
            cv2.polylines(display_frame, [pts], True, (0, 0, 255), 2)
        
        # تبدیل به QPixmap
        rgb_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        self.video_label.setPixmap(pixmap.scaled(
            self.video_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        ))
        
        self.current_frame = display_frame
    
    def on_frame_clicked(self, event):
        """هندل کردن کلیک روی فریم"""
        if len(self.calibration_points) >= 4:
            return
        
        # محاسبه موقعیت کلیک نسبت به label
        label_size = self.video_label.size()
        pixmap = self.video_label.pixmap()
        if pixmap is None:
            return
        
        pixmap_size = pixmap.size()
        
        # محاسبه offset برای centering
        offset_x = (label_size.width() - pixmap_size.width()) / 2
        offset_y = (label_size.height() - pixmap_size.height()) / 2
        
        # تبدیل مختصات
        click_x = event.pos().x() - offset_x
        click_y = event.pos().y() - offset_y
        
        # تبدیل به مختصات فریم اصلی
        scale_x = self.current_frame.shape[1] / pixmap_size.width()
        scale_y = self.current_frame.shape[0] / pixmap_size.height()
        
        frame_x = int(click_x * scale_x)
        frame_y = int(click_y * scale_y)
        
        # اضافه کردن نقطه
        self.calibration_points.append([frame_x, frame_y])
        
        # فعال کردن دکمه اتمام
        if len(self.calibration_points) == 4:
            self.finish_button.setEnabled(True)
    
    def reset_points(self):
        """شروع مجدد کالیبراسیون"""
        self.calibration_points = []
        self.finish_button.setEnabled(False)
    
    def finish_calibration(self):
        """اتمام کالیبراسیون"""
        if len(self.calibration_points) != 4:
            QMessageBox.warning(self, "خطا", "لطفاً هر چهار نقطه را مشخص کنید")
            return
        
        # تبدیل به numpy array
        points = np.array(self.calibration_points, dtype=np.float32)
        
        # بررسی اعتبار نقاط (نباید هم‌خط باشند)
        # این یک بررسی ساده است
        if self._validate_points(points):
            self.calibration_complete.emit(points)
            self.accept()
        else:
            QMessageBox.warning(
                self,
                "خطا",
                "نقاط انتخاب شده معتبر نیستند. لطفاً دوباره تلاش کنید."
            )
    
    def _validate_points(self, points: np.ndarray) -> bool:
        """بررسی اعتبار نقاط"""
        # بررسی اینکه نقاط یک مستطیل معقول تشکیل دهند
        # محاسبه مساحت
        area = cv2.contourArea(points)
        if area < 1000:  # حداقل مساحت
            return False
        
        return True
    
    def closeEvent(self, event):
        """بستن دیالوگ"""
        if self.cap:
            self.cap.release()
        if self.timer:
            self.timer.stop()
        event.accept()

