// A local simulation: no AWS requests, no credentials, no real payments.
import assert from 'node:assert/strict';
const completed = new Map();
let effects = 0;
function processOnce(job) {
  if (completed.has(job.id)) return completed.get(job.id);
  if (job.fail) throw new Error('Simulated dependency failure');
  const receipt = { id: job.id, status: 'done' };
  effects++;
  completed.set(job.id, receipt);
  return receipt;
}
const first = processOnce({ id: 'note-1' });
assert.deepEqual(processOnce({ id: 'note-1' }), first);
assert.equal(effects, 1);
let attempts = 0;
const deadLetters = [];
for (; attempts < 3; attempts++) {
  try { processOnce({ id: 'note-2', fail: true }); break; }
  catch { if (attempts === 2) deadLetters.push('note-2'); }
}
assert.equal(attempts, 3);
assert.deepEqual(deadLetters, ['note-2']);
assert.equal(effects, 1);
console.log('PASS: duplicate delivery produced one effect; failing job stopped after 3 attempts.');
console.log('This Map is not durable or concurrency-safe. AWS needs an atomic durable design.');
