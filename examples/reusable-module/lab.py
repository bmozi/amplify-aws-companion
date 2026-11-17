"""Exercise two versioned local Terraform module consumers and isolated state."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


SOURCE = Path(__file__).parent
ADDRESS = "module.exhibit.terraform_data.contract"


def run(folder):
    if sys.flags.optimize:
        raise RuntimeError("Run without Python optimization: this lab checks observations with assertions")
    for name in ("modules", "practice_consumer", "preview"):
        shutil.copytree(SOURCE / name, folder / name)
    cli = folder / "terraform.rc"
    cli.write_text("disable_checkpoint = true\n")
    env = {key: value for key, value in os.environ.items()
           if not key.startswith(("TF_", "AWS_"))}
    env.update(TF_CLI_CONFIG_FILE=str(cli), TF_IN_AUTOMATION="1", CHECKPOINT_DISABLE="1")

    def tf(consumer, *args, allowed=(0,)):
        completed = subprocess.run(["terraform", *args], cwd=folder / consumer, env=env,
                                   text=True, capture_output=True, timeout=60)
        if completed.returncode not in allowed:
            raise RuntimeError(f"{consumer}: terraform {args[0]} failed: {completed.stderr}\n{completed.stdout}")
        return completed

    def plan(consumer, name):
        tf(consumer, "plan", "-input=false", "-no-color", f"-out={name}")
        data = json.loads(tf(consumer, "show", "-json", name).stdout)
        changes = data["resource_changes"]
        assert len(changes) == 1 and changes[0]["address"] == ADDRESS
        return changes[0]["change"]["actions"]

    def state(consumer):
        raw = json.loads(tf(consumer, "state", "pull").stdout)
        assert raw["resources"][0]["module"] == "module.exhibit"
        resource = raw["resources"][0]
        assert resource["type"] == "terraform_data" and resource["name"] == "contract"
        entry = resource["instances"][0]["attributes"]
        return raw["lineage"], entry["id"], entry["output"]["value"]

    for consumer in ("practice_consumer", "preview"):
        tf(consumer, "init", "-backend=false", "-input=false", "-no-color")
        tf(consumer, "validate", "-no-color")
        assert plan(consumer, "first.tfplan") == ["create"]
        tf(consumer, "apply", "-input=false", "-no-color", "first.tfplan")

    practice_before = state("practice_consumer")
    preview_before = state("preview")
    assert practice_before[0] != preview_before[0]
    assert practice_before[1] != preview_before[1]
    assert practice_before[2]["owner"] == "practice-team"
    assert preview_before[2]["owner"] == "preview-team"
    assert practice_before[2]["schema_version"] == preview_before[2]["schema_version"] == 1
    assert plan("practice_consumer", "unchanged.tfplan") == ["no-op"]
    assert plan("preview", "unchanged.tfplan") == ["no-op"]

    practice = folder / "practice_consumer" / "main.tf"
    candidate = practice.read_text().replace("../modules/exhibit/v1", "../modules/exhibit/v2")
    assert candidate != practice.read_text()
    practice.write_text(candidate)
    tf("practice_consumer", "init", "-backend=false", "-input=false", "-no-color")
    missing = tf("practice_consumer", "validate", "-no-color", allowed=(1,))
    assert "retention_days" in missing.stderr + missing.stdout
    assert state("practice_consumer") == practice_before

    approved_source = candidate.replace('  collection = "practice-exhibit"',
                                        '  collection = "practice-exhibit"\n  retention_days = 7')
    assert approved_source != candidate
    practice.write_text(approved_source.replace("retention_days = 7", "retention_days = 0"))
    invalid = tf("practice_consumer", "plan", "-input=false", "-no-color", allowed=(1,))
    assert "Choose a whole-day teaching retention" in invalid.stderr + invalid.stdout
    assert state("practice_consumer") == practice_before
    practice.write_text(approved_source)
    tf("practice_consumer", "validate", "-no-color")
    assert plan("practice_consumer", "upgrade.tfplan") == ["update"]
    assert state("practice_consumer") == practice_before
    assert plan("preview", "still-v1.tfplan") == ["no-op"]
    tf("practice_consumer", "apply", "-input=false", "-no-color", "upgrade.tfplan")
    practice_after = state("practice_consumer")
    assert practice_after[:2] == practice_before[:2]
    assert practice_after[2]["schema_version"] == 2
    assert practice_after[2]["retention_days"] == 7
    assert state("preview") == preview_before
    assert plan("practice_consumer", "reconciled.tfplan") == ["no-op"]
    assert plan("preview", "still-v1-again.tfplan") == ["no-op"]
    return {
        "two_consumers": "separate local state lineages and object IDs",
        "missing_or_invalid_v2_input": "rejected; practice state unchanged",
        "practice_upgrade": "inspected update preserves local object ID",
        "preview": "remains on v1 with no-op plan",
        "scope": "local versioned paths and terraform_data; no registry, AWS, remote backend or data retention",
    }


if __name__ == "__main__":
    with tempfile.TemporaryDirectory(prefix="amplify-reusable-module-") as temporary:
        directory = Path(temporary)
        result = run(directory)
    result["temporary_directory_removed"] = not directory.exists()
    assert result["temporary_directory_removed"]
    print(json.dumps(result, indent=2))
