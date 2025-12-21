@echo off
echo Installing USB Sentinel...

python -m pip install --upgrade pip
pip install wmi requests pywin32

copy sentinel_agent.py "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"

echo Installation Complete
pause
