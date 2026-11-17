"""A deliberately small, cloud-free branch-library dispatch model.

This models one non-preemptive worker, not Amazon SQS, Lambda, a real pickup
workflow, or a measured customer promise. All arrivals and service times are
fictional. Keep the algorithm visible so learners can challenge its premises.
"""

from __future__ import annotations

import argparse
from collections import defaultdict, deque
from dataclasses import dataclass
import json
from math import ceil


BRANCHES = ("A", "B", "C", "D")
DEADLINE_SECONDS = 30 * 60


@dataclass(frozen=True)
class Job:
    job_id: str
    branch: str
    arrived: int


@dataclass(frozen=True)
class Result:
    job_id: str
    branch: str
    arrived: int
    started: int
    finished: int


def make_arrivals(shape: str) -> list[Job]:
    """400 A jobs and 20 for each other branch in a one-hour window."""
    if shape not in ("even", "front-loaded"):
        raise ValueError("shape must be even or front-loaded")
    a_window = 3600 if shape == "even" else 900
    jobs = [Job(f"A-{n:03}", "A", n * a_window // 400)
            for n in range(400)]
    for branch in BRANCHES[1:]:
        jobs.extend(Job(f"{branch}-{n:02}", branch, n * 3600 // 20)
                    for n in range(20))
    return sorted(jobs, key=lambda job: (job.arrived, job.branch, job.job_id))


def dispatch(jobs: list[Job], policy: str, seconds_per_job: int) -> list[Result]:
    if policy not in ("fifo", "round-robin"):
        raise ValueError("policy must be fifo or round-robin")
    if not 1 <= seconds_per_job <= 3600:
        raise ValueError("seconds_per_job must be between 1 and 3600")
    if len({job.job_id for job in jobs}) != len(jobs):
        raise ValueError("job IDs must be unique")
    if any(job.branch not in BRANCHES or job.arrived < 0 for job in jobs):
        raise ValueError("branch and arrival must be valid")
    arrivals = sorted(jobs, key=lambda job: (job.arrived, job.branch, job.job_id))
    fifo: deque[Job] = deque()
    by_branch: dict[str, deque[Job]] = defaultdict(deque)
    turn: deque[str] = deque()
    results: list[Result] = []
    now = 0
    cursor = 0
    while cursor < len(arrivals) or (fifo if policy == "fifo" else turn):
        if cursor < len(arrivals) and not (fifo if policy == "fifo" else turn):
            now = max(now, arrivals[cursor].arrived)
        while cursor < len(arrivals) and arrivals[cursor].arrived <= now:
            job = arrivals[cursor]
            if policy == "fifo":
                fifo.append(job)
            else:
                if not by_branch[job.branch]:
                    turn.append(job.branch)
                by_branch[job.branch].append(job)
            cursor += 1
        if policy == "fifo":
            job = fifo.popleft()
        else:
            branch = turn.popleft()
            job = by_branch[branch].popleft()
            if by_branch[branch]:
                turn.append(branch)
        finished = now + seconds_per_job
        results.append(Result(job.job_id, job.branch, job.arrived, now, finished))
        now = finished
    return results


def summarize(results: list[Result]) -> dict[str, object]:
    output: dict[str, object] = {"total": len(results), "branches": {}}
    for branch in BRANCHES:
        group = [r for r in results if r.branch == branch]
        durations = sorted(r.finished - r.arrived for r in group)
        output["branches"][branch] = {
            "jobs": len(group),
            "within_30_minutes": sum(duration <= DEADLINE_SECONDS for duration in durations),
            "p95_minutes": round(durations[ceil(len(durations) * .95) - 1] / 60, 2) if durations else None,
            "last_finish_minutes": round(max((r.finished for r in group), default=0) / 60, 2),
        }
    return output


def comparison(shape: str = "even", seconds_per_job: int = 30) -> dict[str, object]:
    jobs = make_arrivals(shape)
    return {
        "assumptions": {"shape": shape, "seconds_per_job": seconds_per_job,
                        "workers": 1, "deadline_minutes": 30,
                        "window_minutes": 60, "total_jobs": len(jobs)},
        "fifo": summarize(dispatch(jobs, "fifo", seconds_per_job)),
        "round_robin": summarize(dispatch(jobs, "round-robin", seconds_per_job)),
        "evidence_scope": "fictional one-worker arithmetic; not SQS behavior or pickup completion",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--shape", choices=("even", "front-loaded"), default="even")
    parser.add_argument("--seconds-per-job", type=int, default=30)
    args = parser.parse_args()
    print(json.dumps(comparison(args.shape, args.seconds_per_job), indent=2))


if __name__ == "__main__":
    main()
