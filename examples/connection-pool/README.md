# Return a connection without returning unfinished work

A shared desk is not ready for the next person just because its previous occupant left. Their unfinished papers may remain. A database connection can likewise retain an open transaction after an application operation fails.

From the repository root, run:

```sh
python3 examples/connection-pool/lab.py
```

Requires Python with SQLite. No packages, network, AWS login or Docker are needed. The drill creates a temporary database, uses real connections, closes them and verifies removal of the folder. Run without `-O` so assertions execute.

## Predict before running

| Case | Expected observation |
| --- | --- |
| Return a connection without resetting its unfinished transaction | Next borrower sees the uncommitted row; independent connection sees no committed row |
| Raise an exception after inserting, with cleanup enabled | Rollback removes the failed row for the next borrower and independent observer |
| Keep the only connection borrowed while another borrow waits | Waiting borrow times out; holder still has its active transaction |
| Holder explicitly commits and releases | Next borrower can reuse the connection; independent observer sees the committed row |
| Exit normally but forget to commit | This helper rolls the unfinished transaction back |

The contract is explicit: **the borrower commits intended work; the pool rolls back anything still unfinished before reuse.** Other APIs can choose differently. Do not assume leaving a context always commits. This drill uses explicit SQL transaction statements, including when Python exposes its newer autocommit option. See [Python SQLite transaction control](https://docs.python.org/3/library/sqlite3.html#transaction-control).

The queue has one slot and a short bounded wait. Nested borrowers run in one thread so the holder cannot release while the waiting call executes. This is a controlled schedule showing exhaustion, not a concurrent throughput benchmark. The wait is a fixture choice, not a recommended timeout. There is no query cancellation: the timed-out operation was waiting to borrow, not running SQL.

The independent observer matters. Visibility through a reused connection does not establish that another connection sees committed work. The negative control demonstrates that difference. The corrected path checks both views and preserves only the explicitly committed row.

## Challenge the cleanup

In a temporary copy, replace the cleanup `connection.execute('ROLLBACK')` with `pass`. Predict which assertion should fail after the injected application error. Run the copy and inspect the failure; restore the original source. Do not remove the assertion to make defective code pass.

For transfer, suppose rollback fails because the connection is broken. Explain why it must not return to the available pool. This helper closes it and propagates the error; it does not replace it, so the pool can lose capacity. A production pool also needs lifecycle, replacement, shutdown and observability behavior, plus resetting relevant session state beyond transactions. Choose and test an established driver/pool for the actual database.

Ask Codex to identify what each assertion proves and what it cannot prove about PostgreSQL, a managed proxy, cancellation or concurrent access. These SQLite observations do not verify RDS Proxy pinning, cloud failover, IAM, TLS or another engine's behavior.
