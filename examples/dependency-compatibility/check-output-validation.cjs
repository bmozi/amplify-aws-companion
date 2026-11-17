// Exercise the installed generator with fictional output; never fetch AWS output.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {createRequire, syncBuiltinESMExports} = require('node:module');
const {pathToFileURL} = require('node:url');
const net = require('node:net');
const tls = require('node:tls');
net.Socket.prototype.connect = () => { throw new Error('Network forbidden in this probe'); };
tls.connect = () => { throw new Error('Network forbidden in this probe'); };
globalThis.fetch = () => { throw new Error('Network forbidden in this probe'); };
syncBuiltinESMExports();
const app = fs.realpathSync(path.resolve(process.argv[2] || 'app'));
const appRequire = createRequire(path.join(app, 'package.json'));
const generatorPath = path.join(path.dirname(appRequire.resolve('@aws-amplify/client-config')), 'unified_client_config_generator.js');
const callerRequire = createRequire(generatorPath);
const schemaPath = callerRequire.resolve('@aws-amplify/backend-output-schemas');
const schemaRequire = createRequire(schemaPath);
const lock = JSON.parse(fs.readFileSync(path.join(app, 'package-lock.json')));
function identity(entry) {
  let dir = path.dirname(entry);
  while (!fs.existsSync(path.join(dir, 'package.json')) || !JSON.parse(fs.readFileSync(path.join(dir, 'package.json'))).version) {
    assert.notEqual(dir, path.dirname(dir));
    dir = path.dirname(dir);
  }
  const version = JSON.parse(fs.readFileSync(path.join(dir, 'package.json'))).version;
  const location = path.relative(app, dir).split(path.sep).join('/');
  assert.ok(version, 'Package version must be present');
  assert.ok(lock.packages[location], 'Resolved package must have a lock record');
  assert.equal(lock.packages[location].version, version, 'Installed caller differs from lock');
  return {location, version};
}
(async () => {
  const identities = [generatorPath, schemaPath, schemaRequire.resolve('zod')].map(identity);
  const {UnifiedClientConfigGenerator} = await import(pathToFileURL(generatorPath));
  const {functionOutputKey} = callerRequire('@aws-amplify/backend-output-schemas');
  let calls = 0;
  let observed;
  const contributor = {contribute: async output => {
    calls++;
    observed = output;
    return {version:'1.4', custom:{fixture:'local-only'}};
  }};
  const run = output => new UnifiedClientConfigGenerator(async () => output, [contributor]).generateClientConfig();
  const valid = {[functionOutputKey]:{version:'1',payload:{definedFunctions:'["fixture-worker"]'}}};
  assert.deepEqual(await run(valid), {version:'1.4',custom:{fixture:'local-only'}});
  assert.deepEqual(observed, valid);
  await run({...valid, unknownCategory:{unexpected:true}});
  assert.deepEqual(observed, valid, 'Unknown top-level category should be stripped');
  for (const bad of [
    {[functionOutputKey]:{version:'999',payload:{definedFunctions:'[]'}}},
    {[functionOutputKey]:{version:'1',payload:{definedFunctions:42}}},
    {[functionOutputKey]:{version:'1',payload:{}}},
  ]) {
    const before = calls;
    await assert.rejects(run(bad), error => error.name === 'ZodError');
    assert.equal(calls, before, 'Invalid shape reached the contributor');
  }
  const malformed = {[functionOutputKey]:{version:'1',payload:{definedFunctions:'not JSON'}}};
  await run(malformed);
  assert.deepEqual(observed, malformed, 'String validation does not parse serialized JSON');
  assert.throws(() => JSON.parse(observed[functionOutputKey].payload.definedFunctions), SyntaxError);
  assert.equal(calls, 3);
  console.log(JSON.stringify({identities,cases:6,invalidShapesRejectedBeforeContributor:3,
    unknownCategoryStripped:true,malformedSerializedJSONPassedShapeCheck:true,
    scope:'Installed generator and schema; injected local fetch and synthetic contributor. Not real output retrieval, actual category conversion, full CLI, repair or exploit proof.'},null,2));
})().catch(error => {console.error(error);process.exitCode=1;});
