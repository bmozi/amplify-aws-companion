"""Observe a Terraform state lock with disposable local state only."""

import json
import os
from pathlib import Path
import subprocess
import tempfile
import time


CONFIG = '''terraform {
  required_version = ">= 1.6"
}

resource "terraform_data" "lesson" {
  input = "one local record"

  provisioner "local-exec" {
    command     = "touch lock-held; sleep 8"
    working_dir = "."
  }
}
'''


def run(directory: Path, environment: dict[str, str], *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["terraform", f"-chdir={directory}", *args],
        env=environment, input="", capture_output=True, text=True, timeout=25,
    )


def require_success(result: subprocess.CompletedProcess[str], step: str) -> None:
    if result.returncode:
        raise RuntimeError(f"{step} failed: {result.stderr[-1200:]}")


def actions(directory: Path, environment: dict[str, str], plan: str) -> list[str]:
    result = run(directory, environment, "show", "-json", plan)
    require_success(result, f"inspect {plan}")
    changes = json.loads(result.stdout).get("resource_changes", [])
    if len(changes) != 1 or changes[0]["address"] != "terraform_data.lesson":
        raise AssertionError(f"unexpected resource changes in {plan}")
    return changes[0]["change"]["actions"]


def main() -> None:
    # No provider or remote backend is installed. Inherited Terraform overrides
    # and AWS credentials are kept out of every subprocess.
    environment = {key: value for key, value in os.environ.items()
                   if not key.startswith(("TF_", "AWS_"))}
    environment["TF_IN_AUTOMATION"] = "1"
    with tempfile.TemporaryDirectory(prefix="amplify-local-lock-") as temporary:
        directory = Path(temporary)
        (directory / "main.tf").write_text(CONFIG)
        require_success(run(directory, environment, "init", "-backend=false", "-input=false", "-no-color"), "init")
        holder = subprocess.Popen(
            ["terraform", f"-chdir={directory}", "apply", "-auto-approve", "-input=false", "-no-color"],
            env=environment, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        try:
            deadline = time.monotonic() + 4
            while not (directory / "lock-held").exists() and holder.poll() is None and time.monotonic() < deadline:
                time.sleep(0.02)
            if not (directory / "lock-held").exists() or holder.poll() is not None:
                raise AssertionError("the first local apply did not reach the controlled hold")

            blocked = run(directory, environment, "plan", "-lock-timeout=0s", "-input=false", "-no-color")
            if blocked.returncode == 0 or "Error acquiring the state lock" not in blocked.stderr:
                raise AssertionError("the second writer was not refused by the local state lock")

            # A deliberately unsafe *read-only plan* shows what bypassing the
            # lock can see. It is inspected, never applied.
            bypass = run(directory, environment, "plan", "-lock=false", "-input=false", "-no-color",
                         "-out=unsafe.tfplan")
            require_success(bypass, "bypassing-plan negative control")
            during = actions(directory, environment, "unsafe.tfplan")
            if during != ["create"]:
                raise AssertionError(f"expected a stale create proposal, got {during}")

            stdout, stderr = holder.communicate(timeout=15)
            if holder.returncode:
                raise RuntimeError(f"first apply failed: {(stdout + stderr)[-1200:]}")
            after = run(directory, environment, "plan", "-lock-timeout=0s", "-input=false", "-no-color",
                        "-out=after.tfplan")
            require_success(after, "plan after lock release")
            later = actions(directory, environment, "after.tfplan")
            if later != ["no-op"]:
                raise AssertionError(f"expected a no-op after committed apply, got {later}")
            print(json.dumps({
                "scope": "disposable local terraform_data and local backend only",
                "contender_refused_during_apply": True,
                "bypass_plan_only_during_apply": during,
                "normal_plan_after_release": later,
                "bypass_plan_applied": False,
            }, indent=2))
        finally:
            if holder.poll() is None:
                holder.terminate()
                try:
                    holder.communicate(timeout=8)
                except subprocess.TimeoutExpired:
                    holder.kill()
                    holder.communicate(timeout=5)


if __name__ == "__main__":
    main()
