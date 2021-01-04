from core.device.abstract import Device
from custom.devices.MettlerToledo.libs.Connection import Connection


class SICS(Device):
    def __init__(self, config: dict):
        super(SICS, self).__init__(config)
        self.connection = Connection(self.address, self.device_id)
        self.interpreter = {
            '1': self.get_weight,
            '2': self.get_info
        }

    def get_weight(self):
        """
        Get actual measured weight in set units.

        :return: Current weight value.
        """
        return {'weight': self.connection.get_weight()}

    def get_info(self):
        """
        Get sensor humidity (relative humidity in %).

        :return: Current humidity value.
        """
        return self.connection.get_info()

    def disconnect(self):
        self.connection.close()
        return True

    def test_connection(self) -> bool:
        try:
            self.connection.get_address()
            return True
        except Exception:
            return False
