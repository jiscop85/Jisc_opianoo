@echo off
echo ====================================
echo Piano Master Tutor
echo ====================================
echo.

REM بررسی وجود Python
python --version >nul 2>&1
if errorlevel 1 (
    echo خطا: Python نصب نشده است!
    echo لطفاً Python 3.8 یا بالاتر را نصب کنید.
    pause
    exit /b 1
)

echo Python پیدا شد!
echo.

REM بررسی وجود محیط مجازی
if exist "venv\Scripts\activate.bat" (
    echo فعال کردن محیط مجازی...
    call venv\Scripts\activate.bat
) else (
    echo محیط مجازی پیدا نشد. استفاده از Python سیستم...
)

echo.
echo در حال اجرای برنامه...
echo.

python main.py

if errorlevel 1 (
    echo.
    echo خطا در اجرای برنامه!
    echo لطفاً وابستگی‌ها را نصب کنید:
    echo   pip install -r requirements.txt
    pause
)

