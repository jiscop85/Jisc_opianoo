"""
پنجره اصلی برنامه
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QMessageBox, QStatusBar, QSplitter, QFrame
)
from PyQt6.QtCore import Qt, Signal, QTimer
from PyQt6.QtGui import QIcon
import numpy as np
from typing import Optional
import config

from .auth_dialog import AuthDialog
from .piano_widget import PianoWidget
from .webcam_view import WebcamView
from .sheet_music_view import SheetMusicView
from .lesson_selector import LessonSelector
from .report_dialog import ReportDialog

from ..core.hand_tracker import HandTracker
from ..core.audio_engine import AudioEngine
from ..core.lesson_engine import LessonEngine
from ..core.metronome import Metronome
from ..core.calibration import CalibrationDialog
from ..core.posture_detector import PostureDetector
from ..core.session_recorder import SessionRecorder

from ..data.user_manager import UserManager
from ..data.models import User
from ..data.gamification import GamificationManager

from ..gui.theme_manager import ThemeManager
from ..gui.dashboard_widget import DashboardWidget

from ..utils.logger import logger



class MainWindow(QMainWindow):
    """پنجره اصلی"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Piano Master Tutor")
        self.setGeometry(100, 100, config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
        
        # کاربر فعلی
        self.current_user: Optional[User] = None
        self.user_manager = UserManager()
        
        # کامپوننت‌های اصلی
        self.hand_tracker: Optional[HandTracker] = None
        self.audio_engine: Optional[AudioEngine] = None
        self.lesson_engine: Optional[LessonEngine] = None
        self.metronome: Optional[Metronome] = None
        self.posture_detector = PostureDetector()
        self.session_recorder: Optional[SessionRecorder] = None
        self.gamification = GamificationManager()
        self.theme_manager = ThemeManager()
        
        # UI components
        self.piano_widget: Optional[PianoWidget] = None
        self.webcam_view: Optional[WebcamView] = None
        self.sheet_music_view: Optional[SheetMusicView] = None
        self.lesson_selector: Optional[LessonSelector] = None
        self.dashboard_widget: Optional[DashboardWidget] = None
        
        # وضعیت
        self.is_lesson_active = False
        self.is_recording = False
        self.calibration_points: Optional[np.ndarray] = None
        
        # اعمال تم
        self.apply_theme()
        
        self.setup_ui()
        self.setup_audio()
        self.show_auth_dialog()
    
    def setup_ui(self):
        """راه‌اندازی رابط کاربری"""
        central_widget = QWidget()
        main_layout = QHBoxLayout()
        
        # Splitter برای تقسیم صفحه
        splitter = QSplitter(Qt.Horizontal)
        
        # پنل چپ: انتخاب درس و کنترل‌ها
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # پنل وسط: پیانو و وبکم
        center_panel = self.create_center_panel()
        splitter.addWidget(center_panel)
        
        # پنل راست: نت‌های موسیقی
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
    
    
        # تنظیم نسبت‌ها
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)
        splitter.setStretchFactor(2, 1)
        
        main_layout.addWidget(splitter)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
        # نوار وضعیت
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("آماده")
        
        # منو
        self.create_menu_bar()
    
    def create_left_panel(self) -> QWidget:
        """ایجاد پنل چپ"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Dashboard
        self.dashboard_widget = DashboardWidget()
        layout.addWidget(self.dashboard_widget)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)
        
        # انتخاب درس
        self.lesson_selector = LessonSelector()
        self.lesson_selector.lesson_selected.connect(self.on_lesson_selected)
        layout.addWidget(self.lesson_selector)
        
        # دکمه‌های کنترل
        control_layout = QVBoxLayout()
        
        self.calibration_button = QPushButton("کالیبراسیون")
        self.calibration_button.clicked.connect(self.show_calibration)
        control_layout.addWidget(self.calibration_button)
        
        self.record_button = QPushButton("🔴 ضبط")
        self.record_button.clicked.connect(self.toggle_recording)
        self.record_button.setEnabled(False)
        control_layout.addWidget(self.record_button)
        
        self.start_button = QPushButton("شروع درس")
        self.start_button.clicked.connect(self.start_lesson)
        self.start_button.setEnabled(False)
        control_layout.addWidget(self.start_button)
        
        self.pause_button = QPushButton("توقف")
        self.pause_button.clicked.connect(self.pause_lesson)
        self.pause_button.setEnabled(False)
        control_layout.addWidget(self.pause_button)
        
        self.stop_button = QPushButton("پایان")
        self.stop_button.clicked.connect(self.stop_lesson)
        self.stop_button.setEnabled(False)
        control_layout.addWidget(self.stop_button)
        
        layout.addLayout(control_layout)
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget

    
    def create_center_panel(self) -> QWidget:
        """ایجاد پنل مرکزی"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # وبکم
        self.webcam_view = WebcamView()
        layout.addWidget(self.webcam_view)
        
        # پیانو
        self.piano_widget = PianoWidget()
        self.piano_widget.key_pressed.connect(self.on_key_pressed)
        self.piano_widget.key_released.connect(self.on_key_released)
        layout.addWidget(self.piano_widget)
        
        widget.setLayout(layout)
        return widget
    
    def create_right_panel(self) -> QWidget:
        """ایجاد پنل راست"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # نمایش نت‌ها
        self.sheet_music_view = SheetMusicView()
        layout.addWidget(self.sheet_music_view)
        
        # آمار درس
        self.stats_label = QLabel("آمار: -")
        layout.addWidget(self.stats_label)
        
        widget.setLayout(layout)
        return widget
    
    def create_menu_bar(self):
        """ایجاد منو"""
        menubar = self.menuBar()
        
        # منوی فایل
        file_menu = menubar.addMenu("فایل")
        
        logout_action = file_menu.addAction("خروج")
        logout_action.triggered.connect(self.logout)
        
        exit_action = file_menu.addAction("خروج از برنامه")
        exit_action.triggered.connect(self.close)
        
        # منوی تنظیمات
        settings_menu = menubar.addMenu("تنظیمات")
        
        calibration_action = settings_menu.addAction("کالیبراسیون")
        calibration_action.triggered.connect(self.show_calibration)
        
        # منوی تم
        theme_menu = settings_menu.addMenu("تم")
        light_theme_action = theme_menu.addAction("روشن")
        light_theme_action.triggered.connect(lambda: self.change_theme('light'))
        dark_theme_action = theme_menu.addAction("تاریک")
        dark_theme_action.triggered.connect(lambda: self.change_theme('dark'))
        
        # منوی نمایش
        view_menu = menubar.addMenu("نمایش")
        dashboard_action = view_menu.addAction("داشبورد")
        dashboard_action.triggered.connect(self.show_dashboard)
    
    def setup_audio(self):
        """راه‌اندازی موتور صوتی"""
        try:
            self.audio_engine = AudioEngine()
            if not self.audio_engine.initialize():
                QMessageBox.warning(self, "هشدار", "موتور صوتی راه‌اندازی نشد. صدا در دسترس نیست.")
        except Exception as e:
            logger.error(f"Error setting up audio: {e}")
            QMessageBox.warning(self, "خطا", f"خطا در راه‌اندازی صدا: {e}")
    
    def show_auth_dialog(self):
        """نمایش دیالوگ احراز هویت"""
        dialog = AuthDialog(self)
        if dialog.exec() == AuthDialog.Accepted:
            self.current_user = dialog.get_user()
            self.statusBar.showMessage(f"کاربر: {self.current_user.username}")
            
            # به‌روزرسانی dashboard
            if self.dashboard_widget:
                self.dashboard_widget.set_user(self.current_user.id)
            
            # لود کالیبراسیون
            if self.current_user:
                calibration_points = self.user_manager.load_calibration(self.current_user.id)
                if calibration_points:
                    self.calibration_points = np.array(calibration_points, dtype=np.float32)
        else:
            # اگر کاربر لاگین نکرد، برنامه را ببند
            self.close()
       def show_calibration(self):
        """نمایش دیالوگ کالیبراسیون"""
        dialog = CalibrationDialog(self)
        dialog.calibration_complete.connect(self.on_calibration_complete)
        dialog.exec()
    
    def on_calibration_complete(self, points: np.ndarray):
        """هندل کردن تکمیل کالیبراسیون"""
        self.calibration_points = points
        
        # ذخیره در دیتابیس
        if self.current_user:
            points_list = points.tolist()
            self.user_manager.save_calibration(
                self.current_user.id,
                points_list
            )
        
        # به‌روزرسانی hand tracker
        if self.hand_tracker:
            self.hand_tracker.set_calibration_points(points)
        
        QMessageBox.information(self, "موفق", "کالیبراسیون با موفقیت انجام شد!")
    
    def on_lesson_selected(self, midi_file_path: str):
        """هندل کردن انتخاب درس"""
        try:
            self.lesson_engine = LessonEngine(midi_file_path)
            self.sheet_music_view.set_lesson_notes(self.lesson_engine.lesson_notes)
            self.start_button.setEnabled(True)
            self.statusBar.showMessage(f"درس انتخاب شد: {midi_file_path}")
        except Exception as e:
            logger.error(f"Error loading lesson: {e}")
            QMessageBox.critical(self, "خطا", f"خطا در بارگذاری درس: {e}")
    
    def start_lesson(self):
        """شروع درس"""
        if not self.lesson_engine:
            QMessageBox.warning(self, "هشدار", "لطفاً ابتدا یک درس انتخاب کنید")
            return
        
        if self.calibration_points is None:
            reply = QMessageBox.question(
                self,
                "کالیبراسیون",
                "کالیبراسیون انجام نشده است. آیا می‌خواهید ادامه دهید؟",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        
        # شروع hand tracking
        if not self.hand_tracker:
            self.hand_tracker = HandTracker(self.calibration_points)
            self.hand_tracker.frame_ready.connect(self.webcam_view.update_frame)
            self.hand_tracker.hands_detected.connect(self.on_hands_detected)
            self.hand_tracker.start_tracking()
        
        # شروع session recorder
        if self.current_user and self.lesson_engine:
            lesson_id = 1  # باید از دیتابیس لود شود
            self.session_recorder = SessionRecorder(self.current_user.id, lesson_id)
            if self.is_recording:
                self.session_recorder.start_recording()

         
        # شروع درس
        self.lesson_engine.start_lesson()
        self.is_lesson_active = True
        
        # فعال کردن دکمه ضبط
        self.record_button.setEnabled(True)
        
        # به‌روزرسانی UI
        self.start_button.setEnabled(False)
        self.pause_button.setEnabled(True)
        self.stop_button.setEnabled(True)
        
        # تایمر برای به‌روزرسانی آمار
        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self.update_stats)
        self.stats_timer.start(1000)  # هر ثانیه
        
        self.statusBar.showMessage("درس در حال اجرا...")
    
    def pause_lesson(self):
        """توقف موقت درس"""
        if self.lesson_engine:
            self.lesson_engine.pause_lesson()
            self.pause_button.setText("ادامه")
            self.pause_button.clicked.disconnect()
            self.pause_button.clicked.connect(self.resume_lesson)
            self.statusBar.showMessage("درس متوقف شده")
    
    def resume_lesson(self):
        """ادامه درس"""
        if self.lesson_engine:
            self.lesson_engine.resume_lesson()
            self.pause_button.setText("توقف")
            self.pause_button.clicked.disconnect()
            self.pause_button.clicked.connect(self.pause_lesson)
            self.statusBar.showMessage("درس در حال اجرا...")
    
    def stop_lesson(self):
        """پایان درس"""
        if self.lesson_engine:
            self.lesson_engine.stop_lesson()
            self.is_lesson_active = False
            
            # توقف تایمر
            if hasattr(self, 'stats_timer'):
                self.stats_timer.stop()
            
            # به‌روزرسانی UI
            self.start_button.setEnabled(True)
            self.pause_button.setEnabled(False)
            self.stop_button.setEnabled(False)
            self.pause_button.setText("توقف")
            self.pause_button.clicked.disconnect()
            self.pause_button.clicked.connect(self.pause_lesson)
            
            # توقف ضبط
            if self.session_recorder and self.is_recording:
                self.session_recorder.stop_recording()
                recording_path = self.session_recorder.save_recording()
                logger.info(f"Session recorded to: {recording_path}")
                self.is_recording = False
                self.record_button.setText("🔴 ضبط")
            
            # نمایش گزارش
            self.show_report()
            
            self.statusBar.showMessage("درس به پایان رسید")
    
    def on_hands_detected(self, hands: list):
        """هندل کردن تشخیص دست"""
        if not self.is_lesson_active or not self.lesson_engine:
            return
        
        # تشخیص کلاویه‌های فشرده شده
        piano_keys = self.piano_widget.get_key_positions()
        
        for hand in hands:
            landmarks = hand.get('landmarks', [])
            if landmarks:
                pressed_keys = self.hand_tracker.detect_pressed_keys(landmarks, piano_keys)
                
                for midi_note in pressed_keys:
                    self.on_key_pressed(midi_note)
    
    def on_key_pressed(self, midi_note: int, finger: Optional[int] = None):
        """هندل کردن فشردن کلاویه"""
        # پخش صدا
        if self.audio_engine:
            self.audio_engine.play_note(midi_note)
        
        # ثبت در session recorder
        if self.session_recorder and self.is_recording:
            expected_note = None
            if self.lesson_engine:
                # پیدا کردن نت مورد انتظار
                current_time = self.lesson_engine.get_current_time()
                for note in self.lesson_engine.lesson_notes:
                    if abs(note.start_time - current_time) < 0.5:
                        expected_note = note.midi_note
                        break
            
            correct = (expected_note == midi_note) if expected_note else False
            self.session_recorder.record_note_press(midi_note, expected_note, finger, correct)
        
        # ثبت در درس
        if self.lesson_engine and self.is_lesson_active:
            # پیدا کردن نت مورد انتظار برای finger detection
            expected_finger = None  # می‌توان از music21 یا hard-coded fingerings استفاده کرد
            
            success, message, details = self.lesson_engine.register_played_note(
                midi_note,
                finger=finger,
                expected_finger=expected_finger
            )
            
            # به‌روزرسانی نمایش
            if success:
                # پیدا کردن نت فعلی و به‌روزرسانی وضعیت
                current_index = self.lesson_engine.current_note_index
                if current_index > 0:
                    self.sheet_music_view.update_note_status(
                        current_index - 1,
                        self.lesson_engine.lesson_notes[current_index - 1].status
                    )
    
    def on_key_released(self, midi_note: int):
        """هندل کردن رها کردن کلاویه"""
        if self.audio_engine:
            self.audio_engine.note_off(midi_note)
    
    def update_stats(self):
        """به‌روزرسانی آمار"""
        if self.lesson_engine:
            progress = self.lesson_engine.get_progress()
            stats_text = (
                f"دقت: {progress['accuracy']:.1f}% | "
                f"پیشرفت: {progress['progress']:.1f}% | "
                f"صحیح: {progress['stats']['correct_notes']} | "
                f"اشتباه: {progress['stats']['wrong_notes']} | "
                f"از دست رفته: {progress['stats']['missed_notes']}"
            )
            self.stats_label.setText(stats_text)
    
    def show_report(self):
        """نمایش گزارش"""
        if not self.lesson_engine or not self.current_user:
            return
        
        error_logs = self.lesson_engine.get_error_logs()
        lesson_name = self.lesson_engine.midi_file_path.split('/')[-1]
        
        dialog = ReportDialog(error_logs, lesson_name, self)
        dialog.exec()
        
        # ذخیره پیشرفت در دیتابیس
        progress = self.lesson_engine.get_progress()
        stats = progress['stats']
        
        # پیدا کردن lesson_id از مسیر فایل
        # این یک پیاده‌سازی ساده است - می‌توان بهبود داد
        lesson_id = 1  # باید از دیتابیس لود شود
        
        self.user_manager.save_lesson_progress(
            self.current_user.id,
            lesson_id,
            stats['total_notes'],
            stats['correct_notes'],
            stats['wrong_notes'],
            stats['missed_notes'],
            self.lesson_engine.get_current_time(),
            error_logs
        )
    
    def logout(self):
        """خروج کاربر"""
        reply = QMessageBox.question(
            self,
            "خروج",
            "آیا مطمئن هستید که می‌خواهید خارج شوید؟",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.current_user = None
            self.show_auth_dialog()
    
    def toggle_recording(self):
        """تغییر وضعیت ضبط"""
        if not self.is_lesson_active:
            QMessageBox.warning(self, "هشدار", "ابتدا یک درس را شروع کنید")
            return
        
        if not self.session_recorder:
            QMessageBox.warning(self, "هشدار", "Session recorder راه‌اندازی نشده")
            return
        
        if self.is_recording:
            self.session_recorder.stop_recording()
            self.is_recording = False
            self.record_button.setText("🔴 ضبط")
            self.statusBar.showMessage("ضبط متوقف شد")
        else:
            self.session_recorder.start_recording()
            self.is_recording = True
            self.record_button.setText("⏹ توقف ضبط")
            self.statusBar.showMessage("ضبط شروع شد")
    
    def change_theme(self, theme_name: str):
        """تغییر تم"""
        self.theme_manager.set_theme(theme_name)
        self.apply_theme()
        QMessageBox.information(self, "تم", f"تم به {theme_name} تغییر کرد")
    
    def apply_theme(self):
        """اعمال تم فعلی"""
        stylesheet = self.theme_manager.get_stylesheet()
        self.setStyleSheet(stylesheet)
    
    def show_dashboard(self):
        """نمایش داشبورد"""
        if self.dashboard_widget:
            self.dashboard_widget.update_dashboard()
            QMessageBox.information(self, "داشبورد", "داشبورد به‌روزرسانی شد")
    
    def closeEvent(self, event):
        """هندل کردن بستن پنجره"""
        # توقف کامپوننت‌ها
        if self.hand_tracker:
            self.hand_tracker.stop_tracking()
        
        if self.audio_engine:
            self.audio_engine.close()
        
        if self.metronome:
            self.metronome.stop()
        
        # ذخیره ضبط اگر در حال ضبط است
        if self.session_recorder and self.is_recording:
            self.session_recorder.stop_recording()
            self.session_recorder.save_recording()
        
        event.accept()





