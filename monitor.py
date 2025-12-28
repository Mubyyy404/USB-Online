import usb.core
import usb.util
import platform
import time
import firebase_admin
from firebase_admin import credentials, firestore

UID = "USER_FIREBASE_UID_HERE"  # dynamically set for each user

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

WHITELIST = ["SanDisk Ultra", "Logitech USB Receiver"]

def get_machine():
    return platform.node()

def severity(action):
    return "HIGH" if action == "BLOCKED" else "LOW"

def log_event(name, serial, action, dev_class):
    data = {
        "uid": UID,
        "device_serial": serial,
        "device_name": name,
        "machine": get_machine(),
        "action": action,
        "rule": "Unknown Device Policy" if action=="BLOCKED" else "Allowed Device",
        "class": dev_class,
        "timestamp": int(time.time()),
        "severity": severity(action)
    }

    db.collection("logs").add(data)
    print(data)

while True:
    devices = usb.core.find(find_all=True)

    for d in devices:
        try:
            name = usb.util.get_string(d, d.iProduct)
            serial = usb.util.get_string(d, d.iSerialNumber)

            if name in WHITELIST:
                log_event(name, serial, "ALLOWED", "Mass Storage")
            else:
                log_event(name, serial, "BLOCKED", "Mass Storage")

        except Exception as e:
            pass

    time.sleep(5)
