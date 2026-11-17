"""Fictional fleet rollout decision checks; no AWS APIs, SDKs, CLI or network."""
from copy import deepcopy
import json


NOW = 100
MAX_INVENTORY_AGE = 10
EXPECTED_IDS = {"api-01", "api-02", "api-03", "api-04"}
RINGS = ("canary", "pilot", "fleet")
BASELINE = "repair-linux-2026.10-r2"


def make_fleet():
    return [
        {"id": "api-01", "environment": "prod", "role": "repair-api", "managed": True,
         "observed_at": 98, "os": "linux-supported", "baseline": BASELINE, "ring": "canary"},
        {"id": "api-02", "environment": "prod", "role": "repair-api", "managed": True,
         "observed_at": 97, "os": "linux-supported", "baseline": BASELINE, "ring": "pilot"},
        {"id": "api-03", "environment": "prod", "role": "repair-api", "managed": True,
         "observed_at": 97, "os": "linux-supported", "baseline": BASELINE, "ring": "pilot"},
        {"id": "api-04", "environment": "prod", "role": "repair-api", "managed": True,
         "observed_at": 99, "os": "linux-supported", "baseline": BASELINE, "ring": "fleet"},
        {"id": "dev-01", "environment": "dev", "role": "repair-api", "managed": True,
         "observed_at": 99, "os": "linux-supported", "baseline": BASELINE, "ring": "fleet"},
    ]


def preflight(nodes, approved_ids, baseline=BASELINE):
    matched = [node for node in nodes if node["environment"] == "prod" and node["role"] == "repair-api"]
    selected = {node["id"] for node in matched}
    problems = []
    all_ids = [node["id"] for node in nodes]
    if len(all_ids) != len(set(all_ids)):
        problems.append({"check": "duplicate_inventory_identity"})
    if selected != set(approved_ids):
        problems.append({"check": "target_scope", "expected": sorted(approved_ids), "matched": sorted(selected)})
    for node in matched:
        if node["ring"] not in RINGS:
            problems.append({"check": "rollout_ring", "node": node["id"]})
        if not node["managed"]:
            problems.append({"check": "managed_node", "node": node["id"]})
        if NOW - node["observed_at"] > MAX_INVENTORY_AGE:
            problems.append({"check": "inventory_freshness", "node": node["id"]})
        if node["os"] != "linux-supported":
            problems.append({"check": "platform_eligibility", "node": node["id"]})
        if node["baseline"] != baseline:
            problems.append({"check": "baseline_version", "node": node["id"]})
    return matched, problems


def run_campaign(nodes, approved_ids, operation_id, outcomes, health, ledger=None):
    ledger = {} if ledger is None else ledger
    fingerprint = json.dumps({"approved_ids": sorted(approved_ids), "baseline": BASELINE}, sort_keys=True)
    if operation_id in ledger:
        prior = ledger[operation_id]
        if prior["fingerprint"] != fingerprint:
            return {"operation_id": operation_id, "status": "idempotency_conflict",
                    "attempts": [], "scope": "changed request rejected locally"}, ledger
        return deepcopy(prior["result"]), ledger
    targets, problems = preflight(nodes, approved_ids)
    if problems:
        result = {"operation_id": operation_id, "status": "blocked_before_change",
                  "problems": problems, "attempts": [], "baseline": BASELINE}
        ledger[operation_id] = {"fingerprint": fingerprint, "result": result}
        return deepcopy(result), ledger

    attempts = []
    for ring in RINGS:
        wave = [node for node in targets if node["ring"] == ring]
        if not wave:
            continue
        wave_failed = False
        for node in wave:
            outcome = outcomes.get(node["id"], "unknown")
            attempts.append({"node": node["id"], "ring": ring, "patch_result": outcome,
                             "health": health.get(node["id"], "not_checked") if outcome == "success" else "not_checked"})
            if outcome != "success" or health.get(node["id"]) != "pass":
                wave_failed = True
                break  # sequential model with max-errors=0; no later ring starts
        if wave_failed:
            break

    completed_rings = []
    failed = False
    for ring in RINGS:
        rows = [row for row in attempts if row["ring"] == ring]
        if not rows:
            break
        if len(rows) != len([node for node in targets if node["ring"] == ring]) or any(
                row["patch_result"] != "success" or row["health"] != "pass" for row in rows):
            failed = True
            break
        completed_rings.append(ring)
    result = {"operation_id": operation_id,
              "status": "stopped_for_investigation" if failed else "all_rings_verified_in_fixture",
              "baseline": BASELINE, "target_ids": sorted(approved_ids),
              "completed_rings": completed_rings, "attempts": attempts,
              "max_errors": 0,
              "scope": "synthetic local policy check; no node was patched and no AWS behavior was invoked"}
    ledger[operation_id] = {"fingerprint": fingerprint, "result": result}
    return deepcopy(result), ledger


