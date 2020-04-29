from threading import Thread, Event
from typing import List, Callable

from core.utils.singleton import singleton


class Job:
    def __init__(self, task: Callable, args=None):
        if args is None:
            args = []

        self.task: Callable = task
        self.success = False
        self.cause = None
        self.data = None
        self.is_done = Event()
        self.args: [] = args


class Scheduler(Thread):
    def __init__(self):
        super(Scheduler, self).__init__()
        self.name = "scheduler thread"
        self.jobs: List[(Job, [])] = []
        self.is_active = True
        self.has_jobs = Event()

    def schedule_job(self, job: Job):
        self.jobs.append(job)
        self.has_jobs.set()

    @staticmethod
    def execute(job: Job):
        job.success, cause, job.data = job.task(*job.args)
        job.cause = repr(cause)
        job.is_done.set()

    def run(self):
        from custom.devices.PSI.java.utils import Controller
        Controller.start_jvm()
        while self.is_active:
            self.has_jobs.wait()
            while self.jobs:
                self.execute(self.jobs.pop(0))
            self.has_jobs.clear()


@singleton
class WorkflowProvider:
    def __init__(self):

        self.scheduler = Scheduler()
        self.scheduler.start()
