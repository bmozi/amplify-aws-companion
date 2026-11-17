"""Cloud-free two-stage library model: dispatch is not pickup readiness.

Each stage is one fictional, non-preemptive worker. The second stage receives
only completed dispatches. Neither worker represents an AWS service or an
actual library process.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json

from queue_window import DEADLINE_SECONDS, Job, dispatch, make_arrivals, summarize


@dataclass(frozen=True)
class PickupResult:
    job_id: str
    branch: str
    hold_arrived: int
    dispatched: int
    ready: int


def two_stage(shape: str = "even", dispatch_seconds: int = 5,
              pickup_seconds: int = 30, dispatch_policy: str = "fifo",
              pickup_policy: str = "fifo") -> dict[str, object]:
    holds = make_arrivals(shape)
    dispatched = dispatch(holds, dispatch_policy, dispatch_seconds)
    pickup_inputs = [Job(result.job_id, result.branch, result.finished)
                     for result in dispatched]
    pickups = dispatch(pickup_inputs, pickup_policy, pickup_seconds)
    arrival_by_id = {job.job_id: job.arrived for job in holds}
    dispatch_by_id = {result.job_id: result.finished for result in dispatched}
    customer = [PickupResult(result.job_id, result.branch,
                             arrival_by_id[result.job_id],
                             dispatch_by_id[result.job_id], result.finished)
                for result in pickups]
    if {result.job_id for result in customer} != set(arrival_by_id):
        raise AssertionError("A job was lost between modeled stages")
    dispatch_summary = summarize(dispatched)
    branches = {}
    for branch in ("A", "B", "C", "D"):
        group = [result for result in customer if result.branch == branch]
        branches[branch] = {
            "jobs": len(group),
            "dispatched_within_30_minutes": dispatch_summary["branches"][branch]["within_30_minutes"],
            "ready_within_30_minutes": sum(
                result.ready - result.hold_arrived <= DEADLINE_SECONDS for result in group
            ),
        }
    return {
        "assumptions": {"shape": shape, "dispatch_seconds": dispatch_seconds,
                        "pickup_seconds": pickup_seconds,
                        "dispatch_policy": dispatch_policy,
                        "pickup_policy": pickup_policy,
                        "workers_per_stage": 1,
                        "deadline_from_hold_minutes": 30,
                        "jobs": len(holds)},
        "branches": branches,
        "scope": "fictional serial two-stage arithmetic; no actual pickup or AWS measurement",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--shape", choices=("even", "front-loaded"), default="even")
    parser.add_argument("--dispatch-seconds", type=int, default=5)
    parser.add_argument("--pickup-seconds", type=int, default=30)
    parser.add_argument("--dispatch-policy", choices=("fifo", "round-robin"), default="fifo")
    parser.add_argument("--pickup-policy", choices=("fifo", "round-robin"), default="fifo")
    args = parser.parse_args()
    print(json.dumps(two_stage(args.shape, args.dispatch_seconds,
                               args.pickup_seconds, args.dispatch_policy,
                               args.pickup_policy), indent=2))


if __name__ == "__main__":
    main()
