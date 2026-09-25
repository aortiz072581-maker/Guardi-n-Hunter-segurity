from dataclasses import dataclass, field
from datetime import datetime, timezone


def utc_now():
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Job:
    name: str
    target: str
    interval_minutes: int = 60
    enabled: bool = True
    last_run: str | None = None


class Scheduler:
    """
    Scheduler seguro:
    - No ejecuta red automáticamente.
    - Solo administra trabajos autorizados.
    - La ejecución real queda a cargo del pipeline.
    """

    def __init__(self):
        self.jobs = {}

    def add_job(
        self,
        name,
        target,
        interval_minutes=60,
    ):
        if not name or not target:
            raise ValueError("name y target son obligatorios.")

        job = Job(
            name=name,
            target=target,
            interval_minutes=max(1, int(interval_minutes)),
        )

        self.jobs[name] = job
        return job

    def remove_job(self, name):
        return self.jobs.pop(name, None)

    def enable(self, name):
        self.jobs[name].enabled = True

    def disable(self, name):
        self.jobs[name].enabled = False

    def list_jobs(self):
        return [
            {
                "name": job.name,
                "target": job.target,
                "interval_minutes": job.interval_minutes,
                "enabled": job.enabled,
                "last_run": job.last_run,
            }
            for job in self.jobs.values()
        ]

    def mark_run(self, name):
        if name not in self.jobs:
            raise KeyError(name)

        self.jobs[name].last_run = utc_now()

        return self.jobs[name]
