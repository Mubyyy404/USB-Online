import usb.core
import usb.util
import time
import platform
import firebase_admin
from firebase_admin import credentials, firestore

# =====================================================
# 🔐 SET USER UID (from dashboard)
# =====================================================
USER_UID = "PUT_USER_UID_HERE"

# =====================================================
# 🔥 FIREBASE SETUP
# =====================================================
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

MACHINE_NAME = platform.node()

# whitelist names
WHITELIST = [
    "SanDisk Ultra",
    "Logitech USB Receiver"
]

def send_heartbeat():
    db.collection("agents").document(USER_UID).set({
        "machine": MACHINE_NAME,
        "status": "ONLINE",
        "last_seen": int(time.time())
    })

def log_event(name, serial, action):
    entry = {
        "uid": USER_UID,
        "device_name": name or "UNKNOWN",
        "device_serial": serial or "UNKNOWN",
        "machine": MACHINE_NAME,
        "action": action,
        "rule": "Whitelist Policy" if action=="ALLOWED" else "Unknown Device Policy",
        "class": "USB Device",
        "severity": "LOW" if action=="ALLOWED" else "HIGH",
        "timestamp": int(time.time())
    }

    db.collection("logs").add(entry)
    print(entry)

def monitor_loop():
    last_devices = set()

    while True:
        send_heartbeat()

        devices = usb.core.find(find_all=True)
        current = set()

        for dev in devices:
            try:
                name = usb.util.get_string(dev, dev.iProduct)
                serial = usb.util.get_string(dev, dev.iSerialNumber)
            except:
                name = "UNKNOWN"
                serial = "UNKNOWN"

            key = (name, serial)
            current.add(key)

            if key not in last_devices:
                if name in WHITELIST:
                    log_event(name, serial, "ALLOWED")
                else:
                    log_event(name, serial, "BLOCKED")

        last_devices = current

        time.sleep(4)

if __name__ == "__main__":
    print("Agent running...")
    monitor_loop()
