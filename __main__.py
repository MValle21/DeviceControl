import sys

from core.flow.workflow import Scheduler, WorkflowProvider
from core.log import Logger

import core.connection
from custom.devices.PSI.java.utils.jvm_controller import Controller

logger = Logger()


workflowProvider = WorkflowProvider()
controller = Controller()

default = "flask_server"

if len(sys.argv) > 1:
    testing = eval(sys.argv[1])
else:
    testing = False

conModule, conModuleStartArgs = core.connection.classes.get(default)
conModule().start(testing)
