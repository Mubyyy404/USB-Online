import wmi, time, requests

API = "http://127.0.0.1:5000/api/report"
c = wmi.WMI()
prev = set()

while True:
    devices = {d.PNPDeviceID for d in c.Win32_USBHub()}
    added = devices - prev
    removed = prev - devices

    for d in added:
        requests.post(API, json={"event":"USB_INSERT","data":d})

    for d in removed:
        requests.post(API, json={"event":"USB_REMOVE","data":d})

    prev = devices
    time.sleep(2)
