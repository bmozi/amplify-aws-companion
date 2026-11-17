"""Bounded loopback HTTP fault experiment with synthetic bookings only."""

from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import threading
import time
from urllib.error import URLError
from urllib.request import Request, urlopen


WORKER = "booking-lab-1"


class BookingState:
    def __init__(self, unsafe_retry=False):
        self.lock = threading.Lock()
        self.rows = []
        self.delay_seconds = 0.0
        self.unsafe_retry = unsafe_retry
        self.fault_started = None
        self.fault_limit_seconds = 0.0
        self.attempts = 0
        self.max_attempts = 0

    def _expire_if_due(self):
        if self.fault_started is not None and time.monotonic() - self.fault_started >= self.fault_limit_seconds:
            self.delay_seconds = 0.0
            self.fault_started = None

    def start_fault(self, targets, *, observer_age_seconds, recovery_ready,
                    delay_seconds=0.2, duration_seconds=1.0, max_attempts=6):
        if targets != [WORKER]:
            raise ValueError("Fault target must resolve to exactly the named lab worker")
        if observer_age_seconds < 0 or observer_age_seconds > 20 or not recovery_ready:
            raise ValueError("Fresh observer and recovery operator are required")
        if not (0 < delay_seconds <= 0.25 and 0 < duration_seconds <= 60 and 0 < max_attempts <= 60):
            raise ValueError("Fault duration, delay and attempt count must be bounded")
        with self.lock:
            if self.fault_started is not None:
                raise ValueError("Fault already active")
            self.delay_seconds = delay_seconds
            self.fault_started = time.monotonic()
            self.fault_limit_seconds = duration_seconds
            self.max_attempts = max_attempts
            self.attempts = 0

    def stop_fault(self):
        with self.lock:
            self.delay_seconds = 0.0
            self.fault_started = None

    def accept(self, request_id, customer):
        with self.lock:
            self._expire_if_due()
            self.attempts += 1
            if self.fault_started is not None and self.attempts > self.max_attempts:
                self.delay_seconds = 0.0
                self.fault_started = None
            existing = next((row for row in self.rows if row["request_id"] == request_id), None)
            if existing is not None and existing["customer"] != customer:
                return 409, {"error": "request identity reused for different customer"}, 0.0
            if existing is None or self.unsafe_retry:
                existing = {"booking_id": len(self.rows) + 1, "request_id": request_id,
                            "customer": customer}
                self.rows.append(existing)
            return 200, dict(existing), self.delay_seconds

    def snapshot(self):
        with self.lock:
            self._expire_if_due()
            return {"rows": [dict(row) for row in self.rows],
                    "fault_active": self.fault_started is not None,
                    "attempts": self.attempts}


@contextmanager
def local_server(state):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_arguments):
            pass

        def respond(self, code, payload):
            body = json.dumps(payload).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            try:
                self.wfile.write(body)
            except (BrokenPipeError, ConnectionResetError):
                pass  # The timed-out caller has gone; the accepted effect remains.

        def do_POST(self):
            if self.path != "/book":
                self.respond(404, {"error": "unknown path"})
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if not 0 < length <= 512:
                    raise ValueError("invalid length")
                item = json.loads(self.rfile.read(length))
                request_id, customer = item["request_id"], item["customer"]
                if not all(isinstance(value, str) and 0 < len(value) <= 40 for value in (request_id, customer)):
                    raise ValueError("invalid fields")
            except (ValueError, KeyError, TypeError, json.JSONDecodeError):
                self.respond(400, {"error": "invalid synthetic booking"})
                return
            code, payload, delay = state.accept(request_id, customer)
            if delay:
                time.sleep(delay)
            self.respond(code, payload)

        def do_GET(self):
            if self.path == "/audit":
                self.respond(200, state.snapshot())
            else:
                self.respond(404, {"error": "unknown path"})

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        state.stop_fault()
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def book(url, request_id, customer, timeout=1.0):
    body = json.dumps({"request_id": request_id, "customer": customer}).encode()
    request = Request(url + "/book", data=body, headers={"Content-Type": "application/json"})
    with urlopen(request, timeout=timeout) as response:
        return json.loads(response.read())


def audit(url):
    with urlopen(url + "/audit", timeout=1.0) as response:
        return json.loads(response.read())


def run_experiment(*, unsafe_retry=False):
    state = BookingState(unsafe_retry=unsafe_retry)
    with local_server(state) as url:
        baseline = book(url, "baseline", "Maya")
        state.start_fault([WORKER], observer_age_seconds=0, recovery_ready=True)
        first_failure_at = None
        try:
            book(url, "fault-1", "Alex", timeout=0.05)
        except (TimeoutError, URLError):
            first_failure_at = time.monotonic()
        finally:
            state.stop_fault()
        if first_failure_at is None:
            raise AssertionError("The selected timeout fault was not observed")
        retried = book(url, "fault-1", "Alex")
        probes = [book(url, f"after-{number}", "Sam") for number in (1, 2)]
        record = audit(url)
        observed_seconds = round(time.monotonic() - first_failure_at, 4)
        fault_rows = [row for row in record["rows"] if row["request_id"] == "fault-1"]
        correct_probes = all(row["request_id"] == f"after-{number}" for number, row in zip((1, 2), probes))
        return {"baseline_booking": baseline["booking_id"], "first_customer_outcome": "timeout",
                "retry_booking": retried["booking_id"], "fault_request_records": len(fault_rows),
                "new_probes_correct": correct_probes, "fault_stopped": not record["fault_active"],
                "observed_failure_to_second_probe_seconds": observed_seconds,
                "hypothesis_met": len(fault_rows) == 1 and correct_probes and not record["fault_active"],
                "scope": "one-process loopback HTTP and in-memory store; not AWS or timed customer recovery"}


if __name__ == "__main__":
    print(json.dumps(run_experiment(), indent=2))
