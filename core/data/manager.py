from core.utils import time
from core.data.dao import Dao
from core.utils.singleton import singleton
from core.utils.time import from_string


@singleton
class DataManager:
    def __init__(self, ws_client=None):
        self.last_seen_id = {'values': {}, 'events': {}}
        self.ws_client = ws_client

        self.variables = self.load_variables()
        self.experiments = dict()

    def load_variables(self):
        import core.data.model as model
        return [var.code for var in model.Variable.query.all()]

    def save_value(self, value):
        if value.variable not in self.variables:
            self.save_variable(value.variable)
            self.variables.append(value.variable)
        Dao.insert(value)

    def save_variable(self, variable):
        import core.data.model as model
        variable = model.Variable(code=variable, type='measured')
        Dao.insert(variable)

    def save_event(self, event):
        Dao.insert(event)

    def save_device(self, connector):
        import core.data.model as model
        device = model.Device(id=connector.device_id, device_class=connector.device_class,
                              device_type=connector.device_type, address=connector.address)
        Dao.insert(device)

        # TEMPORAL HACK !!!
        self.save_experiment(device.id)

    # TEMPORAL HACK !!!
    def save_experiment(self, device_id):
        import core.data.model as model
        current_time = time.now()
        experiment = model.Experiment(dev_id=device_id, start=current_time)
        Dao.insert(experiment)
        self.experiments[device_id] = experiment

    # TEMPORAL HACK !!!
    def update_experiment(self, device_id):
        experiment = self.experiments.pop(device_id)
        experiment.end = time.now()
        Dao.insert(experiment)

    def post_process(self, query_results, data_type, device_id):
        result = {}

        for obj in query_results:
            row = obj.__dict__  # PROBABLY WONT WORK !!!
            log_id = row.pop('id')
            result[log_id] = row

        if device_id is not None:
            self.last_seen_id[data_type][device_id] = max(list(map(int, result.keys())))

        return result

    def get_data(self, log_id: int, last_time: str, device_id: str, data_type: str = 'values'):
        import core.data.model as model
        cls = model.Value if data_type == 'values' else model.Event

        if last_time is not None:
            last_time = from_string(last_time)
            return self.post_process(cls.query.filter_by(dev_id=device_id).filter(cls.time > last_time).all(),
                                     data_type, device_id)
        else:
            if log_id is None:
                log_id = self.last_seen_id[data_type].get(device_id, 0)
            return self.post_process(cls.query.filter_by(dev_id=device_id).filter(cls.id > log_id).all(),
                                     data_type, device_id)

    def get_latest_data(self, device_id, data_type: str = 'values'):
        import core.data.model as model
        cls = model.Value if data_type == 'values' else model.Event

        return cls.query.filter_by(dev_id=device_id).order_by(cls.id.desc()).first()
