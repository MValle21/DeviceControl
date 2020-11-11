import requests

# This is to execute a test run to check if all functionality is working
# tested on a test (artificial) PBR

# FIRST START THE SERVER !

# settings for test PBR
PBR_id = 'PBR-PSI-test01'
test_PBR_device = {
                    'device_id': PBR_id,
                    'device_class': 'test',
                    'device_type': 'PBR',
                    'address': 'null',
                  }

response = requests.post('http://localhost:5000/device', json=test_PBR_device)
assert response.json()["success"] == True

# settings for periodical measurement task
measure_all_task_id = 'task-measure-PBR-test-01'
measure_all_task = {
                    'task_id': measure_all_task_id,
                    'task_class': 'PSI',
                    'task_type': 'PBR_measure_all',
                    'device_id': PBR_id,
                    'sleep_period': 0.1,
                    'max_outliers': 6,
                    'pump_id': 5,
                    'lower_tol': 5,
                    'upper_tol': 5,
                    'od_channel': 1
                   }

response = requests.post('http://localhost:5000/task', json=measure_all_task)
assert response.json()["success"] == True

# settings for turbidostat task
pump_task_id = 'task-turbidostat-PBR-test-01'
turbidostat_task = {
                    'task_id': pump_task_id,
                    'task_class': 'PSI',
                    'task_type': 'PBR_pump',
                    'device_id': PBR_id,
                    'min_od': 0.4,
                    'max_od': 0.6,
                    'pump_id': 5,
                    'measure_all_task_id': measure_all_task_id,
                    'pump_on_command': {'command_id': '8', 'arguments': '[5, True]'},
                    'pump_off_command': {'command_id': '8', 'arguments': '[5, False]'}
                   }

response = requests.post('http://localhost:5000/task', json=turbidostat_task)
assert response.json()["success"] == True

# sleep for some time

# send a random command - to change some value

# ask for data - both event and values
# ask again with new log_id to check if got only new ones

# end all tasks and device
