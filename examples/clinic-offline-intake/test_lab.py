import tempfile
import unittest
from pathlib import Path

from lab import ClinicDevice, IntakeServer, local_escalation_status


class ClinicOfflineIntakeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.device_path = root / "device.sqlite"
        self.server_path = root / "server.sqlite"

    def test_offline_restart_and_two_receipt_clocks(self):
        device = ClinicDevice(self.device_path, "clinic-a")
        device.submit("r-1", "critical", "fictional-photo", 0, True)
        reopened = ClinicDevice(self.device_path, "clinic-a")
        queued = reopened.get("r-1")
        self.assertEqual(local_escalation_status(queued, 30), "missing")
        server = IntakeServer(self.server_path, {"device-a": "clinic-a"})
        self.assertEqual(server.sync("device-a", queued, 120)["server_received_minute"], 120)
        self.assertEqual(server.sync("device-a", queued, 121)["server_received_minute"], 120)

    def test_local_log_is_separate_from_server_acceptance(self):
        device = ClinicDevice(self.device_path, "clinic-a")
        device.submit("r-1", "critical", "fictional-photo", 0, True)
        self.assertEqual(local_escalation_status(device.log_local_escalation("r-1", 20), 120), "logged_within_30")
        device.submit("r-2", "critical", "other-photo", 0, True)
        self.assertEqual(local_escalation_status(device.log_local_escalation("r-2", 35), 120), "logged_late")

    def test_replay_cannot_change_payload_and_neighbor_cannot_read(self):
        device = ClinicDevice(self.device_path, "clinic-a")
        queued = device.submit("r-1", "routine", "photo-one", 0, False)
        with self.assertRaises(ValueError):
            device.submit("r-1", "routine", "photo-two", 1, False)
        with self.assertRaises(ValueError):
            device.submit("r-1", "routine", "photo-one", 1, True)
        server = IntakeServer(self.server_path, {"device-a": "clinic-a", "device-b": "clinic-b"})
        with self.assertRaises(PermissionError):
            server.sync("device-b", queued, 120)
        server.sync("device-a", queued, 120)
        with self.assertRaises(PermissionError):
            server.read("device-b", "clinic-a", "r-1")
        self.assertEqual(server.read("device-a", "clinic-a", "r-1")["server_received_minute"], 120)
        changed = {**queued, "payload_hash": "changed"}
        with self.assertRaises(ValueError):
            server.sync("device-a", changed, 121)


if __name__ == "__main__":
    unittest.main()
