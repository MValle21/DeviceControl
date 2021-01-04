from typing import Optional

from core.data.model import Experiment, Variable, Device
from core.utils import time
from core.data.dao import Dao
from core.utils.db import enquote
from core.utils.singleton import singleton


@singleton
class DataManager:
    def __init__(self, ws_client=None):
        self.last_seen_id = {'values': {}, 'events': {}}
        self.ws_client = ws_client

        self.variables = self.load_variables()
        self.experiments = dict()

    def load_variables(self):
        return [var.code for var in Variable.query.all()]

    def save_value(self, value):
        if value.variable not in self.variables:
            self.save_variable(value.variable)
            self.variables.append(value.variable)
        Dao.insert(value)

    def save_variable(self, variable):
        variable = Variable(code=variable, type='measured')
        Dao.insert(variable)

    def save_event(self, event):
        Dao.insert(event)

    def save_device(self, connector):
        device = Device(id=connector.device_id, device_class=connector.device_class,
                        device_type=connector.device_type, address=connector.address)
        Dao.insert(device)

        # TEMPORAL HACK !!!
        self.save_experiment(device.id)

    # TEMPORAL HACK !!!
    def save_experiment(self, device_id):
        current_time = time.now()
        experiment = Experiment(dev_id=device_id, start=current_time)
        Dao.insert(experiment)
        self.experiments[device_id] = experiment

    # TEMPORAL HACK !!!
    def update_experiment(self, device_id):
        experiment = self.experiments.pop(device_id)
        experiment.end = time.now()
        Dao.insert(experiment)

    # TODO
    def _get_data(self, conditions, device_id, table):
        response = Dao.select(table, conditions)
        result = {}

        columns = list.copy(Dao.tables[table])

        for row in response:
            log_id = row[0]
            row = dict(zip(columns, (row[1:])))
            for key, item in row.items():
                # noinspection PyBroadException
                try:
                    item = eval(item)
                    row[key] = item
                except Exception:
                    continue
            result[log_id] = row

        if device_id is not None and response:
            self.last_seen_id[table][device_id] = max(list(map(int, result.keys())))

        return result

    def get_data(self,
                 log_id: Optional[int],
                 last_time: Optional[str],
                 device_id: Optional[str],
                 data_type: str = 'values'):

        where_conditions = ["dev_id={}".format(enquote(device_id))]

        if last_time is not None:
            where_conditions.append("TIMESTAMP(time)>TIMESTAMP({})".format(last_time))
        else:
            if log_id is None:
                log_id = self.last_seen_id[data_type].get(device_id, 0)
            where_conditions.append("id>{}".format(log_id))

        return self._get_data(where_conditions, device_id, data_type)

    def get_latest_data(self, device_id, data_type: str = 'values'):
        where_conditions = []
        if device_id is None:
            where_conditions.append("log_id=(SELECT MAX(id) FROM {})".format(data_type))
        else:
            where_conditions.append(
                "log_id=(SELECT MAX(id) FROM {} WHERE dev_id={})".format(data_type, enquote(device_id)),
            )
        return self._get_data(where_conditions, device_id, data_type)
