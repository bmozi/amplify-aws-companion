"""Local parallel-completion checkpoint lesson; no AWS or distributed consumer protocol."""
import argparse
from contextlib import closing
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import time


EVENTS = [
    {"position": 1, "id": "sale-a", "cents": 1000},
    {"position": 2, "id": "sale-b", "cents": 2000},
    {"position": 3, "id": "sale-c", "cents": 3000},
]
CRASH_EXIT = 73


def prepare(root):
    root.mkdir()
    (root / "source.json").write_text(json.dumps(EVENTS))
    with closing(sqlite3.connect(root / "ledger.db")) as db:
        db.executescript(
            "CREATE TABLE ledger (id TEXT PRIMARY KEY, body TEXT NOT NULL, cents INTEGER NOT NULL);"
            "CREATE TABLE completed (position INTEGER PRIMARY KEY, event_id TEXT NOT NULL);"
            "CREATE TABLE progress (singleton INTEGER PRIMARY KEY CHECK(singleton=1), position INTEGER NOT NULL);"
            "INSERT INTO progress VALUES (1,0);"
        )


def snapshot(root):
    with closing(sqlite3.connect(root / "ledger.db")) as db:
        progress = db.execute("SELECT position FROM progress WHERE singleton=1").fetchone()[0]
        completed = [x[0] for x in db.execute("SELECT position FROM completed ORDER BY position")]
        ids = [x[0] for x in db.execute("SELECT id FROM ledger ORDER BY id")]
        total = db.execute("SELECT COALESCE(SUM(cents),0) FROM ledger").fetchone()[0]
    return {"progress": progress, "completed": completed, "ids": ids, "cents": total}


def apply(root, position, mode):
    events = json.loads((root / "source.json").read_text())
    event = events[position - 1]
    assert event["position"] == position
    body = json.dumps(event, sort_keys=True, separators=(",", ":"))
    with closing(sqlite3.connect(root / "ledger.db", timeout=5)) as db:
        db.execute("BEGIN IMMEDIATE")
        prior_position = db.execute(
            "SELECT event_id FROM completed WHERE position=?", (position,)
        ).fetchone()
        if prior_position:
            if prior_position[0] != event["id"]:
                raise ValueError("source position changed identity")
            return "already_completed"
        prior_effect = db.execute("SELECT body FROM ledger WHERE id=?", (event["id"],)).fetchone()
        if prior_effect:
            if prior_effect[0] != body:
                raise ValueError("business identity changed content")
            outcome = "duplicate_business_identity"
        else:
            db.execute("INSERT INTO ledger VALUES (?,?,?)", (event["id"], body, event["cents"]))
            outcome = "created"
        db.execute("INSERT INTO completed VALUES (?,?)", (position, event["id"]))
        current = db.execute("SELECT position FROM progress WHERE singleton=1").fetchone()[0]
        if mode == "naive":
            current = max(current, position)
        else:
            # Only the uninterrupted prefix can be claimed as complete.
            while db.execute("SELECT 1 FROM completed WHERE position=?", (current + 1,)).fetchone():
                current += 1
        db.execute("UPDATE progress SET position=? WHERE singleton=1", (current,))
        db.commit()
    return outcome


def child_command(root, position, mode, wait):
    args = [sys.executable, str(Path(__file__).resolve()), "--worker", str(root),
            "--position", str(position), "--mode", mode]
    if wait:
        args.append("--wait")
    return args


def launch(root, position, mode):
    result = subprocess.run(child_command(root, position, mode, False),
                            capture_output=True, text=True, timeout=10)
    assert result.returncode == 0, (result.returncode, result.stdout, result.stderr)
    return json.loads(result.stdout)["outcome"]


def run_case(root, mode):
    prepare(root)
    assert launch(root, 1, mode) == "created"
    stalled = subprocess.Popen(child_command(root, 2, mode, True),
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        deadline = time.monotonic() + 5
        while not (root / "worker-2-ready").exists():
            if stalled.poll() is not None or time.monotonic() >= deadline:
                raise AssertionError("second worker never reached its stall point")
            time.sleep(0.02)
        assert launch(root, 3, mode) == "created"
        (root / "abort-worker-2").write_text("abort")
        stdout, stderr = stalled.communicate(timeout=5)
        assert stalled.returncode == CRASH_EXIT, (stalled.returncode, stdout, stderr)
    finally:
        if stalled.poll() is None:
            stalled.kill()
            stalled.communicate(timeout=5)
        if stalled.stdout:
            stalled.stdout.close()
        if stalled.stderr:
            stalled.stderr.close()
    after_gap = snapshot(root)
    assert after_gap["completed"] == [1, 3]
    assert after_gap["ids"] == ["sale-a", "sale-c"]
    assert after_gap["cents"] == 4000
    assert after_gap["progress"] == (1 if mode == "safe" else 3)

    restart_outcomes = []
    for position in range(after_gap["progress"] + 1, len(EVENTS) + 1):
        restart_outcomes.append({"position": position, "outcome": launch(root, position, mode)})
    after_restart = snapshot(root)
    if mode == "safe":
        assert restart_outcomes == [
            {"position": 2, "outcome": "created"},
            {"position": 3, "outcome": "already_completed"},
        ]
        assert after_restart == {
            "progress": 3, "completed": [1, 2, 3],
            "ids": ["sale-a", "sale-b", "sale-c"], "cents": 6000,
        }
    else:
        assert restart_outcomes == []
        assert after_restart == after_gap
    return {"after_gap": after_gap, "restart_outcomes": restart_outcomes,
            "after_restart": after_restart}


def main():
    if not __debug__:
        raise SystemExit("Run without Python optimization")
    with tempfile.TemporaryDirectory(prefix="amplify-parallel-checkpoint-") as temporary:
        root = Path(temporary)
        safe = run_case(root / "safe", "safe")
        naive = run_case(root / "naive", "naive")
        print(json.dumps({
            "safe_frontier": safe, "naive_high_watermark": naive,
            "scope": "two overlapping local worker processes and one SQLite file per case; "
                     "trusted ordered fixture, no distributed stream, lease or external side effect",
        }, indent=2))
    assert not root.exists()
    print("Removed temporary source, ledger and progress files.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--worker", type=Path)
    parser.add_argument("--position", type=int, choices=[1, 2, 3])
    parser.add_argument("--mode", choices=["safe", "naive"], default="safe")
    parser.add_argument("--wait", action="store_true")
    args = parser.parse_args()
    if args.worker:
        if args.wait:
            (args.worker / "worker-2-ready").write_text("ready")
            deadline = time.monotonic() + 5
            while not (args.worker / "abort-worker-2").exists():
                if time.monotonic() >= deadline:
                    raise SystemExit("stall controller timed out")
                time.sleep(0.02)
            os._exit(CRASH_EXIT)
        print(json.dumps({"outcome": apply(args.worker, args.position, args.mode)}))
    else:
        main()
