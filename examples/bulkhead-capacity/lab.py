"""Deterministic local capacity exercise; deliberately not an AWS simulator."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Job:
    name: str
    kind: str
    arrival: int
    duration: int


JOBS = (
    Job("report-1", "report", 0, 4),
    Job("report-2", "report", 0, 4),
    Job("report-3", "report", 0, 4),
    Job("report-4", "report", 0, 4),
    Job("booking-1", "booking", 1, 1),
)


def run(*, separate_workers: bool, database_slots: int, jobs=JOBS):
    """Return start/end times while enforcing worker and shared DB capacities.

    A job holds one worker and one DB slot for its whole stipulated duration.
    Bookings get priority only when a slot becomes free; running reports are not
    preempted. This explicit rule keeps the exercise reproducible.
    """
    if database_slots < 1:
        raise ValueError("database_slots must be positive")
    if any(job.duration < 1 or job.arrival < 0 for job in jobs):
        raise ValueError("arrival and duration must be nonnegative/positive")
    if len({job.name for job in jobs}) != len(jobs):
        raise ValueError("job names must be unique")
    if any(job.kind not in {"booking", "report"} for job in jobs):
        raise ValueError("unknown job kind")

    capacities = {"booking": 1, "report": 1} if separate_workers else {"shared": 2}
    running = {}
    result = {}
    clock = 0
    while len(result) < len(jobs):
        for name, (_, end, _) in list(running.items()):
            if end == clock:
                del running[name]

        waiting = [job for job in jobs if job.arrival <= clock and job.name not in running and job.name not in result]
        waiting.sort(key=lambda job: (job.kind != "booking", job.arrival, job.name))
        for job in waiting:
            pool = job.kind if separate_workers else "shared"
            busy_pool = sum(used_pool == pool for _, _, used_pool in running.values())
            if busy_pool >= capacities[pool] or len(running) >= database_slots:
                continue
            end = clock + job.duration
            running[job.name] = (clock, end, pool)
            result[job.name] = (clock, end)
        clock += 1
        if clock > 1000:
            raise RuntimeError("fixture did not finish")
    return result


def summary(*, separate_workers: bool, database_slots: int):
    result = run(separate_workers=separate_workers, database_slots=database_slots)
    booking_start, booking_end = result["booking-1"]
    return {"booking_start": booking_start, "booking_end": booking_end,
            "within_three_ticks": booking_end <= 3, "report_backlog_at_three":
            sum(end > 3 for name, (_, end) in result.items() if name.startswith("report-"))}


if __name__ == "__main__":
    for label, separated, slots in (("shared workers", False, 2),
                                    ("separate workers", True, 2),
                                    ("separate workers, shared DB bottleneck", True, 1)):
        print(f"{label}: {summary(separate_workers=separated, database_slots=slots)}")
