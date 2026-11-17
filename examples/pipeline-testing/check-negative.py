"""Verify that injected defects fail at their intended pipeline gate."""
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
CASES = {
    "consent-bypass": "GATE FAILED: integration",
    "wrong-message": "GATE FAILED: acceptance",
}

for fault, expected in CASES.items():
    result = subprocess.run(
        [sys.executable, "examples/pipeline-testing/lab.py", "--fault", fault],
        cwd=BASE,
        text=True,
        capture_output=True,
        timeout=15,
    )
    output = result.stdout + result.stderr
    assert result.returncode == 1, f"{fault} returned {result.returncode}, expected 1"
    assert expected in output, f"{fault} failed at an unexpected gate:\n{output}"
    print(f"{fault}: rejected at expected gate")
