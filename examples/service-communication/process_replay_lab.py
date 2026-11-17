"""Cloud-free replay claim across separate local backend processes.

SQLite is one shared same-machine file. This is not a distributed store,
production credential scheme, network boundary, or business outcome ledger.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from multiprocessing import get_context
from pathlib import Path
import json
import secrets
import sqlite3
from tempfile import TemporaryDirectory

from proxy_bypass_lab import proof, server
from replay_boundary_lab import backend_handler, entry_handler, get


class SqliteNonceLedger:
    """One SQLite file with a unique nonce claim across local processes."""

    def __init__(self, path: Path):
        self.path = path
        with self._connect() as connection:
            connection.execute(
                "CREATE TABLE IF NOT EXISTS used_nonce (nonce TEXT PRIMARY KEY)"
            )

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path, timeout=10)

    def claim(self, nonce: str) -> bool:
        with self._connect() as connection:
            cursor = connection.execute(
                "INSERT OR IGNORE INTO used_nonce(nonce) VALUES (?)", (nonce,)
            )
            return cursor.rowcount == 1


def _serve_backend(pipe, database: str, proxy_secret: bytes,
                   customer_secret: bytes, fail_after_claim: bool) -> None:
    try:
        ledger = SqliteNonceLedger(Path(database))
        with server(backend_handler(ledger, proxy_secret, customer_secret,
                                    fail_after_claim=fail_after_claim)) as url:
            pipe.send(("ready", url))
            pipe.recv()
    except Exception as error:
        pipe.send(("error", f"{type(error).__name__}: {error}"))
    finally:
        pipe.close()


@contextmanager
def backend_process(database: Path, proxy_secret: bytes,
                    customer_secret: bytes, fail_after_claim: bool = False):
    """Start one backend in a distinct Python process and always stop it."""
    parent, child = get_context("spawn").Pipe()
    process = get_context("spawn").Process(
        target=_serve_backend,
        args=(child, str(database), proxy_secret, customer_secret,
              fail_after_claim),
    )
    process.start()
    child.close()
    try:
        if not parent.poll(10):
            raise RuntimeError("backend did not start")
        state, value = parent.recv()
        if state != "ready":
            raise RuntimeError(value)
        yield value
    finally:
        if process.is_alive():
            try:
                parent.send("stop")
            except (BrokenPipeError, EOFError):
                pass
        process.join(timeout=10)
        if process.is_alive():
            process.terminate()
            process.join(timeout=5)
        parent.close()
        if process.exitcode != 0:
            raise RuntimeError(f"backend exited with {process.exitcode}")


def _fixture_headers(customer_secret: bytes) -> dict[str, str]:
    return {
        "X-Customer-ID": "c-one",
        "X-Customer-Proof": proof(customer_secret, "c-one|INV-01"),
    }


def run_restart_case() -> dict[str, int]:
    with TemporaryDirectory(prefix="amplify-replay-") as temp:
        database = Path(temp) / "claims.sqlite3"
        SqliteNonceLedger(database)
        proxy_secret = secrets.token_bytes(32)
        customer_secret = secrets.token_bytes(32)
        workload_key = secrets.token_hex(24)
        capture: list[dict[str, str]] = []
        customer = {"X-Workload-Key": workload_key,
                    **_fixture_headers(customer_secret)}
        with backend_process(database, proxy_secret, customer_secret) as a:
            with backend_process(database, proxy_secret, customer_secret) as b:
                with server(entry_handler(a, workload_key, proxy_secret, capture)) as entry:
                    first = get(entry, customer)
                    assert len(capture) == 1
                    copied = capture[0].copy()
                    same = get(a, copied)
                    second = get(b, copied)
            # B is a new process with a new in-memory state, but it reopens
            # the same durable local claim file.
            with backend_process(database, proxy_secret, customer_secret) as b2:
                after_restart = get(b2, copied)
                fresh = get(b2, {
                    **_fixture_headers(customer_secret),
                    "X-Proxy-Nonce": "fresh-" + secrets.token_hex(16),
                })
                new_nonce = secrets.token_hex(16)
                new_signed = get(b2, {
                    **_fixture_headers(customer_secret),
                    "X-Proxy-Nonce": new_nonce,
                    "X-Proxy-Receipt": proof(
                        proxy_secret,
                        f"GET|/invoices/INV-01|c-one|{new_nonce}",
                    ),
                })
        return {
            "first_via_entry": first,
            "copy_to_a": same,
            "copy_to_b": second,
            "copy_to_restarted_b": after_restart,
            "fresh_without_receipt": fresh,
            "new_signed_after_restart": new_signed,
        }


def run_claim_without_result_case() -> dict[str, int]:
    with TemporaryDirectory(prefix="amplify-replay-failure-") as temp:
        database = Path(temp) / "claims.sqlite3"
        SqliteNonceLedger(database)
        proxy_secret = secrets.token_bytes(32)
        customer_secret = secrets.token_bytes(32)
        workload_key = secrets.token_hex(24)
        capture: list[dict[str, str]] = []
        customer = {"X-Workload-Key": workload_key,
                    **_fixture_headers(customer_secret)}
        with backend_process(database, proxy_secret, customer_secret,
                             fail_after_claim=True) as a:
            with server(entry_handler(a, workload_key, proxy_secret, capture)) as entry:
                first = get(entry, customer)
                assert len(capture) == 1
                copied = capture[0].copy()
        with backend_process(database, proxy_secret, customer_secret) as b:
            retry = get(b, copied)
        return {"after_claim_error": first, "retry_after_restart": retry}


def run_race_case() -> dict[str, int]:
    with TemporaryDirectory(prefix="amplify-replay-race-") as temp:
        database = Path(temp) / "claims.sqlite3"
        SqliteNonceLedger(database)
        proxy_secret = secrets.token_bytes(32)
        customer_secret = secrets.token_bytes(32)
        nonce = secrets.token_hex(16)
        headers = {
            **_fixture_headers(customer_secret),
            "X-Proxy-Nonce": nonce,
            "X-Proxy-Receipt": proof(
                proxy_secret, f"GET|/invoices/INV-01|c-one|{nonce}"
            ),
        }
        with backend_process(database, proxy_secret, customer_secret) as a:
            with backend_process(database, proxy_secret, customer_secret) as b:
                urls = [a, b] * 16
                with ThreadPoolExecutor(max_workers=16) as pool:
                    statuses = list(pool.map(lambda url: get(url, headers), urls))
        return {"accepted": statuses.count(200),
                "rejected": statuses.count(403),
                "other": len(statuses) - statuses.count(200) - statuses.count(403)}


def run_separate_copy_case() -> dict[str, int]:
    """Two isolated claim-file copies cannot make one global claim decision."""
    with TemporaryDirectory(prefix="amplify-replay-isolated-") as temp:
        # Both files begin empty. They model independent hosts after a split,
        # without pretending to implement replication or a network partition.
        a_file = Path(temp) / "a.sqlite3"
        b_file = Path(temp) / "b.sqlite3"
        SqliteNonceLedger(a_file)
        SqliteNonceLedger(b_file)
        proxy_secret = secrets.token_bytes(32)
        customer_secret = secrets.token_bytes(32)
        nonce = secrets.token_hex(16)
        headers = {
            **_fixture_headers(customer_secret),
            "X-Proxy-Nonce": nonce,
            "X-Proxy-Receipt": proof(
                proxy_secret, f"GET|/invoices/INV-01|c-one|{nonce}"
            ),
        }
        with backend_process(a_file, proxy_secret, customer_secret) as a:
            with backend_process(b_file, proxy_secret, customer_secret) as b:
                first_a = get(a, headers)
                first_b = get(b, headers)
                repeat_a = get(a, headers)
                repeat_b = get(b, headers)
        with sqlite3.connect(a_file) as connection:
            a_claims = {row[0] for row in connection.execute(
                "SELECT nonce FROM used_nonce"
            )}
        with sqlite3.connect(b_file) as connection:
            b_claims = {row[0] for row in connection.execute(
                "SELECT nonce FROM used_nonce"
            )}
        return {
            "first_a": first_a,
            "first_b": first_b,
            "repeat_a": repeat_a,
            "repeat_b": repeat_b,
            "accepted_responses": sum(s == 200 for s in (first_a, first_b)),
            "distinct_claims_after_union": len(a_claims | b_claims),
        }


def main() -> None:
    result = {"restart": run_restart_case(),
              "claim_without_result": run_claim_without_result_case(),
              "two_process_race": run_race_case(),
              "isolated_copies": run_separate_copy_case()}
    assert result == {
        "restart": {
            "first_via_entry": 200,
            "copy_to_a": 403,
            "copy_to_b": 403,
            "copy_to_restarted_b": 403,
            "fresh_without_receipt": 403,
            "new_signed_after_restart": 200,
        },
        "claim_without_result": {
            "after_claim_error": 503,
            "retry_after_restart": 403,
        },
        "two_process_race": {"accepted": 1, "rejected": 31, "other": 0},
        "isolated_copies": {
            "first_a": 200, "first_b": 200,
            "repeat_a": 403, "repeat_b": 403,
            "accepted_responses": 2, "distinct_claims_after_union": 1,
        },
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
