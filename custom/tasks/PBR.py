from collections import deque
from threading import Thread
from time import sleep

import numpy as np

from core.device.abstract import Connector
from core.data.command import Command
from core.device.manager import DeviceManager
from core.task.abstract import BaseTask
from core.task.manager import TaskManager
from core.utils.observable import Observable, Observer


class PBRMeasureAll(BaseTask):

    def __init__(self, config):

        # Task-specific attributes
        self.outliers = 0
        self.sleep_period = None
        self.lower_tol = None
        self.upper_tol = None
        self.od_channel = None
        self.tolerance = None
        self.max_outliers = None
        self.ft_channel = None
        self.latest_values = deque(maxlen=2)
        self.device_id: str = ""
        self.pump_id = None

        self.__dict__.update(config)
        self.device: Connector = DeviceManager().get_device(self.device_id)
        self.average_od = self.measure_initial_od_average()
        self.od = Observable()

        try:
            assert self.sleep_period is not None
            assert self.max_outliers is not None
            assert self.sleep_period is not None
            assert self.pump_id is not None
            assert self.lower_tol is not None
            assert self.upper_tol is not None
            assert self.od_channel is not None
            assert self.ft_channel is not None
            assert self.device_id is not ""

        except AssertionError:
            raise AttributeError("Configuration of PBRMeasureAll task must contain all required attributes")

        super(PBRMeasureAll, self).__init__()

    def get_od_for_init(self):
        cmd = Command(self.device_id, "5",
                      [self.od_channel],
                      self.task_id)

        self.device.post_command(cmd)
        cmd.await_cmd()
        if cmd.is_valid:
            return cmd.response

    def measure_initial_od_average(self):
        data = []
        # collect the OD value from 5 measurements
        while len(data) < 5:
            od = self.get_od_for_init()
            if od is not None:
                data.append(od)

        data.sort()
        computed = False
        average = 0

        # calculate the average OD from the measured data
        while not computed:

            mean = np.mean(data)
            median = np.median(data)

            if len(data) < 2:
                computed = True
                average = data[0]

            if mean / median <= 1:

                if mean / median >= 0.9:
                    computed = True
                    average = mean
                else:
                    data = data[1:]
            else:
                data = data[:-1]
        return average

    def handle_outlier(self, measured_od) -> bool:
        """
        Decides whether the measured OD value is an outlier or not.
        :param measured_od: optical density value
        :return: True if it is an outlier, False otherwise
        """
        lower_tol = self.calculate_tolerance(-self.lower_tol)
        upper_tol = self.calculate_tolerance(self.upper_tol)

        if lower_tol <= measured_od <= upper_tol:
            self.outliers = 0
            self.average_od = self.calculate_average()
            return False
        else:
            self.outliers += 1
            if self.outliers > self.max_outliers:
                self.outliers = 0
                self.average_od = self.calculate_average()
                return False
            else:
                return True

    def calculate_tolerance(self, value):
        return ((100 + value) / 100) * self.average_od

    def calculate_average(self):
        """
        Helper method which calculates the average of a list while removing the elements from the objects deque.
        :return: The average of the deque
        """
        my_list = []
        while self.latest_values:
            my_list.append(self.latest_values.pop())

        return sum(my_list) / len(my_list)

    def start(self):
        t = Thread(target=self._run)
        t.start()

    def _run(self):
        self.average_od = self.measure_initial_od_average()

        while self.is_active:
            command = Command(self.device_id, "19", [self.pump_id], self.task_id, is_awaited=True)
            self.device.post_command(command, 1)

            od_variant = 'od_1' if self.od_channel == 1 else 'od_0'
            command.await_cmd()

            if command.is_valid:
                od_is_valid, od = command.response.get(od_variant)
                if od_is_valid:
                    self.latest_values.appendleft(od)
                    od_is_outlier = self.handle_outlier(od)
                    if not od_is_outlier:
                        self.od.value = od
                else:
                    od_is_outlier = False

                command.response[od_variant] = od_is_valid, od, od_is_outlier
                command.save_to_database()

            sleep(self.sleep_period)

    def end(self):
        self.is_active = False


class PBRGeneralPump(BaseTask, Observer):

    def __init__(self, config):
        self.min_od = None
        self.max_od = None
        self.pump_id = None
        self.device_id: str = ""
        self.od_task_id: str = ""

        self.__dict__.update(config)
        self.is_pump_on = False

        try:
            assert self.min_od is not None
            assert self.max_od is not None
            assert self.device_id is not ""
            assert self.pump_id is not None
            assert self.od_task_id is not ""
        except AssertionError:
            raise AttributeError("Configuration of PBRGeneralPump task must contain all required attributes")

        self.device = DeviceManager().get_device(self.device_id)
        self.od_task: PBRMeasureAll = TaskManager().get_task(self.od_task_id)

        self.od_task.od.observe(self)

        super(PBRGeneralPump, self).__init__()

    def update(self, observable: Observable):
        self.stabilize(observable.value)

    def start(self):
        pass

    def end(self):
        pass

    def is_od_value_too_high(self, od):
        return od > self.max_od

    def is_od_value_too_low(self, od):
        return od < self.min_od

    def turn_pump_on(self):
        self.change_pump_state(True)

    def turn_pump_off(self):
        self.change_pump_state(False)

    def change_pump_state(self, state: bool):
        for try_n in range(5):
            command = Command(self.device_id, "8", [self.pump_id, state], self.task_id)
            self.device.post_command(command, 1)
            command.await_cmd()

            if isinstance(command.response, bool) and command.response:
                print("pump is {}".format("ON" if state else "OFF"))
                print("changing pump state to: {}".format(state))
                self.is_pump_on = state
                return
        raise ConnectionError

    def stabilize(self, od):
        if self.is_od_value_too_high(od):
            if not self.is_pump_on:
                self.turn_pump_on()
        elif self.is_od_value_too_low(od):
            if self.is_pump_on:
                self.turn_pump_off()
