"""Finite, fictional worker-capacity worksheet; no AWS calls or energy model."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Result:
    accepted: int
    timely: int
    late: int
    unfinished: int
    worker_minutes: int
    peak_backlog: int
    backlog_at_deadline: int


def simulate(arrivals: tuple[int, ...], workers: tuple[int, ...], *,
             rate: int = 15, deadline: int = 4) -> Result:
    """One shared absolute deadline; each worker completes `rate` jobs per minute.

    Arrivals enter at the start of each minute; completed jobs leave at its end.
    Every provisioned worker-minute is counted, including an idle worker.
    The queue is assumed durable and every job correct; neither is verified here.
    """
    if (not arrivals or len(arrivals) != len(workers) or rate <= 0 or
            not 0 < deadline <= len(arrivals) or
            any(not isinstance(n, int) or n < 0 for n in arrivals + workers) or
            any(arrivals[deadline:])):
        raise ValueError("Use nonnegative minute counts and arrivals before the shared deadline")
    backlog = peak = timely = late = 0
    at_deadline = 0
    for minute, (new, active) in enumerate(zip(arrivals, workers)):
        backlog += new
        peak = max(peak, backlog)
        completed = min(backlog, active * rate)
        backlog -= completed
        if minute < deadline:
            timely += completed
        else:
            late += completed
        if minute + 1 == deadline:
            at_deadline = backlog
    return Result(sum(arrivals), timely, late, backlog, sum(workers), peak, at_deadline)


if __name__ == "__main__":
    burst = (90, 0, 0, 0, 0, 0, 0, 0)
    cases = {
        "four_workers_all_eight_minutes": (4,) * 8,
        "two_workers_four_minutes": (2, 2, 2, 2, 0, 0, 0, 0),
        "one_worker_six_minutes": (1, 1, 1, 1, 1, 1, 0, 0),
        "one_worker_out_after_first_minute": (2, 1, 1, 1, 1, 1, 0, 0),
    }
    for label, schedule in cases.items():
        print(label, simulate(burst, schedule))
