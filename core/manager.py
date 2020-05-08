from typing import Tuple, Optional

from core.data.command import Command
from core.data.manager import DataManager
from core.device.manager import DeviceManager
from core.log import Log
from core.task.manager import TaskManager
from core.utils.errors import IdError
from core.utils.singleton import singleton


@singleton
class AppManager:
    def __init__(self, taskManager: TaskManager, deviceManager: DeviceManager, dataManager: DataManager):
        self.taskManager = taskManager
        self.deviceManager = deviceManager
        self.dataManager = dataManager

    def register_device(self, config: dict) -> (bool, Optional[Exception], None):
        try:
            device = self.deviceManager.new_device(config)
        except (IdError, ModuleNotFoundError, AttributeError) as e:
            Log.error(e)
            return False, e, None

        return device is not None, None, None

    def end_device(self, device_id: str):
        try:
            self.deviceManager.remove_device(device_id)
            return True, None, None
        except AttributeError:
            exc = IdError("Connector with given ID: %s was not found" % device_id)
            Log.error(exc)
            return False, exc, None

    def command(self, device_id, command_id, args, source, priority=False):
        try:
            cmd = Command(device_id, command_id, eval(args), source)
            if priority:
                self.deviceManager.get_device(device_id).post_command(cmd, priority=1)
            else:
                self.deviceManager.get_device(device_id).post_command(cmd)
            return True, None, None
        except (IdError, AttributeError) as e:
            Log.error(e)
            return False, e, None

    def register_task(self, config):
        try:
            task = self.taskManager.create_task(config)
            task.start()
            return True, None, None
        except (IdError, TypeError) as e:
            Log.error(e)
            return False, e, None

    def end_task(self, task_id):
        try:
            self.taskManager.remove_task(task_id)
            return True, None, None
        except IdError as e:
            Log.error(e)
            return False, e, None

    def ping(self) -> Tuple[bool, Optional[Exception], dict]:
        return True, None, {
            "devices": self.deviceManager.ping(),
            "tasks": self.taskManager.ping()
        }

    def get_data(self, device_id, log_id=None, time=None):
        if log_id is not None:
            return True, None, self.dataManager.get_data_by_id(log_id, device_id)
        return True, None, self.dataManager.get_data_by_time(time, device_id)

    def end(self):
        self.deviceManager.end()
        self.taskManager.end()
        return True, None, None
