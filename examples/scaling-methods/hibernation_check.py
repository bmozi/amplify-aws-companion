#!/usr/bin/env python3
"""Check a supplied EC2 hibernation candidate against selected documented rules.

This local teaching aid is deliberately not an AWS capability query. The caller
must verify AMI/type support in current AWS documentation and the target Region.
"""

import json
import math
import sys
from pathlib import Path


def _number(candidate, field, errors):
    value = candidate.get(field)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        errors.append(f"{field} must be a number in GiB")
        return None
    if not math.isfinite(value) or value <= 0:
        errors.append(f"{field} must be finite and greater than zero")
        return None
    return float(value)


def assess(candidate):
    """Return a conservative teaching assessment for the supplied record."""
    errors = []
    if not isinstance(candidate, dict):
        return {"status": "invalid", "errors": ["candidate must be a JSON object"]}

    os_name = candidate.get("os")
    if not isinstance(os_name, str) or os_name not in {"linux", "windows"}:
        errors.append("os must be 'linux' or 'windows'")

    ram = _number(candidate, "ram_gib", errors)
    root = _number(candidate, "root_volume_gib", errors)
    system = _number(candidate, "os_and_application_gib", errors)
    reserve = _number(candidate, "working_space_gib", errors)

    if ram is not None and os_name == "linux" and ram >= 150:
        errors.append("Linux hibernation requires less than 150 GiB RAM")
    if ram is not None and os_name == "windows" and ram > 16:
        errors.append("Windows hibernation supports at most 16 GiB RAM")

    if candidate.get("ami_hibernation_support_verified") is not True:
        errors.append("verify that this exact AMI supports hibernation")
    if candidate.get("regional_instance_type_support_verified") is not True:
        errors.append("verify hibernation support for this instance type in the target Region")
    if candidate.get("hibernation_enabled_at_launch") is not True:
        errors.append("hibernation must be enabled when the instance is launched")
    if candidate.get("root_is_ebs") is not True:
        errors.append("the root volume must be EBS-backed")
    root_volume_type = candidate.get("root_volume_type")
    if not isinstance(root_volume_type, str) or root_volume_type not in {"gp2", "gp3", "io1", "io2"}:
        errors.append("the root EBS volume type must be gp2, gp3, io1, or io2")
    if candidate.get("root_is_encrypted") is not True:
        errors.append("the root EBS volume must be encrypted")
    managed_by_auto_scaling = candidate.get("managed_by_auto_scaling")
    if managed_by_auto_scaling is True:
        errors.append("do not hibernate an ordinary Auto Scaling group member")
    elif managed_by_auto_scaling is not False:
        errors.append("managed_by_auto_scaling must be explicitly true or false")
    depends_on_instance_store = candidate.get("depends_on_instance_store")
    if depends_on_instance_store is True:
        errors.append("instance-store data is lost on hibernation; move required state first")
    elif depends_on_instance_store is not False:
        errors.append("depends_on_instance_store must be explicitly true or false")

    if None not in (ram, root, system, reserve):
        minimum = ram + system + reserve
        if root < minimum:
            errors.append(
                f"root volume is {root:g} GiB; supplied RAM, OS/application, and working-space "
                f"needs total {minimum:g} GiB"
            )

    return {
        "status": "needs-aws-verification" if not errors else "not-ready",
        "errors": errors,
        "scope": "local consistency check only; no AWS query, price, or resume test",
        "cost_note": "stopped instances still incur attached EBS storage charges",
    }


def main(argv):
    if len(argv) != 2:
        print(f"Usage: {Path(argv[0]).name} CANDIDATE.json", file=sys.stderr)
        return 2
    try:
        candidate = json.loads(Path(argv[1]).read_text())
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "invalid", "errors": [str(exc)]}, indent=2))
        return 2
    result = assess(candidate)
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "needs-aws-verification" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
