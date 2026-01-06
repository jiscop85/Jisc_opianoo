@echo off
echo ====================================
echo نصب وابستگی‌های Piano Master Tutor
echo ====================================
echo.

REM بررسی وجود Python
python --version >nul 2>&1
if errorlevel 1 (
    echo خطا: Python نصب نشده است!
    echo لطفاً Python 3.8 یا بالاتر را از python.org دانلود کنید.
    pause
    exit /b 1
)

echo Python پیدا شد!
python --version
echo.

REM ایجاد محیط مجازی (اگر وجود نداشته باشد)
if not exist "venv" (
    echo ایجاد محیط مجازی...
    python -m venv venv
    if errorlevel 1 (
        echo خطا در ایجاد محیط مجازی!
        pause
        exit /b 1
    )
    echo محیط مجازی ایجاد شد.
) else (
    echo محیط مجازی از قبل وجود دارد.
)

echo.
echo فعال کردن محیط مجازی...
call venv\Scripts\activate.bat

echo.
echo نصب وابستگی‌ها...
echo این ممکن است چند دقیقه طول بکشد...
echo.

pip install --upgrade pip
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo خطا در نصب وابستگی‌ها!
    echo لطفاً دستی نصب کنید:
    echo   pip install -r requirements.txt
    pause
    exit /b 1
)

echo.
echo ====================================
echo نصب با موفقیت انجام شد!
echo ====================================
echo.
echo حالا می‌توانید برنامه را با run.bat اجرا کنید.
echo.
pause

