// Local compatibility probe; does not load Amplify credentials or call AWS.
const assert = require('node:assert/strict');
const path = require('node:path');
const fs = require('node:fs');
const {createRequire} = require('node:module');
const app = fs.realpathSync(path.resolve(process.argv[2] || 'app'));
const requireApp = createRequire(path.join(app, 'package.json'));
const {buildSchema, parse, print, graphqlSync} = requireApp('graphql');
const optimizerPath = requireApp.resolve('@graphql-tools/relay-operation-optimizer');
const {optimizeDocuments} = requireApp(optimizerPath);
const requireOptimizer = createRequire(optimizerPath);
const compilerPath = requireOptimizer.resolve('@ardatan/relay-compiler/lib/core/CompilerContext.js');
const requireCompiler = createRequire(compilerPath);
const immutableVersion = requireCompiler('immutable/package.json').version;
const immutableLocation = path.relative(app,path.dirname(requireCompiler.resolve('immutable/package.json'))).split(path.sep).join('/');
const lock = JSON.parse(fs.readFileSync(path.join(app,'package-lock.json'),'utf8'));
assert.equal(immutableVersion,lock.packages[immutableLocation]?.version,
  'Installed compiler dependency differs from the selected lockfile');
const schema = buildSchema(`
  type Note { id: ID!, title: String!, tags: [String!]! }
  type Query { note(id: ID!): Note, notes: [Note!]! }
`);
const note = {id: 'n1', title: 'First note', tags: ['learning']};
const rootValue = {note: ({id}) => id === 'n1' ? note : null, notes: () => [note]};
const cases = [
  ['fragment and duplicate fields', `query Read { note(id:"n1") { id ...Fields title } } fragment Fields on Note { title tags }`, {}, {note}],
  ['alias and variables', `query Read($id:ID!){ chosen:note(id:$id){ id title } }`, {id:'n1'}, {chosen:{id:'n1',title:'First note'}}],
  ['conditional included', `query Read($show:Boolean!){ notes { id title @include(if:$show) } }`, {show:true}, {notes:[{id:'n1',title:'First note'}]}],
  ['conditional excluded', `query Read($show:Boolean!){ notes { id title @include(if:$show) } }`, {show:false}, {notes:[{id:'n1'}]}],
  ['missing item remains null', `query Read { note(id:"missing") { id title } }`, {}, {note:null}],
];
const plain = value => JSON.parse(JSON.stringify(value));
for (const [name, source, variableValues, expected] of cases) {
  for (const includeFragments of [false, true]) {
    // The optimizer can return reusable fragments separately from inlined operations.
    // Execute operation documents; concatenating unused fragments fails GraphQL validation.
    const documents = optimizeDocuments(schema,[parse(source)],{includeFragments});
    const operations = documents.filter(doc => doc.definitions.some(def => def.kind === 'OperationDefinition'));
    assert.equal(operations.length,1);
    const optimized = operations.map(print).join('\n');
    for (const candidate of [source,optimized]) {
      const result = graphqlSync({schema,source:candidate,rootValue,variableValues});
      assert.equal(result.errors,undefined,`${name}: unexpected error`);
      assert.deepEqual(plain(result.data),expected,`${name}: changed result`);
    }
  }
}
assert.throws(() => optimizeDocuments(schema,[parse('query Bad { nonexistent }')]));
console.log(JSON.stringify({immutableVersion,immutableLocation,lockVersionMatched:true,compilerVersion:requireCompiler('../../package.json').version,
  cases:cases.length,fragmentModes:2,invalidFieldRejected:true,
  scope:'Local GraphQL optimizer result compatibility; no full Amplify CLI, deployment, authorization or exploitability proof'},null,2));

require('./check-lodash.cjs');

require('./check-csv.cjs');
