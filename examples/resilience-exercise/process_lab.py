"""Synthetic lost-reply/restart experiment; local processes and SQLite only."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from concurrent.futures import ThreadPoolExecutor
import json
from multiprocessing import Pipe, Process
from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory
from threading import Barrier
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def _rows(database):
    with sqlite3.connect(database, timeout=2) as connection:
        return [dict(zip(("booking_id", "request_id", "customer"), row))
                for row in connection.execute(
                    "SELECT booking_id, request_id, customer FROM bookings ORDER BY booking_id")]


def _worker(database, channel, *, unsafe_retry, delay_selected):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_args):
            pass

        def do_POST(self):
            if self.path != "/book":
                self.send_error(404)
                return
            try:
                size = int(self.headers.get("Content-Length", "0"))
                if not 0 < size <= 256:
                    raise ValueError("invalid size")
                item = json.loads(self.rfile.read(size))
                request_id, customer = item["request_id"], item["customer"]
                if not all(isinstance(value, str) and 0 < len(value) <= 40
                           for value in (request_id, customer)):
                    raise ValueError("invalid fields")
            except (ValueError, KeyError, TypeError):
                self.send_error(400)
                return

            with sqlite3.connect(database, timeout=2) as connection:
                connection.execute("BEGIN IMMEDIATE")
                existing = connection.execute(
                    "SELECT booking_id, customer FROM bookings WHERE request_id = ? ORDER BY booking_id LIMIT 1",
                    (request_id,)).fetchone()
                if existing is not None and existing[1] != customer:
                    connection.rollback()
                    self.send_error(409)
                    return
                if existing is None or unsafe_retry:
                    cursor = connection.execute(
                        "INSERT INTO bookings(request_id, customer) VALUES (?, ?)",
                        (request_id, customer))
                    booking_id = cursor.lastrowid
                else:
                    booking_id = existing[0]
                connection.commit()

            if delay_selected and request_id == "fault-1":
                time.sleep(1.0)
            body = json.dumps({"booking_id": booking_id, "request_id": request_id,
                               "customer": customer}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            try:
                self.wfile.write(body)
            except (BrokenPipeError, ConnectionResetError):
                pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    channel.send(server.server_port)
    channel.close()
    try:
        server.serve_forever()
    finally:
        server.server_close()


def _start_worker(database, *, unsafe_retry, delay_selected):
    parent, child = Pipe(duplex=False)
    process = Process(target=_worker, args=(database, child),
                      kwargs={"unsafe_retry": unsafe_retry,
                              "delay_selected": delay_selected})
    process.start()
    child.close()
    try:
        if not parent.poll(5):
            raise RuntimeError("Local worker did not report its port")
        port = parent.recv()
        return process, f"http://127.0.0.1:{port}"
    except Exception:
        process.terminate()
        process.join(timeout=2)
        raise
    finally:
        parent.close()


def _stop_worker(process):
    if process.is_alive():
        process.terminate()
    process.join(timeout=2)
    if process.is_alive():
        process.kill()
        process.join(timeout=2)
    if process.is_alive():
        raise RuntimeError("Local worker did not stop")


def _book(url, request_id, customer, timeout=2):
    body = json.dumps({"request_id": request_id, "customer": customer}).encode()
    with urlopen(Request(url + "/book", data=body), timeout=timeout) as response:
        return json.loads(response.read())


def run_experiment(*, unsafe_retry=False):
    with TemporaryDirectory(prefix="amplify-a22-") as directory:
        database = str(Path(directory) / "bookings.sqlite3")
        with sqlite3.connect(database) as connection:
            connection.execute("CREATE TABLE bookings (booking_id INTEGER PRIMARY KEY, "
                               "request_id TEXT NOT NULL, customer TEXT NOT NULL)")
            if not unsafe_retry:
                connection.execute("CREATE UNIQUE INDEX one_booking_per_request ON bookings(request_id)")

        first, url = _start_worker(database, unsafe_retry=unsafe_retry, delay_selected=True)
        first_pid = first.pid
        try:
            baseline = _book(url, "baseline", "Maya")
            try:
                _book(url, "fault-1", "Alex", timeout=0.08)
                raise AssertionError("Expected the selected reply timeout")
            except (TimeoutError, URLError):
                timeout_at = time.monotonic()
            # This read uses another SQLite connection in the operator process.
            before_restart = [row for row in _rows(database)
                              if row["request_id"] == "fault-1"]
            if len(before_restart) != 1:
                raise AssertionError("Commit-before-reply precondition was not observed")
        finally:
            _stop_worker(first)

        second, new_url = _start_worker(database, unsafe_retry=unsafe_retry,
                                        delay_selected=False)
        second_pid = second.pid
        try:
            retried = _book(new_url, "fault-1", "Alex")
            try:
                _book(new_url, "fault-1", "Sam")
                customer_conflict_rejected = False
            except HTTPError as error:
                customer_conflict_rejected = error.code == 409
            probes = [_book(new_url, f"after-{n}", "Sam") for n in (1, 2)]
            elapsed = round(time.monotonic() - timeout_at, 4)
            rows = _rows(database)
        finally:
            _stop_worker(second)

        fault_rows = [row for row in rows if row["request_id"] == "fault-1"]
        correct_probes = all(probe["request_id"] == f"after-{n}"
                             for n, probe in zip((1, 2), probes))
        return {
            "baseline_booking": baseline["booking_id"],
            "first_customer_outcome": "timeout",
            "committed_before_worker_stop": len(before_restart) == 1,
            "first_worker_stopped": not first.is_alive(),
            "worker_pids_differ": first_pid != second_pid,
            "retry_booking": retried["booking_id"],
            "customer_conflict_rejected": customer_conflict_rejected,
            "fault_request_records": len(fault_rows),
            "new_probes_correct": correct_probes,
            "observed_timeout_to_second_probe_seconds": elapsed,
            "hypothesis_met": (first_pid != second_pid and len(fault_rows) == 1 and
                               retried["booking_id"] == before_restart[0]["booking_id"] and
                               customer_conflict_rejected and correct_probes),
            "scope": "two local worker processes, one operator process and a same-host SQLite file; not AWS or customer RTO",
        }


def run_concurrent_retry():
    """Race two separate workers against one local transactional request key."""
    with TemporaryDirectory(prefix="amplify-a22-race-") as directory:
        database = str(Path(directory) / "bookings.sqlite3")
        with sqlite3.connect(database) as connection:
            connection.execute("CREATE TABLE bookings (booking_id INTEGER PRIMARY KEY, "
                               "request_id TEXT NOT NULL UNIQUE, customer TEXT NOT NULL)")
        first, first_url = _start_worker(database, unsafe_retry=False, delay_selected=False)
        try:
            second, second_url = _start_worker(database, unsafe_retry=False,
                                                delay_selected=False)
            try:
                start_gate = Barrier(2, timeout=3)

                def send_together(url):
                    start_gate.wait()
                    return _book(url, "race-1", "Alex")

                with ThreadPoolExecutor(max_workers=2) as pool:
                    futures = [pool.submit(send_together, url)
                               for url in (first_url, second_url)]
                    receipts = [future.result(timeout=3) for future in futures]
                rows = _rows(database)
            finally:
                _stop_worker(second)
        finally:
            _stop_worker(first)
        return {"worker_pids_differ": first.pid != second.pid,
                "receipt_ids": [receipt["booking_id"] for receipt in receipts],
                "record_count": len(rows),
                "same_booking": (len(rows) == 1 and
                                 all(receipt["booking_id"] == rows[0]["booking_id"]
                                     for receipt in receipts)),
                "scope": "two same-host local workers, SQLite transaction; not AWS concurrency"}


if __name__ == "__main__":
    print(json.dumps(run_experiment(), indent=2))
