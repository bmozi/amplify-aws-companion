// Called by run-mysql-server.py with its disposable loopback server and CA.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {createRequire} = require('node:module');
const [appPath, portText, caPath] = process.argv.slice(2);
const app = fs.realpathSync(appPath);
const appRequire = createRequire(path.join(app, 'package.json'));
const adapterPath = appRequire.resolve('@aws-amplify/graphql-schema-generator/lib/datasource-adapter/mysql-datasource-adapter.js');
const localRequire = createRequire(adapterPath);
const {MySQLDataSourceAdapter: Adapter} = localRequire(adapterPath);
const knexRequire = createRequire(localRequire.resolve('knex'));
const version = knexRequire('mysql2/package.json').version;
const base = {host: '127.0.0.1', port: Number(portText), database: 'teaching',
  username: 'reader', password: 'fixture-reader-only'};
assert(Number.isInteger(base.port) && base.port > 0 && base.port < 65536);
async function dispose(adapter) {
  if (adapter.dbBuilder) await adapter.dbBuilder.destroy();
}
(async () => {
  // No custom trust: the server's generated self-signed CA must be rejected.
  const untrusted = new Adapter(base);
  try {
    untrusted.establishDBConnection();
    await assert.rejects(untrusted.dbBuilder.raw('SELECT 1'), error =>
      /self.signed|certificate/i.test(error.message));
  } finally { await dispose(untrusted); }
  const trusted = new Adapter({...base, sslCertificate: fs.readFileSync(caPath, 'utf8')});
  try {
    await trusted.initialize();
    assert.deepEqual(trusted.getTablesList().sort(), ['notes', 'shops']);
    const fields = trusted.getFields('notes');
    assert.deepEqual(fields.map(f => f.name), ['id', 'shop_id', 'title', 'amount']);
    assert.equal(Number(fields[2].length), 80);
    assert.deepEqual(fields[0].type, {kind: 'NonNull', type: {kind: 'Scalar', name: 'Int'}});
    assert.deepEqual(fields[2].type, {kind: 'Scalar', name: 'String'});
    assert.deepEqual(trusted.getPrimaryKey('notes').getFields(), ['id']);
    const indexes = trusted.getIndexes('notes').map(i => ({name: i.name, fields: i.getFields()}));
    assert.deepEqual(indexes, [{name: 'by_shop_title', fields: ['shop_id', 'title']}]);
    assert.equal(trusted.getModels().length, 2);
    const [tls] = await trusted.dbBuilder.raw("SHOW SESSION STATUS LIKE 'Ssl_cipher'");
    assert(tls[0].Value.length > 0, 'Session must actually negotiate TLS');
    await assert.rejects(trusted.dbBuilder.raw("INSERT INTO notes VALUES (99, 1, 'forbidden', 1.00)"),
      error => error.code === 'ER_TABLEACCESS_DENIED_ERROR');
    console.log(JSON.stringify({version, tables: 2, fieldOrder: true, primaryKey: true,
      compositeIndex: true, models: 2, tlsCipher: tls[0].Value,
      untrustedCertificateRejected: true, insertDenied: true,
      scope: 'Local MySQL importer; no AWS, full CLI, hostname-negative or exploit test'}));
  } finally { await dispose(trusted); }
})().catch(error => {console.error(error); process.exitCode = 1;});
