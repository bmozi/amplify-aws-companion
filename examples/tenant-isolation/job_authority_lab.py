"""Cloud-free A10 queued-job authority exercise with synthetic identities.

The effect is one SQLite row, not an email, payment, AWS queue, or IAM decision.
"""

import json
from pathlib import Path
import sqlite3
import tempfile


ACTION_AUTHORITY = {
    'personal_report': 'delegated',
    'repair_followup': 'accepted_workflow',
}


class JobAuthority:
    def __init__(self, path: Path):
        self.path = path
        with sqlite3.connect(path) as db:
            db.executescript("""
                CREATE TABLE tenants(tenant TEXT PRIMARY KEY, active INTEGER NOT NULL);
                CREATE TABLE memberships(
                    actor TEXT, tenant TEXT, active INTEGER NOT NULL,
                    revision INTEGER NOT NULL, PRIMARY KEY(actor, tenant)
                );
                CREATE TABLE notes(
                    tenant TEXT, id TEXT, body TEXT, PRIMARY KEY(tenant, id)
                );
                CREATE TABLE jobs(
                    id INTEGER PRIMARY KEY, tenant TEXT NOT NULL, actor TEXT NOT NULL,
                    note_id TEXT NOT NULL, action TEXT NOT NULL, authority TEXT NOT NULL,
                    membership_revision INTEGER NOT NULL, status TEXT NOT NULL
                );
                CREATE TABLE effects(job_id INTEGER PRIMARY KEY, tenant TEXT NOT NULL);
                INSERT INTO tenants VALUES ('shop-a', 1), ('shop-b', 1);
                INSERT INTO memberships VALUES ('alice', 'shop-a', 1, 1),
                    ('bob', 'shop-b', 1, 1);
                INSERT INTO notes VALUES ('shop-a', 'same-id', 'A private note'),
                    ('shop-b', 'same-id', 'B private note');
            """)

    def submit(self, actor: str, tenant: str, note_id: str, action: str) -> int:
        authority = ACTION_AUTHORITY.get(action)
        if authority is None:
            raise ValueError('Choose a declared action')
        with sqlite3.connect(self.path) as db:
            db.execute('BEGIN IMMEDIATE')
            membership = db.execute(
                'SELECT active,revision FROM memberships WHERE actor=? AND tenant=?',
                (actor, tenant),
            ).fetchone()
            tenant_row = db.execute(
                'SELECT active FROM tenants WHERE tenant=?', (tenant,)
            ).fetchone()
            note = db.execute(
                'SELECT 1 FROM notes WHERE tenant=? AND id=?', (tenant, note_id)
            ).fetchone()
            if not membership or not membership[0] or not tenant_row or not tenant_row[0] or not note:
                raise PermissionError('Submission not authorized or note unavailable')
            return db.execute(
                'INSERT INTO jobs(tenant,actor,note_id,action,authority,membership_revision,status) '
                'VALUES (?,?,?,?,?,?,?)',
                (tenant, actor, note_id, action, authority, membership[1], 'pending'),
            ).lastrowid

    def revoke(self, actor: str, tenant: str) -> None:
        with sqlite3.connect(self.path) as db:
            updated = db.execute(
                'UPDATE memberships SET active=0,revision=revision+1 '
                'WHERE actor=? AND tenant=? AND active=1', (actor, tenant)
            ).rowcount
            if updated != 1:
                raise ValueError('No active fixture membership to revoke')

    def reinstate(self, actor: str, tenant: str) -> None:
        with sqlite3.connect(self.path) as db:
            updated = db.execute(
                'UPDATE memberships SET active=1,revision=revision+1 '
                'WHERE actor=? AND tenant=? AND active=0', (actor, tenant)
            ).rowcount
            if updated != 1:
                raise ValueError('No revoked fixture membership to reinstate')

    def close_tenant(self, tenant: str) -> None:
        with sqlite3.connect(self.path) as db:
            updated = db.execute(
                'UPDATE tenants SET active=0 WHERE tenant=? AND active=1', (tenant,)
            ).rowcount
            if updated != 1:
                raise ValueError('No active fixture tenant to close')

    def preview(self, job_id: int) -> bool:
        """An intentionally non-authoritative early check for the race exercise."""
        with sqlite3.connect(self.path) as db:
            row = db.execute(
                'SELECT j.authority,j.membership_revision,m.active,m.revision,t.active '
                'FROM jobs j JOIN memberships m ON (j.actor=m.actor AND j.tenant=m.tenant) '
                'JOIN tenants t ON j.tenant=t.tenant WHERE j.id=?', (job_id,)
            ).fetchone()
        return bool(row and row[4] and (
            row[0] == 'accepted_workflow' or (row[2] and row[1] == row[3])
        ))

    def execute(self, job_id: int) -> str:
        """Recheck authority and write the local effect in one SQLite transaction."""
        with sqlite3.connect(self.path) as db:
            db.execute('BEGIN IMMEDIATE')
            row = db.execute(
                'SELECT tenant,actor,note_id,action,authority,membership_revision,status '
                'FROM jobs WHERE id=?', (job_id,)
            ).fetchone()
            if not row:
                raise ValueError('Unknown internal job')
            tenant, actor, note_id, action, authority, accepted_revision, status = row
            if status == 'done':
                return 'already_done'
            active = db.execute(
                'SELECT active FROM tenants WHERE tenant=?', (tenant,)
            ).fetchone()
            if not active or not active[0]:
                raise PermissionError('Tenant closed before local effect')
            if ACTION_AUTHORITY.get(action) != authority:
                raise PermissionError('Stored job authority does not match server policy')
            if authority == 'delegated':
                membership = db.execute(
                    'SELECT active,revision FROM memberships WHERE actor=? AND tenant=?',
                    (actor, tenant),
                ).fetchone()
                if not membership or not membership[0] or membership[1] != accepted_revision:
                    raise PermissionError('Delegated authority changed before local effect')
            elif authority != 'accepted_workflow':
                raise ValueError('Unknown stored authority')
            note = db.execute(
                'SELECT 1 FROM notes WHERE tenant=? AND id=?', (tenant, note_id)
            ).fetchone()
            if not note:
                raise PermissionError('Tenant-scoped note unavailable')
            db.execute('INSERT INTO effects(job_id,tenant) VALUES (?,?)', (job_id, tenant))
            db.execute('UPDATE jobs SET status=? WHERE id=?', ('done', job_id))
            return 'done'

    def effects(self) -> list[tuple[int, str]]:
        with sqlite3.connect(self.path) as db:
            return db.execute('SELECT job_id,tenant FROM effects ORDER BY job_id').fetchall()


