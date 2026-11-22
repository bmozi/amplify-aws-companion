const test = require('node:test');
const assert = require('node:assert/strict');
const model = require('./models.js');

test('lost replies leave indistinguishable customer uncertainty across different writes', () => {
  const before = model.request({ allowed: true, failure: 'before' });
  const after = model.request({ allowed: true, failure: 'after' });
  assert.equal(before.known, false); assert.equal(after.known, false);
  assert.equal(before.saved, false); assert.equal(after.saved, true);
  assert.equal(model.request({ allowed: false, failure: 'after' }).saved, false);
});
test('all retry combinations preserve the atomic acceptance invariant', () => {
  for (const firstSaved of [false, true]) for (const retry of [false, true])
    for (const sameKey of [false, true]) for (const deduplicate of [false, true]) {
      const actual = model.retry({ firstSaved, retry, sameKey, deduplicate }).records;
      const expected = !retry ? Number(firstSaved) : !firstSaved || (sameKey && deduplicate) ? 1 : 2;
      assert.equal(actual, expected, JSON.stringify({ firstSaved, retry, sameKey, deduplicate }));
    }
});
test('backup frequency and recovery duration satisfy independent targets, including equality', () => {
  assert.deepEqual([model.recovery({interval:60,restore:45,lossTarget:15,timeTarget:60}).lossFits,
    model.recovery({interval:60,restore:45,lossTarget:15,timeTarget:60}).timeFits], [false,true]);
  const equal = model.recovery({interval:15,restore:60,lossTarget:15,timeTarget:60});
  assert.equal(equal.lossFits, true); assert.equal(equal.timeFits, true);
  assert.equal(model.recovery({interval:5,restore:61,lossTarget:15,timeTarget:60}).timeFits, false);
});
