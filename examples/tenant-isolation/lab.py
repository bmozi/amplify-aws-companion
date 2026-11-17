"""Local tenant-scoped records, cache and queued job context. Synthetic identities only."""
import json
from pathlib import Path
import sqlite3
import tempfile

# Fixture lookup stands in for a trusted authentication/membership service, not JWT verification.
IDENTITIES={'fixture-alice':'shop-a','fixture-bob':'shop-b'}

class Service:
    def __init__(self,path):
        self.path=path;self.cache={}
        with sqlite3.connect(path) as db:
            db.executescript('''CREATE TABLE notes(tenant TEXT,id TEXT,body TEXT,PRIMARY KEY(tenant,id));
            CREATE TABLE jobs(id INTEGER PRIMARY KEY,tenant TEXT,record_id TEXT);
            INSERT INTO notes VALUES('shop-a','shared-id','A private note');
            INSERT INTO notes VALUES('shop-b','shared-id','B private note');
            INSERT INTO notes VALUES('shop-b','b-only','Another B note');''')
    def tenant(self,credential,requested_tenant=None):
        tenant=IDENTITIES.get(credential)
        if tenant is None or (requested_tenant is not None and requested_tenant!=tenant):
            raise PermissionError('Tenant access denied')
        return tenant
    def read(self,credential,record_id,requested_tenant=None):
        return self._read(self.tenant(credential,requested_tenant),record_id)
    def _read(self,tenant,record_id):
        key=(tenant,record_id)
        if key not in self.cache:
            with sqlite3.connect(self.path) as db:
                row=db.execute('SELECT body FROM notes WHERE tenant=? AND id=?',key).fetchone()
            if not row:raise PermissionError('Record unavailable')
            self.cache[key]=row[0]
        return self.cache[key]
    def listing(self,credential):
        tenant=self.tenant(credential)
        with sqlite3.connect(self.path) as db:
            return db.execute('SELECT id,body FROM notes WHERE tenant=? ORDER BY id',(tenant,)).fetchall()
    def enqueue(self,credential,record_id,requested_tenant=None):
        tenant=self.tenant(credential,requested_tenant)
        self._read(tenant,record_id)
        with sqlite3.connect(self.path) as db:
            return db.execute('INSERT INTO jobs(tenant,record_id) VALUES (?,?)',(tenant,record_id)).lastrowid
    def process(self,job_id):
        # Internal worker boundary: job arguments are loaded from server-created rows.
        with sqlite3.connect(self.path) as db:
            row=db.execute('SELECT tenant,record_id FROM jobs WHERE id=?',(job_id,)).fetchone()
        if not row:raise ValueError('Unknown internal job')
        return self._read(*row)


def denied(action):
    try:action()
    except PermissionError:return
    raise AssertionError('Expected access denial')


def run(path):
    s=Service(path)
    assert s.read('fixture-alice','shared-id')=='A private note'
    assert s.read('fixture-bob','shared-id')=='B private note'
    assert len(s.cache)==2  # Colliding record IDs cannot share a cache entry.
    assert s.read('fixture-alice','shared-id')=='A private note'
    denied(lambda:s.read('fixture-alice','shared-id','shop-b'))
    denied(lambda:s.read('fixture-alice','b-only'))
    denied(lambda:s.read('untrusted','shared-id'))
    assert s.listing('fixture-alice')==[('shared-id','A private note')]
    assert len(s.listing('fixture-bob'))==2
    a=s.enqueue('fixture-alice','shared-id');b=s.enqueue('fixture-bob','shared-id')
    denied(lambda:s.enqueue('fixture-alice','shared-id','shop-b'))
    assert s.process(b)=='B private note' and s.process(a)=='A private note'
    s.cache.clear()  # Database lookups must remain isolated after cache eviction.
    assert s.process(a)=='A private note' and s.process(b)=='B private note'
    return {'same_record_id_isolated':True,'warm_and_cold_cache_checked':True,
            'forged_tenant_denied':True,'cross_tenant_record_denied':True,
            'unknown_identity_denied':True,'lists_scoped':True,'job_context_preserved':True,
            'scope':'Actual local queries/cache and stored job context; synthetic identities; internal worker not an exposed API; no JWT, IAM, membership revocation or cloud queue verification'}

if __name__=='__main__':
    with tempfile.TemporaryDirectory(prefix='amplify-tenants-') as tmp:
        folder=Path(tmp);result=run(folder/'tenant.sqlite')
    result['temporary_resources_removed']=not folder.exists()
    assert result['temporary_resources_removed']
    print(json.dumps(result,indent=2))
