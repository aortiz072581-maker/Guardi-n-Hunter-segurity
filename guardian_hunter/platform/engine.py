from guardian_hunter.analysis import analyze
from guardian_hunter.dashboard.pro import build_dashboard
from guardian_hunter.automation import Scheduler


class GuardianPlatform:
    """
    Orquestador local de Guardian Hunter.

    No realiza reconocimiento por sí mismo.
    Coordina módulos ya autorizados y probados.
    """

    VERSION = "3.0"

    def __init__(self):
        self.scheduler = Scheduler()

    def analyze_findings(
        self,
        findings,
        previous_baseline=None,
    ):
        return analyze(
            findings,
            previous_baseline=previous_baseline,
        )

    def dashboard(self, **kwargs):
        return build_dashboard(**kwargs)

    def schedule(
        self,
        name,
        target,
        interval_minutes=60,
    ):
        return self.scheduler.add_job(
            name,
            target,
            interval_minutes,
        )

    def status(self):
        return {
            "platform": "Guardian Hunter",
            "version": self.VERSION,
            "scheduler_jobs": len(
                self.scheduler.jobs
            ),
            "mode": "authorized_defensive",
        }
