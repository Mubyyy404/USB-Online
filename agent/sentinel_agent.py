import time
import wmi
import requests
import datetime

# 🔴 REPLACE
FIREBASE_PROJECT_ID = "cybermonitor-1ab3c"
COLLECTION = "usb_logs"
USER_EMAIL = "USER_EMAIL_HERE"  # auto-fill later

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
    requests.post(url, json=payload)

c = wmi.WMI()
watcher = c.Win32_USBHub.watch_for("creation")

print("USB Sentinel Running...")

while True:
    usb = watcher()
    info = {
        "user": USER_EMAIL,
        "device": usb.Name or "Unknown",
        "serial": usb.DeviceID,
        "action": "Inserted",
        "time": str(datetime.datetime.now())
    }
    send_to_firebase(info)
    time.sleep(1)
