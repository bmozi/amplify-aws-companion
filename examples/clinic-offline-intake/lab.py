"""Cloud-free clinic intake fixture; minutes and identities are invented inputs."""

from __future__ import annotations

import hashlib
import json
import sqlite3
import tempfile
from pathlib import Path


def _digest(kind: str, photo_token: str, critical: bool) -> str:
    return hashlib.sha256(f"{kind}\0{photo_token}\0{int(critical)}".encode()).hexdigest()


class ClinicDevice:
    def __init__(self, path: Path, clinic_id: str):
        self.path = path
        self.clinic_id = clinic_id
        with sqlite3.connect(path) as db:
            db.execute(
                """CREATE TABLE IF NOT EXISTS pending (
                    request_id TEXT PRIMARY KEY, clinic_id TEXT NOT NULL,
                    payload_hash TEXT NOT NULL, local_minute INTEGER NOT NULL,
                    critical INTEGER NOT NULL, escalation_minute INTEGER
                )"""
            )

    def submit(self, request_id: str, kind: str, photo_token: str,
               local_minute: int, critical: bool) -> dict:
        if not request_id or local_minute < 0:
            raise ValueError("request ID and nonnegative fixture minute required")
        payload_hash = _digest(kind, photo_token, critical)
        with sqlite3.connect(self.path) as db:
            old = db.execute(
                "SELECT payload_hash FROM pending WHERE request_id=?", (request_id,)
            ).fetchone()
            if old and old[0] != payload_hash:
                raise ValueError("same request ID with changed content")
            if not old:
                db.execute(
                    "INSERT INTO pending VALUES (?, ?, ?, ?, ?, NULL)",
                    (request_id, self.clinic_id, payload_hash, local_minute, int(critical)),
                )
        return self.get(request_id)

    def get(self, request_id: str) -> dict:
        with sqlite3.connect(self.path) as db:
            row = db.execute(
                "SELECT request_id,clinic_id,payload_hash,local_minute,critical,"
                "escalation_minute FROM pending WHERE request_id=?", (request_id,)
            ).fetchone()
        if row is None:
            raise KeyError(request_id)
        return dict(zip(("request_id", "clinic_id", "payload_hash", "local_minute",
                         "critical", "escalation_minute"), row))

    def log_local_escalation(self, request_id: str, minute: int) -> dict:
        row = self.get(request_id)
        if not row["critical"] or minute < row["local_minute"]:
            raise ValueError("only a critical request can receive a later escalation log")
        with sqlite3.connect(self.path) as db:
            db.execute(
                "UPDATE pending SET escalation_minute=? WHERE request_id=?",
                (minute, request_id),
            )
        return self.get(request_id)


class IntakeServer:
    def __init__(self, path: Path, device_clinics: dict[str, str]):
        self.path = path
        self.device_clinics = device_clinics
        with sqlite3.connect(path) as db:
            db.execute(
                """CREATE TABLE IF NOT EXISTS accepted (
                    clinic_id TEXT NOT NULL, request_id TEXT NOT NULL,
                    payload_hash TEXT NOT NULL, server_minute INTEGER NOT NULL,
                    device_id TEXT NOT NULL,
                    PRIMARY KEY (clinic_id, request_id)
                )"""
            )

    def sync(self, device_id: str, queued: dict, server_minute: int) -> dict:
        if self.device_clinics.get(device_id) != queued["clinic_id"]:
            raise PermissionError("device is not assigned to this clinic")
        if server_minute < 0:
            raise ValueError("nonnegative fixture minute required")
        key = (queued["clinic_id"], queued["request_id"])
        with sqlite3.connect(self.path) as db:
            old = db.execute(
                "SELECT payload_hash,server_minute FROM accepted WHERE clinic_id=? "
                "AND request_id=?", key,
            ).fetchone()
            if old and old[0] != queued["payload_hash"]:
                raise ValueError("server rejects changed content under an accepted ID")
            if old:
                accepted_minute = old[1]
            else:
                db.execute(
                    "INSERT INTO accepted VALUES (?, ?, ?, ?, ?)",
                    (*key, queued["payload_hash"], server_minute, device_id),
                )
                accepted_minute = server_minute
        return {"clinic_id": key[0], "request_id": key[1],
                "server_received_minute": accepted_minute}

    def read(self, device_id: str, clinic_id: str, request_id: str) -> dict:
        if self.device_clinics.get(device_id) != clinic_id:
            raise PermissionError("device is not assigned to this clinic")
        with sqlite3.connect(self.path) as db:
            row = db.execute(
                "SELECT clinic_id,request_id,server_minute FROM accepted "
                "WHERE clinic_id=? AND request_id=?", (clinic_id, request_id)
            ).fetchone()
        if row is None:
            raise PermissionError("no accepted request in this clinic scope")
        return dict(zip(("clinic_id", "request_id", "server_received_minute"), row))


def local_escalation_status(queued: dict, observation_minute: int) -> str:
    if not queued["critical"]:
        return "not_required_by_fixture"
    logged = queued["escalation_minute"]
    if logged is not None:
        return "logged_within_30" if logged <= queued["local_minute"] + 30 else "logged_late"
    return "pending" if observation_minute < queued["local_minute"] + 30 else "missing"


def demonstrate() -> dict:
    with tempfile.TemporaryDirectory(prefix="clinic-offline-") as temp:
        root = Path(temp)
        device = ClinicDevice(root / "clinic-a.sqlite", "clinic-a")
        device.submit("repair-1", "safety-critical-repair", "fictional-photo-A", 0, True)
        device.submit("repair-2", "routine-repair", "fictional-photo-B", 2, False)
        device.submit("repair-3", "safety-critical-repair", "fictional-photo-C", 4, True)
        device = ClinicDevice(root / "clinic-a.sqlite", "clinic-a")  # offline restart
        device.log_local_escalation("repair-1", 20)
        before = [device.get(x) for x in ("repair-1", "repair-2", "repair-3")]
        server = IntakeServer(root / "server.sqlite", {"device-a": "clinic-a"})
        accepted = [server.sync("device-a", row, 120) for row in before]
        replay = server.sync("device-a", before[0], 121)
        try:
            server.read("device-a", "clinic-b", "repair-1")
        except PermissionError:
            neighbor_read = "denied_in_fixture"
        else:
            raise AssertionError("neighbor request crossed the fixture scope")
        return {
            "offline_rows_survived_restart": len(before),
            "critical_local_log": local_escalation_status(before[0], 120),
            "unlogged_critical": local_escalation_status(before[2], 120),
            "server_receipts": accepted,
            "same_id_replay_receipt": replay,
            "neighbor_read": neighbor_read,
            "boundary": "Fixture minutes and log entries do not prove trusted time, a human call, real identity, durable devices or AWS behavior.",
        }


if __name__ == "__main__":
    print(json.dumps(demonstrate(), indent=2))
