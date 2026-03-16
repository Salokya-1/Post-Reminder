@echo off
setlocal

if not exist venv (
  python -m venv venv
)

call venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt

pyinstaller --noconfirm --onefile --name PostReminderDesktop --add-data "templates;templates" --add-data "static;static" run_desktop.py

echo.
echo Build complete. EXE location:
echo dist\PostReminderDesktop.exe
pause