def run(path: Path) -> dict:
    lab = JobAuthority(path)
    delegated = lab.submit('alice', 'shop-a', 'same-id', 'personal_report')
    workflow = lab.submit('alice', 'shop-a', 'same-id', 'repair_followup')
    other = lab.submit('bob', 'shop-b', 'same-id', 'personal_report')
    assert lab.preview(delegated)
    lab.revoke('alice', 'shop-a')
    assert not lab.preview(delegated)
    try:
        lab.execute(delegated)
    except PermissionError:
        pass
    else:
        raise AssertionError('Revoked delegated job ran')
    assert lab.execute(workflow) == 'done'
    assert lab.execute(workflow) == 'already_done'
    assert lab.execute(other) == 'done'
    assert lab.effects() == [(workflow, 'shop-a'), (other, 'shop-b')]
    return {
        'delegated_after_revocation': 'denied',
        'accepted_workflow_after_revocation': 'one local effect',
        'other_tenant': 'one local effect',
        'scope': 'Synthetic identities and one SQLite transaction; no external effect or AWS authority tested',
    }


if __name__ == '__main__':
    with tempfile.TemporaryDirectory(prefix='amplify-job-authority-') as tmp:
        folder = Path(tmp)
        result = run(folder / 'jobs.sqlite')
    result['temporary_resources_removed'] = not folder.exists()
    print(json.dumps(result, indent=2))
