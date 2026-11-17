// Inspect the actual importer -> Knex -> mysql2 configuration, without connecting.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const net = require('node:net');
const {createRequire} = require('node:module');
const app = fs.realpathSync(path.resolve(process.argv[2] || 'app'));
const appRequire = createRequire(path.join(app, 'package.json'));
const adapterPath = appRequire.resolve('@aws-amplify/graphql-schema-generator/lib/datasource-adapter/mysql-datasource-adapter.js');
const adapterRequire = createRequire(adapterPath);
const knexRequire = createRequire(adapterRequire.resolve('knex'));
const driverPackage = knexRequire.resolve('mysql2/package.json');
const driverRoot = path.dirname(driverPackage);
const version = JSON.parse(fs.readFileSync(driverPackage)).version;
const lock = JSON.parse(fs.readFileSync(path.join(app, 'package-lock.json')));
const location = path.relative(app, driverRoot).split(path.sep).join('/');
assert.equal(version, lock.packages[location]?.version, 'Resolved driver differs from lock');
const Config = require(path.join(driverRoot, 'lib/connection_config.js'));
const {MySQLDataSourceAdapter: Adapter} = adapterRequire(adapterPath);
const originalConnect = net.Socket.prototype.connect;
let attempts = 0;
net.Socket.prototype.connect = function () {
  attempts++;
  throw new Error('This configuration probe must not open a socket');
};

(async () => {
  try {
    for (const customCA of [undefined, 'synthetic-CA-not-a-real-certificate']) {
      const adapter = new Adapter({host: 'database.invalid', port: 3306,
        database: 'teaching', username: 'fixture', password: 'fixture-only',
        sslCertificate: customCA});
      try {
        adapter.establishDBConnection();
        const client = adapter.dbBuilder.client;
        assert.equal(client.driver, knexRequire('mysql2'), 'Unexpected Knex driver');
        const config = new Config(client.connectionSettings);
        assert.equal(config.host, 'database.invalid');
        assert.equal(config.database, 'teaching');
        assert.equal(config.ssl.rejectUnauthorized, true);
        assert.equal(config.ssl.ca, customCA);
        assert.equal(config.compress, false);
        console.log(JSON.stringify({driver: version, location,
          customCA: Boolean(customCA), tlsRequested: Boolean(config.ssl),
          rejectUnauthorized: config.ssl.rejectUnauthorized,
          compression: config.compress}));
      } finally {
        if (adapter.dbBuilder) await adapter.dbBuilder.destroy();
      }
    }
    assert.equal(attempts, 0, 'Network operation was attempted');
    console.log('Configuration only: no handshake, server, schema query or exploit test.');
  } finally {
    net.Socket.prototype.connect = originalConnect;
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
