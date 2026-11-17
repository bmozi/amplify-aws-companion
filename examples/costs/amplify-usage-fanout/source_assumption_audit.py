"""Compare two fictional cost inputs with the checked-in Field Lab source.

This is a narrow source-text screen, not a generated-stack or usage inspection.
"""

from decimal import Decimal
import json
from pathlib import Path
import re

from lab import trace


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
FUNCTION = ROOT / "app/amplify/functions/inspect/resource.ts"
BROWSER = ROOT / "app/src/main.tsx"
PLAN = HERE / "smoke-plan.json"


def one_number(pattern: str, source: str, label: str) -> int:
    matches = re.findall(pattern, source)
    if len(matches) != 1:
        raise ValueError(f"Cannot identify one {label} in the checked source; review it manually")
    return int(matches[0])


def audit(plan: dict, function_source: str, browser_source: str) -> dict:
    # Validate all plan fields and action counts through the quantity model.
    quantities = trace(plan)["quantities"]
    memory_mb = one_number(r"\bmemoryMB\s*:\s*(\d+)\s*,", function_source,
                           "function memoryMB declaration")
    upload_mib = one_number(r"\bfile\.size\s*>\s*(\d+)\s*\*\s*1024\s*\*\s*1024\b",
                            browser_source, "browser upload-size check")
    if memory_mb <= 0 or upload_mib <= 0:
        raise ValueError("Source settings must be positive")
    source_memory_gb = Decimal(memory_mb) / Decimal(1024)
    upload_cap_bytes = upload_mib * 1024 * 1024
    plan_memory_gb = Decimal(plan["lambda_memory_gb"])
    plan_upload_bytes = Decimal(plan["bytes_per_upload"])
    invocations = Decimal(quantities["lambda_invocations_proxy"])
    assumed_duration = Decimal(plan["lambda_duration_seconds_per_inspection"])
    uploads = Decimal(quantities["s3_upload_requests_proxy"])
    return {
        "status": "source_and_fictional_assumptions_require_review",
        "source_settings": {
            "function_memory_mb": memory_mb,
            "function_memory_gb_at_1024_mb_per_gb": str(source_memory_gb),
            "browser_upload_limit_mib": upload_mib,
            "browser_upload_limit_bytes": upload_cap_bytes,
        },
        "plan_assumptions": {
            "lambda_memory_gb": str(plan_memory_gb),
            "bytes_per_upload": str(plan_upload_bytes),
            "inspections": str(invocations),
            "assumed_seconds_per_inspection": str(assumed_duration),
            "uploads": str(uploads),
        },
        "changed_cases": {
            "lambda_gb_seconds_with_source_memory_and_assumed_duration":
                str(invocations * source_memory_gb * assumed_duration),
            "s3_added_gb_if_every_planned_upload_reaches_browser_cap":
                str(uploads * upload_cap_bytes / Decimal(1000000000)),
        },
        "plan_memory_differs_from_source": plan_memory_gb != source_memory_gb,
        "plan_upload_bytes_below_browser_cap": plan_upload_bytes < upload_cap_bytes,
        "can_approve_publisher_estimate": False,
        "scope": "Static source-text check and fictional changed cases only; deployed settings, actual file sizes, duration, service work, transfer, credit and total cost unobserved",
    }


def main() -> None:
    print(json.dumps(audit(json.loads(PLAN.read_text()), FUNCTION.read_text(),
                           BROWSER.read_text()), indent=2))


if __name__ == "__main__":
    main()
