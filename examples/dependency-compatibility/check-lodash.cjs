// Local compatibility probe for both legacy GraphQL helper callers of Lodash.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {createRequire} = require('node:module');
const app = fs.realpathSync(path.resolve(process.argv[2] || 'app'));
const appRequire = createRequire(path.join(app, 'package.json'));
const {buildSchema} = appRequire('graphql');
const lock = JSON.parse(fs.readFileSync(path.join(app, 'package-lock.json'), 'utf8'));
const visitorRequire = createRequire(appRequire.resolve('@graphql-codegen/visitor-plugin-common'));
const callers = [appRequire.resolve('@graphql-codegen/plugin-helpers'),
  visitorRequire.resolve('@graphql-codegen/plugin-helpers')];
const results = [];
for (const caller of callers) {
  const callerRequire = createRequire(caller);
  const lodashPath = callerRequire.resolve('lodash/package.json');
  const location = path.relative(app, path.dirname(lodashPath)).split(path.sep).join('/');
  const version = callerRequire(lodashPath).version;
  assert.equal(version, lock.packages[location]?.version, 'Caller-resolved Lodash differs from lockfile');
  const {ApolloFederation} = appRequire(caller);
  const schema = buildSchema(`
    scalar _FieldSet
    directive @key(fields: _FieldSet!) repeatable on OBJECT
    directive @external on FIELD_DEFINITION
    directive @requires(fields: _FieldSet!) repeatable on FIELD_DEFINITION
    directive @provides(fields: _FieldSet!) on FIELD_DEFINITION
    type Details { weight: Int!, size: Int! }
    type Product @key(fields: "id") {
      id: ID! @external
      details: Details @external
      cost: Int @requires(fields: "details { weight }") @requires(fields: "details { size }")
      label: String
    }
    type Query { product: Product }
  `);
  const parentType = schema.getType('Product');
  const parameters = field => ({fieldNode: parentType.getFields()[field].astNode,
    parentType, parentTypeSignature: 'Parent'});
  const active = new ApolloFederation({enabled: true, schema});
  const expected = `{ __typename: 'Product' } & GraphQLRecursivePick<Parent, {"id":true}> & GraphQLRecursivePick<Parent, {"details":{"weight":true,"size":true}}>`;
  assert.equal(active.transformParentType(parameters('cost')), expected,
    'Nested required fields must both survive caller merge');
  assert.equal(active.transformParentType(parameters('label')),
    `{ __typename: 'Product' } & GraphQLRecursivePick<Parent, {"id":true}>`);
  assert.equal(new ApolloFederation({enabled: false, schema}).transformParentType(parameters('cost')), 'Parent');
  results.push({caller: path.relative(app, caller), lodashVersion: version, cases: 3});
}
console.log(JSON.stringify({results, scope: 'Local federation helper compatibility; not full generation, exploitability or AWS evidence'}, null, 2));
