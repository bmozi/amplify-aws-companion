// Exercise the actual Amplify SQL-schema string adapter; no database or AWS calls.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {createRequire} = require('node:module');
const app = fs.realpathSync(path.resolve(process.argv[2] || 'app'));
const appRequire = createRequire(path.join(app, 'package.json'));
const adapterPath = appRequire.resolve('@aws-amplify/graphql-schema-generator/lib/datasource-adapter/mysql-string-datasource-adapter.js');
const adapterRequire = createRequire(adapterPath);
const parserEntry = adapterRequire.resolve('csv-parse/sync');
let parserRoot = path.dirname(parserEntry);
while (!fs.existsSync(path.join(parserRoot, 'package.json'))) {
  const parent = path.dirname(parserRoot);
  assert.notEqual(parent, parserRoot, 'Cannot locate parser package');
  parserRoot = parent;
}
const version = JSON.parse(fs.readFileSync(path.join(parserRoot, 'package.json'))).version;
const location = path.relative(app, parserRoot).split(path.sep).join('/');
const lock = JSON.parse(fs.readFileSync(path.join(app, 'package-lock.json')));
assert.equal(version, lock.packages[location]?.version, 'Caller-resolved CSV parser differs from lockfile');
const {MySQLStringDataSourceAdapter: Adapter} = adapterRequire(adapterPath);
const {EmptySchemaError, InvalidSchemaError} = adapterRequire('./string-datasource-adapter.js');
const header = 'TABLE_NAME,COLUMN_NAME,COLUMN_DEFAULT,ORDINAL_POSITION,DATA_TYPE,COLUMN_TYPE,IS_NULLABLE,CHARACTER_MAXIMUM_LENGTH,INDEX_NAME,NON_UNIQUE,SEQ_IN_INDEX,NULLABLE';
const rows = [
  'notes,id,NULL,1,int,int,NO,NULL,PRIMARY,0,1,NO',
  'notes,title,"hello, ""reader""",2,varchar,varchar(80),YES,80,NULL,NULL,NULL,YES',
  'notes,body,"line one\nline two",3,text,text,YES,NULL,NULL,NULL,NULL,YES',
  'shops,id,null,1,int,int,NO,NULL,PRIMARY,0,1,NO',
];
for (const newline of ['\n', '\r\n']) {
  const adapter = new Adapter([header, ...rows].join(newline));
  assert.deepEqual(adapter.getTablesList(), ['notes', 'shops']);
  const notes = adapter.getFields('notes');
  assert.deepEqual(notes.map(f => f.name), ['id', 'title', 'body']);
  assert.equal(notes[0].default, undefined);
  assert.deepEqual(notes[1].default, {kind:'DB_GENERATED', value:'hello, "reader"'});
  assert.deepEqual(notes[2].default, {kind:'DB_GENERATED', value:'line one\nline two'});
  assert.equal(notes[1].length, '80');
  assert.deepEqual(adapter.getPrimaryKey('notes').getFields(), ['id']);
  assert.equal(adapter.getFields('shops')[0].default, undefined);
  assert.deepEqual(adapter.getIndexes('notes'), []);
  assert.equal(adapter.getModels().length, 2);
}
assert.throws(() => new Adapter(header), EmptySchemaError);
assert.throws(() => new Adapter('TABLE_NAME,COLUMN_NAME\nnotes,id'), InvalidSchemaError);
assert.throws(() => new Adapter(header+'\nnotes,id'), /Invalid Record Length/);
console.log(JSON.stringify({csvVersion:version,location,lockVersionMatched:true,
  lineEndings:2,quotedCommaAndQuote:true,embeddedNewline:true,nullMarkers:true,
  primaryKeyAndModels:true,invalidInputsRejected:3,
  scope:'Local MySQL schema-string adapter compatibility; no database connection, complete CLI, security exploit or AWS behavior'},null,2));
