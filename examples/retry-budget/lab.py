"""Deterministic retry/deadline arithmetic; no network, AWS, or real billing."""

from dataclasses import dataclass
from decimal import Decimal
import json


@dataclass(frozen=True)
class Policy:
    outer_attempts: int
    inner_attempts: int
    total_call_limit: int | None
    deadline_seconds: int | None


STACKED = Policy(3, 3, None, None)
SINGLE_LAYER = Policy(1, 3, 3, 10)
SHARED_BUDGET = Policy(3, 3, 3, 10)


def simulate(policy: Policy, *, failure: str = "transient", succeeds_on: int | None = None):
    """Count sequential service calls; each takes two fictional seconds.

    A permanent error is never retried. The caller must have enough time to
    finish a call before its deadline; finishing exactly on it is allowed.
    Backoff after each failure is 1, then 2 seconds within a layer. The outer
    layer also waits 1, then 2 seconds after each exhausted inner sequence.
    """
    if failure not in {"transient", "permanent"}:
        raise ValueError("failure must be transient or permanent")
    if succeeds_on is not None and (type(succeeds_on) is not int or succeeds_on < 1):
        raise ValueError("succeeds_on must be a positive call number")
    for number in (policy.outer_attempts, policy.inner_attempts):
        if type(number) is not int or number < 1:
            raise ValueError("attempt limits must be positive integers")
    if policy.total_call_limit is not None and (
        type(policy.total_call_limit) is not int or policy.total_call_limit < 1
    ):
        raise ValueError("total call limit must be a positive integer")
    if policy.deadline_seconds is not None and (
        type(policy.deadline_seconds) is not int or policy.deadline_seconds < 0
    ):
        raise ValueError("deadline must be a nonnegative integer")

    calls = elapsed = 0
    stop = "attempts_exhausted"
    for outer in range(policy.outer_attempts):
        if outer:
            if policy.total_call_limit is not None and calls >= policy.total_call_limit:
                stop = "call_budget_exhausted"
                break
            if policy.deadline_seconds is not None and elapsed + outer + 2 > policy.deadline_seconds:
                stop = "deadline_exhausted"
                break
            elapsed += outer  # 1 second before outer retry 2; 2 before retry 3
        for inner in range(policy.inner_attempts):
            if inner:
                if policy.total_call_limit is not None and calls >= policy.total_call_limit:
                    stop = "call_budget_exhausted"
                    break
                if policy.deadline_seconds is not None and elapsed + inner + 2 > policy.deadline_seconds:
                    stop = "deadline_exhausted"
                    break
                elapsed += inner
            if policy.deadline_seconds is not None and elapsed + 2 > policy.deadline_seconds:
                stop = "deadline_exhausted"
                break
            calls += 1
            elapsed += 2
            if calls == succeeds_on:
                stop = "completed"
                break
            if failure == "permanent":
                stop = "permanent_error"
                break
        if stop != "attempts_exhausted":
            break
    return {"calls": calls, "elapsed_seconds": elapsed, "outcome": stop}


def fictional_cost(calls: int, requests: int, price_per_call: str = "0.001") -> str:
    if type(calls) is not int or calls < 0 or type(requests) is not int or requests < 0:
        raise ValueError("counts must be nonnegative integers")
    price = Decimal(price_per_call)
    if not price.is_finite() or price < 0:
        raise ValueError("price must be finite and nonnegative")
    return str(Decimal(calls) * Decimal(requests) * price)


if __name__ == "__main__":
    cases = {
        "stacked_failure": simulate(STACKED),
        "single_layer_failure": simulate(SINGLE_LAYER),
        "shared_budget_failure": simulate(SHARED_BUDGET),
        "transient_then_success": simulate(SINGLE_LAYER, succeeds_on=3),
        "permanent_denial": simulate(SINGLE_LAYER, failure="permanent"),
    }
    for value in cases.values():
        value["fictional_100_request_cost_usd"] = fictional_cost(value["calls"], 100)
    print(json.dumps(cases, indent=2))
