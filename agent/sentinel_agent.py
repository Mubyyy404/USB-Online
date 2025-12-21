import os
import sys
import shutil
import ctypes
import time
import wmi
import requests
import datetime
import socket
import winreg
from pynput import keyboard

# ---------------- CONFIG ----------------
APP_NAME = "USB Sentinel"
STARTUP_PATH = os.path.join(os.environ['APPDATA'], "usb_sentinel.exe")
FIREBASE_PROJECT_ID = "cybermonitor-1ab3c"
COLLECTION = "usb_logs"

# ---------------- Self-copy & add to startup ----------------
def add_to_startup():
    try:
        if not os.path.exists(STARTUP_PATH):
            shutil.copy(sys.executable, STARTUP_PATH)
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r"Software\Microsoft\Windows\CurrentVersion\Run",
                             0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, STARTUP_PATH)
        winreg.CloseKey(key)
    except:
        pass

# ---------------- Hide console ----------------
def hide_console():
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

# ---------------- Utilities ----------------
def get_user():
    try:
        return socket.gethostname()
    except:
        return "unknown_user"

def send_to_firebase(data):
    url = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT_ID}/databases/(default)/documents/{COLLECTION}"
    payload = {
        "fields": {
            "user": {"stringValue": data["user"]},
            "device": {"stringValue": data["device"]},
            "serial": {"stringValue": data["serial"]},
            "action": {"stringValue": data["action"]},
            "time": {"stringValue": data["time"]}
        }
    }
    try:
        requests.post(url, json=payload)
    except:
        pass

# ---------------- USB Monitoring ----------------
def usb_monitor():
    c = wmi.WMI()
    watcher = c.Win32_USBHub.watch_for("creation")
    while True:
        try:
            usb = watcher()
            info = {
                "user": get_user(),
                "device": usb.Name or "Unknown USB",
                "serial": usb.DeviceID,
                "action": "Inserted",
                "time": str(datetime.datetime.now())
            }
            send_to_firebase(info)
            time.sleep(1)
        except:
            time.sleep(1)

# ---------------- BadUSB / High-speed typing ----------------
typed_chars = 0
start_time = time.time()

def on_press(key):
    global typed_chars, start_time
    typed_chars += 1
    elapsed = time.time() - start_time
    if elapsed < 1 and typed_chars >= 50:
        info = {
            "user": get_user(),
            "device": "Unknown HID",
            "serial": "HID",
            "action": "BadUSB detected",
            "time": str(datetime.datetime.now())
        }
        send_to_firebase(info)
        typed_chars = 0
        start_time = time.time()
    elif elapsed >= 1:
        typed_chars = 0
        start_time = time.time()

listener = keyboard.Listener(on_press=on_press)
listener.start()

# ---------------- Main ----------------
if __name__ == "__main__":
    hide_console()
    add_to_startup()
    usb_monitor()
