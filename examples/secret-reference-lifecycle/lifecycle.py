"""Fictional version-label model for secret rotation and CloudFormation use.

No secret values, CloudFormation template, AWS call, or deployed resource exists.
"""

from __future__ import annotations

import json


def trace(reference: str, steps: list[str]) -> list[dict]:
    if reference not in {"versionless", "pinned-v1"}:
        raise ValueError("reference must be versionless or pinned-v1")
    valid = {"create", "rotate", "refresh_runtime", "refresh_failed_keep_cache", "update_resource", "update_resource_failed"}
    if not steps or steps[0] != "create" or any(step not in valid for step in steps):
        raise ValueError("timeline must begin with create and contain known steps")
    store = "v1"
    supplier = "v1"
    injected = None
    runtime_cache = None
    results = []
    for index, step in enumerate(steps):
        if step == "create":
            if index != 0:
                raise ValueError("create occurs once at the start")
            injected = "v1"
            runtime_cache = "v1"
        elif step == "rotate":
            if store != "v1":
                raise ValueError("this small study has only one rotation")
            store = supplier = "v2"
        elif step == "refresh_runtime":
            runtime_cache = store
        elif step == "refresh_failed_keep_cache":
            # This case explicitly chooses to keep the cached label; real policy may differ.
            pass
        elif step == "update_resource":
            injected = store if reference == "versionless" else "v1"
        elif step == "update_resource_failed":
            # Fictional failure before the new value takes effect; real rollback may differ.
            pass
        results.append({
            "step": step,
            "store_current": store,
            "supplier_accepts": supplier,
            "template_injected": injected,
            "runtime_cache": runtime_cache,
            "injected_works": injected == supplier,
            "runtime_works": runtime_cache == supplier,
            "live_aws_observed": False,
        })
    return results


def main() -> None:
    cases = {
        "versionless": ["create", "rotate", "refresh_runtime", "update_resource"],
        "pinned-v1": ["create", "rotate", "update_resource"],
        "failed-refresh-keep-cache": ["create", "rotate", "refresh_failed_keep_cache", "refresh_runtime"],
        "failed-update-then-retry": ["create", "rotate", "update_resource_failed", "update_resource"],
    }
    print(json.dumps({name: trace("pinned-v1" if name == "pinned-v1" else "versionless", steps) for name, steps in cases.items()}, indent=2))


if __name__ == "__main__":
    main()
