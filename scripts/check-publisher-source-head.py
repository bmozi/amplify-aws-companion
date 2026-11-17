"""Refuse a queued manual publication when main has advanced."""

from __future__ import annotations

import os
import re
import subprocess


def git(*args: str) -> str:
    try:
        return subprocess.run(
            ["git", *args], check=True, capture_output=True, text=True, timeout=20
        ).stdout.strip()
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as error:
        raise SystemExit("Could not verify the current main branch; publication stopped.") from error


def main() -> int:
    expected = os.environ.get("SOURCE_COMMIT", "")
    if not re.fullmatch(r"[0-9a-f]{40}", expected):
        raise SystemExit("Missing exact workflow source commit.")

    if git("rev-parse", "--verify", "HEAD") != expected:
        raise SystemExit("Checked-out source differs from this workflow's source commit.")

    remote = git("ls-remote", "--exit-code", "origin", "refs/heads/main")
    parts = remote.split("\t")
    if len(parts) != 2 or parts[1] != "refs/heads/main" or not re.fullmatch(r"[0-9a-f]{40}", parts[0]):
        raise SystemExit("Could not identify one exact current main branch head.")
    if parts[0] != expected:
        raise SystemExit("Main advanced since this workflow began; review and dispatch the new source.")
    print(f"Current main matches reviewed source {expected}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
