# device_controller.py
import json
import tinytuya
import logging

def load_device_config():
    with open(r'C:\Users\admin\OneDrive - DePaul University\OOP\Desktop(1)\Python\python\Project\flask\RC control way\config.json', 'r') as file:
        return json.load(file)

def initialize_devices(device_config):
    devices = []
    for device in device_config['devices']:
        d = tinytuya.OutletDevice(
            dev_id=device['dev_id'],
            address=device['address'],
            local_key=device['local_key'],
            version=device['version']
        )
        devices.append(d)
    logging.info(f"Devices initialized: {len(devices)}")
    return devices
