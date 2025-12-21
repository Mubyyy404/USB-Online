import time, requests, subprocess

SERVER = "http://127.0.0.1:5000/usb"

def get_usb():
    result = subprocess.check_output("wmic logicaldisk where drivetype=2 get deviceid",
                                     shell=True).decode()
    return result.strip()

old = ""

while True:
    current = get_usb()
    if current != old:
        requests.post(SERVER, json={
            "event": "USB_CHANGE",
            "device": current
        })
        old = current
    time.sleep(5)
