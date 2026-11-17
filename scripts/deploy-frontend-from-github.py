"""Publish one prebuilt static bundle through an assumed GitHub OIDC role."""

from __future__ import annotations

if __name__ == '__main__':
    raise SystemExit('Inspection-only source: cloud commands are disabled in this companion. See reader/COMMAND-SCOPE.md.')


import hashlib
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from zipfile import BadZipFile, ZipFile


EXPECTED_ROLE = "AmplifyLabGitHubPublisher"
EXPECTED_BRANCH = "lab"
REGION = "us-east-2"
MARKER = "deployment.json"


class NoMarkerRedirect(urllib.request.HTTPRedirectHandler):
    """A different URL serving the right JSON is not proof of this branch."""

    def redirect_request(self, request, fp, code, msg, headers, newurl):
        return None


def aws(*arguments: str) -> dict:
    result = subprocess.run(
        ["aws", *arguments, "--region", REGION, "--output", "json", "--no-cli-pager"],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def expected_marker(archive: Path) -> dict[str, str]:
    commit = os.environ.get("SOURCE_COMMIT", "")
    run_id = os.environ.get("WORKFLOW_RUN_ID", "")
    if not re.fullmatch(r"[0-9a-f]{40}", commit) or not re.fullmatch(r"[0-9]+", run_id):
        raise SystemExit("Missing exact source or workflow run identity.")
    expected = {"source_commit": commit, "workflow_run_id": run_id}
    expected_digest = os.environ.get("EXPECTED_ARCHIVE_SHA256", "")
    if not re.fullmatch(r"[0-9a-f]{64}", expected_digest):
        raise SystemExit("Missing build job archive digest.")
    with archive.open("rb") as source:
        actual_digest = hashlib.file_digest(source, "sha256").hexdigest()
    if actual_digest != expected_digest:
        raise SystemExit("Frontend archive digest differs from the build job output.")
    try:
        with ZipFile(archive) as contents:
            names = contents.namelist()
            if len(names) != len(set(names)) or "index.html" not in names:
                raise SystemExit("Frontend archive has duplicate files or no index.html.")
            if any(
                name.startswith("/") or "\\" in name or any(part in {"", ".", ".."} for part in name.split("/"))
                for name in names
            ):
                raise SystemExit("Frontend archive has an unsafe file path.")
            if names.count(MARKER) != 1 or contents.getinfo(MARKER).file_size > 4096:
                raise SystemExit("Frontend archive has no single valid deployment marker.")
            observed = json.loads(contents.read(MARKER))
    except (BadZipFile, KeyError, ValueError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise SystemExit("Frontend archive has no readable deployment marker.") from error
    if observed != expected:
        raise SystemExit("Frontend archive does not match this source commit and workflow run.")
    return expected


def read_direct_marker(url: str, expected: dict[str, str]) -> bool:
    """Accept only the requested URL's own 200 response and exact JSON marker."""
    request = urllib.request.Request(url, headers={"Cache-Control": "no-cache"})
    opener = urllib.request.build_opener(NoMarkerRedirect())
    try:
        with opener.open(request, timeout=15) as response:
            return (response.status == 200 and response.geturl() == url and
                    json.loads(response.read(4097)) == expected)
    except (urllib.error.URLError, ValueError, UnicodeDecodeError, json.JSONDecodeError):
        return False


def verify_hosted_marker(app_id: str, branch: str, expected: dict[str, str]) -> bool:
    url = f"https://{branch}.{app_id}.amplifyapp.com/{MARKER}?run={expected['workflow_run_id']}"
    for attempt in range(6):
        if read_direct_marker(url, expected):
            return True
        if attempt < 5:
            time.sleep(5)
    return False


def main() -> int:
    archive = Path(sys.argv[1]) if len(sys.argv) == 2 else None
    app_id = os.environ.get("AWS_LAB_AMPLIFY_APP_ID", "")
    branch = os.environ.get("AWS_LAB_AMPLIFY_BRANCH", "")
    expected_account = os.environ.get("AWS_LAB_EXPECTED_ACCOUNT_ID", "")
    expected_role = os.environ.get("AWS_LAB_EXPECTED_ROLE_NAME", "")
    if archive is None or not archive.is_file() or archive.stat().st_size == 0:
        raise SystemExit("Supply the nonempty frontend ZIP produced by the build job.")
    if not re.fullmatch(r"d[a-z0-9]+", app_id):
        raise SystemExit("Set AWS_LAB_AMPLIFY_APP_ID to the reviewed app ID.")
    if not re.fullmatch(r"[0-9]{12}", expected_account):
        raise SystemExit("Set AWS_LAB_EXPECTED_ACCOUNT_ID to the reviewed account ID.")
    if branch != EXPECTED_BRANCH:
        raise SystemExit("This workflow is limited to the reviewed lab branch.")
    if expected_role != EXPECTED_ROLE:
        raise SystemExit("The expected publisher role name does not match.")
    marker = expected_marker(archive)

    identity = aws("sts", "get-caller-identity")
    arn = identity.get("Arn", "")
    if identity.get("Account") != expected_account or not re.fullmatch(
        rf"arn:aws:sts::{expected_account}:assumed-role/{re.escape(EXPECTED_ROLE)}/[^/]+",
        arn,
    ):
        raise SystemExit("Refusing publication: caller is not the reviewed publisher role in the expected account.")

    response = aws("amplify", "create-deployment", "--app-id", app_id, "--branch-name", branch)
    upload_url = response.get("zipUploadUrl", "")
    job_id = response.get("jobId", "")
    if not upload_url or not re.fullmatch(r"[0-9]+", job_id):
        raise SystemExit("Amplify did not return the expected deployment upload details.")

    request = urllib.request.Request(
        upload_url,
        data=archive.read_bytes(),
        method="PUT",
        headers={"Content-Type": "application/zip"},
    )
    try:
        with urllib.request.urlopen(request, timeout=90) as upload:
            if upload.status != 200:
                raise SystemExit(f"Amplify upload returned HTTP {upload.status}.")
    except urllib.error.HTTPError as error:
        raise SystemExit(f"Amplify upload returned HTTP {error.code}.") from None
    except urllib.error.URLError:
        raise SystemExit("Amplify upload failed; the temporary upload URL was not logged.") from None

    aws(
        "amplify",
        "start-deployment",
        "--app-id",
        app_id,
        "--branch-name",
        branch,
        "--job-id",
        job_id,
    )
    for _ in range(60):
        job = aws("amplify", "get-job", "--app-id", app_id, "--branch-name", branch, "--job-id", job_id)
        summary = job["job"]["summary"]
        status = summary["status"]
        print(f"Amplify hosting job {job_id}: {status}", flush=True)
        if status in {"SUCCEED", "FAILED", "CANCELLED"}:
            if status != "SUCCEED":
                return 1
            if not verify_hosted_marker(app_id, branch, marker):
                raise SystemExit("Amplify job succeeded, but the hosted source/run marker was not verified.")
            print(f"Published to https://{branch}.{app_id}.amplifyapp.com", flush=True)
            return 0
        time.sleep(10)

    raise SystemExit(f"Timed out waiting for Amplify hosting job {job_id}.")


if __name__ == "__main__":
    raise SystemExit(main())
