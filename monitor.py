import pyrebase
import time
import socket
import psutil
import wmi
from datetime import datetime

# ===================== FIREBASE CONFIG =====================
FIREBASE_CONFIG = {
    "apiKey": "AIzaSyCIY6AiBsGrq7wM0BBYGW2lM_0FLWjnH0k",
    "authDomain": "cybermonitor-1ab3c.firebaseapp.com",
    "projectId": "cybermonitor-1ab3c",
    "storageBucket": "cybermonitor-1ab3c.appspot.com",
    "messagingSenderId": "569408987884",
    "appId": "1:569408987884:web:0839eb7932c206fc157bc9",
    "databaseURL": ""  # Leave blank, Firestore uses REST through pyrebase
}

USER_EMAIL = "SAME_EMAIL_USED_IN_LOGIN"
USER_PASSWORD = "PASSWORD"
# ============================================================

firebase = pyrebase.initialize_app(FIREBASE_CONFIG)
auth = firebase.auth()
db = firebase.database()

print("\nLogging into Firebase user account...")
user = auth.sign_in_with_email_and_password(USER_EMAIL, USER_PASSWORD)
uid = user["localId"]

hostname = socket.gethostname()
w = wmi.WMI()

known_devices = set()

def get_usb_devices():
    devices = []
    for d in w.Win32_DiskDrive():
        if "USB" in str(d.InterfaceType):
            devices.append({
                "device_name": d.Model,
                "serial": getattr(d, "SerialNumber", "UNKNOWN"),
            })
    return devices

while True:
    try:
        usb_list = get_usb_devices()

        # detect newly attached
        current_serials = {d['serial'] for d in usb_list}
        new_devices = current_serials - known_devices
        known_devices.update(current_serials)

        status = {
            "online": True,
            "machine": hostname,
            "last_seen": int(time.time()),
            "active_user": psutil.users()[0].name if psutil.users() else "UNKNOWN",
            "usb_devices": usb_list
        }

        # update live agent status
        db.child("users").child(uid).child("status").set(status, user["idToken"])

        # log any new USB devices
        for dev in usb_list:
            if dev["serial"] in new_devices:
                log_entry = {
                    "device_serial": dev["serial"],
                    "device_name": dev["device_name"],
                    "machine": hostname,
                    "action": "CONNECTED",
                    "rule": "Detection Event",
                    "class": "Mass Storage",
                    "timestamp": int(time.time()),
                    "severity": "MEDIUM"
                }
                db.child("users").child(uid).child("logs").push(log_entry, user["idToken"])

        print("Heartbeat OK", datetime.now(), status)

        time.sleep(8)

    except Exception as e:
        print("Error:", e)
        time.sleep(5)
