"""Two-store A10 teaching fixture. No email, network, queue, or AWS call occurs."""

import json
from pathlib import Path
import secrets
import sqlite3
import tempfile


class LostReply(RuntimeError):
    pass


class TwoStoreEffect:
    def __init__(self, work_path: Path, provider_path: Path):
        self.work_path = work_path
        self.provider_path = provider_path
        with sqlite3.connect(work_path) as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS tenants(id TEXT PRIMARY KEY, active INTEGER NOT NULL);
                CREATE TABLE IF NOT EXISTS memberships(actor TEXT, tenant TEXT, active INTEGER NOT NULL,
                    PRIMARY KEY(actor,tenant));
                CREATE TABLE IF NOT EXISTS outbox(id INTEGER PRIMARY KEY, tenant TEXT NOT NULL,
                    actor TEXT NOT NULL, effect_key TEXT NOT NULL UNIQUE,
                    status TEXT NOT NULL, receipt TEXT);
                INSERT OR IGNORE INTO tenants VALUES ('shop-a',1),('shop-b',1);
                INSERT OR IGNORE INTO memberships VALUES ('alice','shop-a',1),('bob','shop-b',1);
            """)
        with sqlite3.connect(provider_path) as db:
            db.execute('CREATE TABLE IF NOT EXISTS deliveries(effect_key TEXT PRIMARY KEY, tenant TEXT NOT NULL, receipt TEXT NOT NULL)')

    def accept(self, actor: str, tenant: str) -> int:
        """Choose a stable key inside the local acceptance transaction."""
        with sqlite3.connect(self.work_path) as db:
            db.execute('BEGIN IMMEDIATE')
            member = db.execute('SELECT active FROM memberships WHERE actor=? AND tenant=?',
                                (actor, tenant)).fetchone()
            active = db.execute('SELECT active FROM tenants WHERE id=?', (tenant,)).fetchone()
            if not member or not member[0] or not active or not active[0]:
                raise PermissionError('Acceptance requires active fixture membership and tenant')
            # The server chooses and durably stores a key unique within this provider fixture.
            return db.execute(
                "INSERT INTO outbox(tenant,actor,effect_key,status) VALUES (?,?,?,?)",
                (tenant, actor, f'a10-{secrets.token_hex(16)}', 'pending'),
            ).lastrowid

    def revoke(self, actor: str, tenant: str) -> None:
        with sqlite3.connect(self.work_path) as db:
            if db.execute('UPDATE memberships SET active=0 WHERE actor=? AND tenant=? AND active=1',
                          (actor, tenant)).rowcount != 1:
                raise ValueError('No active fixture membership')

    def close(self, tenant: str) -> None:
        with sqlite3.connect(self.work_path) as db:
            if db.execute('UPDATE tenants SET active=0 WHERE id=? AND active=1',
                          (tenant,)).rowcount != 1:
                raise ValueError('No active fixture tenant')

    def _row(self, work_id: int):
        with sqlite3.connect(self.work_path) as db:
            row = db.execute('SELECT tenant,effect_key,status,receipt FROM outbox WHERE id=?',
                             (work_id,)).fetchone()
        if row is None:
            raise ValueError('Unknown internal work ID')
        return row

    def provider_receipt(self, effect_key: str):
        with sqlite3.connect(self.provider_path) as db:
            return db.execute('SELECT tenant,receipt FROM deliveries WHERE effect_key=?',
                              (effect_key,)).fetchone()

    def dispatch(self, work_id: int, *, lose_reply: bool = False,
                 after_active_check=None) -> str:
        """Model an external commit. The two SQLite connections never share a transaction."""
        tenant, key, status, _ = self._row(work_id)
        if status == 'confirmed':
            return 'already_confirmed'
        if status == 'stopped':
            return 'stopped'
        with sqlite3.connect(self.work_path) as db:
            active = db.execute('SELECT active FROM tenants WHERE id=?', (tenant,)).fetchone()
            if not active or not active[0]:
                # A real provider race remains possible after this local check.
                db.execute("UPDATE outbox SET status='stopped' WHERE id=? AND status='pending'", (work_id,))
                return 'stopped'
        if after_active_check is not None:
            # Teaching seam: force the otherwise hard-to-reproduce closure window.
            after_active_check()
        # Fictional provider honors the stable key; a repeat does not create a second delivery.
        with sqlite3.connect(self.provider_path) as provider:
            provider.execute('BEGIN IMMEDIATE')
            existing = provider.execute('SELECT tenant,receipt FROM deliveries WHERE effect_key=?',
                                        (key,)).fetchone()
            if existing and existing[0] != tenant:
                raise PermissionError('Provider key belongs to another tenant')
            if not existing:
                receipt = f'fictional-receipt-{key}'
                provider.execute('INSERT INTO deliveries VALUES (?,?,?)', (key, tenant, receipt))
            else:
                receipt = existing[1]
        if lose_reply:
            raise LostReply('Provider committed, but local worker did not receive its reply')
        with sqlite3.connect(self.work_path) as db:
            db.execute("UPDATE outbox SET status='confirmed',receipt=? WHERE id=?",
                       (receipt, work_id))
        return 'confirmed'

    def reconcile(self, work_id: int) -> str:
        tenant, key, status, _ = self._row(work_id)
        if status == 'confirmed':
            return 'already_confirmed'
        provider_row = self.provider_receipt(key)
        if provider_row is None:
            return 'no_provider_receipt'
        if provider_row[0] != tenant:
            raise PermissionError('Receipt tenant mismatch')
        with sqlite3.connect(self.work_path) as db:
            db.execute("UPDATE outbox SET status='confirmed',receipt=? WHERE id=?",
                       (provider_row[1], work_id))
        return 'confirmed_from_receipt'

    def state(self, work_id: int):
        return self._row(work_id)

    def deliveries(self):
        with sqlite3.connect(self.provider_path) as db:
            return db.execute('SELECT effect_key,tenant,receipt FROM deliveries ORDER BY effect_key').fetchall()

    def closure_report(self, tenant: str) -> dict:
        """Report local evidence, never a claim that all external copies are gone."""
        with sqlite3.connect(self.work_path) as db:
            active = db.execute('SELECT active FROM tenants WHERE id=?', (tenant,)).fetchone()
            if active is None:
                raise ValueError('Unknown fixture tenant')
            counts = dict(db.execute('SELECT status,COUNT(*) FROM outbox WHERE tenant=? GROUP BY status',
                                     (tenant,)).fetchall())
        pending = counts.get('pending', 0)
        confirmed = counts.get('confirmed', 0)
        return {
            'access': 'open' if active[0] else 'closed',
            'pending_effects': pending,
            'confirmed_effects': confirmed,
            'effect_review': ('unresolved' if pending else
                              'completed_effects_need_retention_review' if confirmed else
                              'no_unresolved_local_work'),
            'external_copy_deletion_proven': False,
        }


def run(folder: Path) -> dict:
    lab = TwoStoreEffect(folder / 'work.sqlite', folder / 'provider.sqlite')
    work_id = lab.accept('alice', 'shop-a')
    lab.revoke('alice', 'shop-a')  # This accepted business workflow continues by the chosen policy.
    try:
        lab.dispatch(work_id, lose_reply=True)
    except LostReply:
        pass
    else:
        raise AssertionError('Lost reply not simulated')
    assert lab.state(work_id)[2] == 'pending'
    assert lab.reconcile(work_id) == 'confirmed_from_receipt'
    assert lab.dispatch(work_id) == 'already_confirmed'
    assert len(lab.deliveries()) == 1
    return {'local_after_lost_reply': 'pending', 'provider_after_lost_reply': 'one fictional delivery',
            'reconciliation': 'confirmed from matching receipt',
            'scope': 'Two local SQLite files; provider idempotency and receipt lookup are fixture assumptions'}


if __name__ == '__main__':
    with tempfile.TemporaryDirectory(prefix='a10-two-store-') as tmp:
        folder = Path(tmp)
        result = run(folder)
    result['temporary_resources_removed'] = not folder.exists()
    print(json.dumps(result, indent=2))
