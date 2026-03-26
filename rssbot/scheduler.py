from __future__ import annotations

from dataclasses import dataclass

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger


@dataclass(frozen=True)
class CronScheduler:
    timezone: str | None = None

    def run(self, *, cron_schedules: list[str], job, job_name: str = "rssbot") -> None:  # noqa: ANN001
        schedules = [s.strip() for s in (cron_schedules or []) if s and s.strip()]
        if not schedules:
            raise RuntimeError(
                "CRON_SCHEDULES пустой. Укажи хотя бы одно cron-выражение, "
                'например: CRON_SCHEDULES="0 9 * * *"'
            )

        scheduler = BlockingScheduler(timezone=self.timezone)
        for i, expr in enumerate(schedules):
            trigger = _cron_trigger_from_5_field(expr)
            scheduler.add_job(job, trigger, name=f"{job_name}-{i}")

        scheduler.start()


def _cron_trigger_from_5_field(expr: str) -> CronTrigger:
    parts = [p for p in expr.split(" ") if p]
    if len(parts) != 5:
        raise ValueError(f'Неверный cron "{expr}". Ожидается 5 полей: "m h dom mon dow"')
    minute, hour, day, month, dow = parts
    return CronTrigger(minute=minute, hour=hour, day=day, month=month, day_of_week=dow)

