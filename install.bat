@echo off
echo Installing Cyber USB Monitor...

py -m pip install --upgrade pip
py -m pip install pywin32 psutil pyusb firebase-admin

echo Starting agent...
start "" py monitor.py

echo Done.
pause
