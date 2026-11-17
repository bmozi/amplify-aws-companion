"""Observe local in-flight work on both sides of a stop deadline.

Runs two instances of the standard-library teaching service on loopback.
No Docker, AWS, persistence, or billing is involved.
"""
from concurrent.futures import ThreadPoolExecutor
from http.client import RemoteDisconnected
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request


SERVICE = Path(__file__).with_name("service.py")


def free_loopback_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def get_json(url):
    with urllib.request.urlopen(url, timeout=8) as response:
        return response.status, json.load(response)


def wait_for_state(url, key, timeout=5):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            if get_json(url + "/state")[1][key]:
                return
        except (OSError, urllib.error.URLError):
            pass
        time.sleep(0.02)
    raise AssertionError(f"{key} never became true")


def run_case(duration_ms, stop_deadline):
    port = free_loopback_port()
    release = f"deadline-{duration_ms}"
    env = dict(os.environ, BIND_HOST="127.0.0.1", PORT=str(port), RELEASE=release)
    process = subprocess.Popen(
        [sys.executable, "-u", str(SERVICE)], env=env,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
    )
    lines = []
    reader = threading.Thread(target=lambda: lines.extend(process.stdout), daemon=True)
    reader.start()
    url = f"http://127.0.0.1:{port}"
    try:
        ready_by = time.monotonic() + 5
        while True:
            try:
                if get_json(url + "/ready") == (200, {"ready": True}):
                    break
            except (OSError, urllib.error.URLError):
                pass
            if time.monotonic() >= ready_by:
                raise AssertionError("service did not become ready")
            time.sleep(0.02)
        with ThreadPoolExecutor(max_workers=1) as pool:
            client = pool.submit(get_json, url + f"/work?duration_ms={duration_ms}")
            wait_for_state(url, "working")
            process.terminate()
            forced = False
            try:
                process.wait(timeout=stop_deadline)
            except subprocess.TimeoutExpired:
                forced = True
                process.kill()
                process.wait(timeout=3)
            try:
                result = client.result(timeout=3)
                client_outcome = {"response": result}
            except (RemoteDisconnected, ConnectionResetError, urllib.error.URLError, BrokenPipeError) as exc:
                client_outcome = {"disconnected": type(exc).__name__}
        reader.join(timeout=2)
        log = "".join(lines)
        assert log.index("work_started") < log.index("termination_received")
        if forced:
            assert process.returncode == -9
            assert "work_completed" not in log and "graceful_stop" not in log
            assert "disconnected" in client_outcome
        else:
            assert process.returncode == 0
            assert client_outcome == {"response": (200, {"release": release, "work_ms": duration_ms})}
            assert log.index("termination_received") < log.index("work_completed") < log.index("graceful_stop")
        return {
            "work_ms": duration_ms, "stop_deadline_s": stop_deadline,
            "forced_kill": forced, "exit_code": process.returncode,
            "client_outcome": client_outcome,
            "observed_log_order": [x.strip() for x in lines if
                                   x.startswith(("work_started", "termination_received",
                                                 "work_completed", "graceful_stop"))],
        }
    finally:
        if process.poll() is None:
            process.kill()
            process.wait(timeout=3)
        reader.join(timeout=2)
        if process.stdout:
            process.stdout.close()


def main():
    if not __debug__:
        raise SystemExit("Run without Python optimization")
    short = run_case(400, 3)
    long = run_case(4000, 1)
    assert not short["forced_kill"] and long["forced_kill"]
    print(json.dumps({
        "cases": [short, long],
        "scope": "local loopback process stop; no Docker scheduler, customer result or durable work",
    }, indent=2))


if __name__ == "__main__":
    main()
