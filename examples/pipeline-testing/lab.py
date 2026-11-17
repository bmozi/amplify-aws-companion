#!/usr/bin/env python3
"""Local teaching lab for matching test scope to pipeline stage."""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
import tempfile
import threading
import unittest
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen


class ReminderRules:
    @staticmethod
    def may_queue(consent: bool) -> bool:
        return consent is True


class Outbox:
    def __init__(self, path: str | Path):
        # The local HTTP server thread and the test driver both inspect this
        # one connection. The lab sends requests sequentially.
        self.connection = sqlite3.connect(path, check_same_thread=False)
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS outbox "
            "(id INTEGER PRIMARY KEY, customer TEXT NOT NULL, "
            "appointment TEXT NOT NULL, message TEXT NOT NULL)"
        )

    def add(self, customer: str, appointment: str, message: str) -> None:
        with self.connection:
            self.connection.execute(
                "INSERT INTO outbox(customer, appointment, message) VALUES (?, ?, ?)",
                (customer, appointment, message),
            )

    def all(self) -> list[dict[str, str]]:
        rows = self.connection.execute(
            "SELECT customer, appointment, message FROM outbox ORDER BY id"
        ).fetchall()
        return [
            {"customer": row[0], "appointment": row[1], "message": row[2]}
            for row in rows
        ]

    def close(self) -> None:
        self.connection.close()


class ReminderService:
    def __init__(self, outbox: Outbox, fault: str = "none"):
        self.outbox = outbox
        self.fault = fault

    def submit(self, customer: str, consent: bool, appointment: str) -> tuple[int, dict]:
        # The consent-bypass fault is deliberately in the application path,
        # outside the pure policy function tested by the unit stage.
        allowed = self.fault == "consent-bypass" or ReminderRules.may_queue(consent)
        if not allowed:
            return 403, {"status": "not_queued"}
        message = f"Reminder: your appointment is {appointment}."
        if self.fault == "wrong-message":
            message = "Reminder: your appointment is tomorrow."
        self.outbox.add(customer, appointment, message)
        return 202, {"status": "queued"}


@contextmanager
def local_service(fault: str):
    with tempfile.TemporaryDirectory(prefix="pipeline-testing-") as directory:
        outbox = Outbox(Path(directory) / "reminders.sqlite")
        service = ReminderService(outbox, fault)
        handler = make_handler(service)
        server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            yield service, f"http://127.0.0.1:{server.server_port}"
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)
            outbox.close()


def make_handler(service: ReminderService):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, _format: str, *_args: object) -> None:
            pass

        def send_json(self, status: int, value: dict) -> None:
            payload = json.dumps(value).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def do_POST(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
            if self.path != "/reminders":
                self.send_json(404, {"error": "not_found"})
                return
            try:
                data = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                if not isinstance(data.get("consent"), bool):
                    raise ValueError("consent must be a JSON boolean")
                status, result = service.submit(
                    str(data["customer"]), data["consent"], str(data["appointment"])
                )
            except (KeyError, ValueError, json.JSONDecodeError):
                self.send_json(400, {"error": "invalid_request"})
                return
            self.send_json(status, result)

        def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
            if self.path != "/outbox":
                self.send_json(404, {"error": "not_found"})
                return
            self.send_json(200, {"items": service.outbox.all()})

    return Handler


class UnitTests(unittest.TestCase):
    def test_consent_is_required(self):
        self.assertFalse(ReminderRules.may_queue(False))

    def test_explicit_consent_allows_a_reminder(self):
        self.assertTrue(ReminderRules.may_queue(True))


class IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="pipeline-integration-")
        self.outbox = Outbox(Path(self.directory.name) / "outbox.sqlite")
        self.service = ReminderService(self.outbox, self.fault)

    def tearDown(self):
        self.outbox.close()
        self.directory.cleanup()

    fault = "none"

    def test_no_consent_creates_no_persisted_message(self):
        status, _ = self.service.submit("customer-17", False, "Tuesday at 10")
        self.assertEqual(status, 403)
        self.assertEqual(self.outbox.all(), [])

    def test_consent_persists_one_customer_scoped_message(self):
        status, _ = self.service.submit("customer-17", True, "Tuesday at 10")
        self.assertEqual(status, 202)
        self.assertEqual(len(self.outbox.all()), 1)
        self.assertEqual(self.outbox.all()[0]["customer"], "customer-17")


class AcceptanceTests(unittest.TestCase):
    fault = "none"

    def request(self, base: str, body: dict) -> tuple[int, dict]:
        request = Request(
            base + "/reminders",
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            response = urlopen(request, timeout=3)
        except HTTPError as error:
            response = error
        with response:
            return response.status, json.loads(response.read())

    def get_outbox(self, base: str) -> list[dict]:
        with urlopen(base + "/outbox", timeout=3) as response:
            return json.loads(response.read())["items"]

    def test_customer_consent_and_exact_appointment_are_honored(self):
        with local_service(self.fault) as (_service, base):
            status, result = self.request(
                base,
                {"customer": "customer-17", "consent": True, "appointment": "Tuesday at 10"},
            )
            self.assertEqual((status, result["status"]), (202, "queued"))
            self.assertEqual(
                self.get_outbox(base),
                [{
                    "customer": "customer-17",
                    "appointment": "Tuesday at 10",
                    "message": "Reminder: your appointment is Tuesday at 10.",
                }],
            )

    def test_customer_without_consent_has_no_outbox_entry(self):
        with local_service(self.fault) as (_service, base):
            status, result = self.request(
                base,
                {"customer": "customer-22", "consent": False, "appointment": "Friday at 2"},
            )
            self.assertEqual((status, result["status"]), (403, "not_queued"))
            self.assertEqual(self.get_outbox(base), [])


STAGES = [
    ("unit", UnitTests),
    ("integration", IntegrationTests),
    ("acceptance", AcceptanceTests),
]


def run_stage(name: str, test_case: type[unittest.TestCase], fault: str) -> bool:
    test_case.fault = fault
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(test_case)
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    if not result.wasSuccessful():
        print(f"GATE FAILED: {name}; stop this candidate before later stages.")
        return False
    print(f"GATE PASSED: {name}")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fault",
        choices=("none", "consent-bypass", "wrong-message"),
        default="none",
        help="inject one fictional defect to see which test stage detects it",
    )
    args = parser.parse_args()
    for name, test_case in STAGES:
        if not run_stage(name, test_case, args.fault):
            return 1
    print("All local gates passed. This is not evidence about AWS or production.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
