import sys


from core.flow.workflow import Scheduler, WorkflowProvider
from core.log import Logger

from core.connection import classes

logger = Logger()


workflowProvider = WorkflowProvider()

default = "websocket_client"

conModule = None
conModuleStartArgs = None

if len(sys.argv) > 1:
    conModule, conModuleStartArgs = classes.get(sys.argv[1])

if conModule is None:
    conModule, conModuleStartArgs = classes.get(default)

conModule().start(*conModuleStartArgs)


