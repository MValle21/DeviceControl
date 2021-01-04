from typing import Dict

from core.device.abstract import Device
from core.utils.errors import IdError
from core.utils.singleton import singleton


@singleton
class DeviceManager:

    def __init__(self):
        self._devices: Dict[str, Device] = {}

    def new_device(self, config: dict) -> Device:
        device_class = config.get("device_class")
        device_type = config.get("device_type")
        if self._devices.get(config.get("device_id")) is not None:
            raise IdError("Device with given ID already exists")
        device = self.load_class(device_class, device_type)(config)
        self._devices[device.device_id] = device
        return device

    def remove_device(self, device_id: str):
        device = self._devices.pop(device_id)
        device.end()

    def get_device(self, device_id: str) -> Device:
        device = self._devices.get(device_id)
        if device is None:
            raise IdError("Device with given ID: %s was not found" % device_id)
        return device

    def end(self):
        for key in list(self._devices.keys()):
            self.remove_device(key)

    def ping(self) -> Dict[str, bool]:
        result = {}

        for key, device in self._devices.items():
            result[key] = device.test_connection()

        return result

    @staticmethod
    def load_class(device_class: str, device_type: str) -> Device.__class__:
        from custom.devices import classes
        return classes.get(device_class, {}).get(device_type)