def reject(operation):
    try:
        operation()
    except (KeyError, TypeError, ValueError):
        return
    raise AssertionError("Changed or incomplete request was not rejected")


def main():
    if not __debug__:
        raise SystemExit("Run without Python optimization; this teaching lab uses assertions")
    fleet = make_fleet()
    selected, problems = preflight(fleet, EXPECTED_IDS)
    assert {node["id"] for node in selected} == EXPECTED_IDS and problems == []

    outcomes = {node_id: "success" for node_id in EXPECTED_IDS}
    health = {node_id: "pass" for node_id in EXPECTED_IDS}
    success, ledger = run_campaign(fleet, EXPECTED_IDS, "maint-2026-10-19-01", outcomes, health)
    assert success["status"] == "all_rings_verified_in_fixture"
    assert success["completed_rings"] == list(RINGS)
    replay, ledger = run_campaign(fleet, EXPECTED_IDS, "maint-2026-10-19-01", outcomes, health, ledger)
    assert replay == success and len(ledger) == 1
    changed_replay, ledger = run_campaign(fleet, EXPECTED_IDS | {"api-05"}, "maint-2026-10-19-01",
                                          outcomes, health, ledger)
    assert changed_replay["status"] == "idempotency_conflict" and changed_replay["attempts"] == []

    failed_health = dict(health, **{"api-01": "fail"})
    stopped, _ = run_campaign(fleet, EXPECTED_IDS, "maint-2026-10-19-02", outcomes, failed_health)
    assert stopped["status"] == "stopped_for_investigation"
    assert stopped["completed_rings"] == []
    assert all(row["ring"] == "canary" for row in stopped["attempts"])
    assert stopped["attempts"][0]["patch_result"] == "success"  # health failure did not reverse patch

    stale = deepcopy(fleet)
    stale[0]["observed_at"] = 80
    blocked, _ = run_campaign(stale, EXPECTED_IDS, "maint-2026-10-19-03", outcomes, health)
    assert blocked["status"] == "blocked_before_change"
    assert blocked["attempts"] == []

    unexpected = deepcopy(fleet)
    unexpected.append({"id": "api-05", "environment": "prod", "role": "repair-api", "managed": True,
                       "observed_at": 99, "os": "linux-supported", "baseline": BASELINE, "ring": "fleet"})
    extra, _ = run_campaign(unexpected, EXPECTED_IDS, "maint-2026-10-19-04", outcomes, health)
    assert extra["status"] == "blocked_before_change" and extra["attempts"] == []

    changed_baseline = deepcopy(fleet)
    changed_baseline[2]["baseline"] = "unreviewed-next"
    drifted, _ = run_campaign(changed_baseline, EXPECTED_IDS, "maint-2026-10-19-05", outcomes, health)
    assert drifted["status"] == "blocked_before_change"

    unmanaged = deepcopy(fleet)
    unmanaged[1]["managed"] = False
    unmanaged_result, _ = run_campaign(unmanaged, EXPECTED_IDS, "maint-2026-10-19-06", outcomes, health)
    assert unmanaged_result["status"] == "blocked_before_change"

    duplicate = deepcopy(fleet)
    duplicate.append(deepcopy(fleet[0]))
    duplicate_result, _ = run_campaign(duplicate, EXPECTED_IDS, "maint-2026-10-19-07", outcomes, health)
    assert duplicate_result["status"] == "blocked_before_change"

    print(json.dumps({"successful_fixture": success, "canary_health_failure": stopped,
                      "stale_inventory": blocked, "unexpected_target": extra,
                      "baseline_change": drifted, "unmanaged_target": unmanaged_result,
                      "duplicate_inventory_id": duplicate_result,
                      "scope": "fictional sequential decision model only; no inventory query, patch, workflow, AWS or network call"}, indent=2))


if __name__ == "__main__":
    main()
