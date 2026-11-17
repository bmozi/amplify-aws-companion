"""Measure a local customer-path recovery sequence, not an AWS RTO."""

from http.server import ThreadingHTTPServer
import json
import tempfile
import threading
from time import monotonic_ns

from customer_path_lab import Recovery, handler_for, request


def run_case(*, leave_old_writer_open: bool = False) -> dict:
    with tempfile.TemporaryDirectory(prefix="amplify-failover-clock-") as folder:
        recovery = Recovery(folder)
        recovery.source_online = True
        with ThreadingHTTPServer(("127.0.0.1", 0), handler_for(recovery)) as server:
            worker = threading.Thread(target=server.serve_forever, daemon=True)
            worker.start()
            base = f"http://127.0.0.1:{server.server_port}"
            start = monotonic_ns()
            events = []

            def record(name: str, evidence: dict) -> None:
                events.append({"event": name, "elapsed_ms": round((monotonic_ns() - start) / 1_000_000, 3),
                               "evidence": evidence})

            try:
                baseline = request(base, "/bookings/111")
                if baseline != (200, {"id": "111", "amount_cents": 2300}):
                    raise RuntimeError("Fixture baseline is not a correct customer read")
                record("baseline_customer_read", {"status": baseline[0], "booking": baseline[1]})

                recovery.source_online = False  # local cooperative fault, not DNS or FIS
                record("source_fault_introduced", {"route": recovery.route})
                failed = request(base, "/bookings/111")
                if failed[0] != 503:
                    raise RuntimeError("The customer did not observe the planned failure")
                record("first_failed_customer_read", {"status": failed[0]})

                health = request(base, "/candidate/health")
                difference = recovery.reconcile()
                if health != (200, {"healthy": True}) or difference["missing"] != ["111"]:
                    raise RuntimeError("Fixture did not expose healthy-but-incomplete candidate")
                record("candidate_health_is_insufficient", {"status": health[0],
                         "missing_confirmed_ids": difference["missing"]})

                recovery.key_available = True  # fictional checked prerequisite, not KMS proof
                if not leave_old_writer_open:
                    recovery.source_writable = False  # cooperative flag, not a distributed fence
                record("operator_gate_review", {"key_check_stipulated": True,
                         "old_writer_cooperative_flag_closed": not recovery.source_writable})
                replay = recovery.replay_missing()
                record("candidate_reconciled", {"difference": replay})
                try:
                    recovery.switch()
                except ValueError as error:
                    record("switch_held", {"reason": str(error)})
                    return summarize(events, "HOLD", None)

                record("route_switched", {"route": recovery.route})
                observed = request(base, "/bookings/111")
                if observed != baseline:
                    raise RuntimeError("Switched route did not serve the confirmed value")
                record("first_correct_customer_read", {"status": observed[0], "booking": observed[1]})
                accepted = request(base, "/bookings", {"id": "112", "amount_cents": 900})
                current = request(base, "/bookings/112")
                if accepted[0] != 201 or current != (200, {"id": "112", "amount_cents": 900}):
                    raise RuntimeError("New confirmed booking is not readable on the selected route")
                record("new_work_confirmed_on_candidate", {"write_status": accepted[0],
                       "read_status": current[0]})
                recovery.source_online = True
                pinned = request(base, "/pinned-source/bookings/112")
                record("pinned_old_path_checked", {"status": pinned[0],
                         "limit": "one old-path probe cannot characterize all clients"})
                return summarize(events, "LOCAL_RECOVERY_OBSERVED", pinned[0])
            finally:
                server.shutdown()
                worker.join(timeout=3)


def summarize(events: list[dict], status: str, pinned_status: int | None) -> dict:
    when = {item["event"]: item["elapsed_ms"] for item in events}
    duration = None
    if "first_correct_customer_read" in when:
        duration = round(when["first_correct_customer_read"] - when["first_failed_customer_read"], 3)
    return {"scope": "one same-host loopback run; real elapsed time, not AWS RTO/RPO or customer SLO",
            "status": status, "failure_to_correct_read_ms": duration,
            "pinned_old_path_status": pinned_status, "events": events}


if __name__ == "__main__":
    output = {"reviewed": run_case(), "old_writer_open": run_case(leave_old_writer_open=True)}
    print(json.dumps(output, indent=2))
