"""Read a real disposable Terraform plan through a small proposal-review gate."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


ADDRESS = "terraform_data.delivery_proposal"
BASELINE = {
    "owner": "media-team",
    "module_version": "1.2.0",
    "action": "s3:GetObject",
    "resource_scope": "arn:aws:s3:::approved-exhibit/*",
    "pause_auto_builds": False,
}


def assess(plan, expected):
    """Classify only this teaching record; never evaluate real IAM permissions."""
    changes = plan.get("resource_changes")
    if not isinstance(changes, list) or len(changes) != 1:
        return "reject", "Expected exactly one proposal change"
    change = changes[0]
    if change.get("address") != ADDRESS:
        return "reject", "Unexpected resource address"
    detail = change.get("change", {})
    if detail.get("actions") not in (["create"], ["update"], ["no-op"]):
        return "reject", "Deletion or replacement needs a separate review"
    proposed = detail.get("after", {}).get("input")
    if not isinstance(proposed, dict) or set(proposed) != set(BASELINE):
        return "reject", "Proposed fields are missing or unknown"
    if proposed["owner"] != expected["owner"]:
        return "reject", "Another owner controls this proposal"
    if proposed["action"] != "s3:GetObject" or proposed["resource_scope"] != BASELINE["resource_scope"]:
        return "reject", "The requested action or resource scope exceeds this exercise's contract"
    if proposed["module_version"] != expected["module_version"]:
        return "review", "Module version changed; review consumers and migration"
    if proposed["pause_auto_builds"] is not expected["pause_auto_builds"]:
        return "review", "Emergency pause differs from reviewed intent"
    return "pass", "Proposal matches this exercise's reviewed intent"


def run(folder):
    if sys.flags.optimize:
        raise RuntimeError("Run without Python optimization: this lab checks its observations with assertions")
    shutil.copyfile(Path(__file__).with_name("main.tf"), folder / "main.tf")
    cli = folder / "terraform.rc"
    cli.write_text("disable_checkpoint = true\n")
    env = {key: value for key, value in os.environ.items()
           if not key.startswith(("TF_", "AWS_"))}
    env.update(TF_CLI_CONFIG_FILE=str(cli), TF_IN_AUTOMATION="1", CHECKPOINT_DISABLE="1")

    def tf(*args):
        completed = subprocess.run(["terraform", *args], cwd=folder, env=env,
                                   text=True, capture_output=True, timeout=60)
        if completed.returncode:
            raise RuntimeError(f"Terraform {args[0]} failed: {completed.stderr}\n{completed.stdout}")
        return completed.stdout

    def plan(name, values):
        arguments = ["plan", "-input=false", "-no-color", f"-out={name}"]
        arguments += [f"-var={key}={str(value).lower() if isinstance(value, bool) else value}"
                      for key, value in values.items()]
        tf(*arguments)
        return json.loads(tf("show", "-json", name))

    def selected_state():
        state = json.loads(tf("show", "-json"))
        resources = state["values"]["root_module"]["resources"]
        assert len(resources) == 1 and resources[0]["address"] == ADDRESS
        return resources[0]["values"]["output"]

    def actions(planned):
        changes = planned["resource_changes"]
        assert len(changes) == 1 and changes[0]["address"] == ADDRESS
        return changes[0]["change"]["actions"]

    tf("init", "-backend=false", "-input=false", "-no-color")
    tf("validate", "-no-color")

    first = plan("baseline.tfplan", BASELINE)
    assert actions(first) == ["create"] and assess(first, BASELINE)[0] == "pass"
    tf("apply", "-input=false", "-no-color", "baseline.tfplan")
    assert selected_state() == BASELINE
    unchanged = plan("unchanged.tfplan", BASELINE)
    assert actions(unchanged) == ["no-op"] and assess(unchanged, BASELINE)[0] == "pass"

    broad = {**BASELINE, "action": "s3:*", "resource_scope": "*"}
    assert assess(plan("broad.tfplan", broad), BASELINE)[0] == "reject"
    other_owner = {**BASELINE, "owner": "another-team"}
    assert assess(plan("owner.tfplan", other_owner), BASELINE)[0] == "reject"
    assert selected_state() == BASELINE

    emergency = {**BASELINE, "pause_auto_builds": True}
    emergency_plan = plan("emergency.tfplan", emergency)
    assert actions(emergency_plan) == ["update"]
    assert assess(emergency_plan, BASELINE)[0] == "review"
    assert selected_state() == BASELINE
    reviewed = {**BASELINE, "pause_auto_builds": True}
    assert assess(emergency_plan, reviewed)[0] == "pass"
    tf("apply", "-input=false", "-no-color", "emergency.tfplan")
    assert selected_state() == reviewed
    reconciled = plan("reconciled.tfplan", reviewed)
    assert actions(reconciled) == ["no-op"] and assess(reconciled, reviewed)[0] == "pass"
    return {
        "baseline": "applied to disposable local state",
        "broad_permission": "rejected without apply",
        "ownership_conflict": "rejected without apply",
        "emergency_pause": "review required, then approved intent applied",
        "reconciled_plan": "no-op proposal",
        "scope": "terraform_data only; no AWS IAM, Amplify, remote state or customer path",
    }


if __name__ == "__main__":
    with tempfile.TemporaryDirectory(prefix="amplify-governed-delivery-") as temporary:
        directory = Path(temporary)
        result = run(directory)
    result["temporary_directory_removed"] = not directory.exists()
    assert result["temporary_directory_removed"]
    print(json.dumps(result, indent=2))
