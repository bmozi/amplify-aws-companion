import test from 'node:test';
import assert from 'node:assert/strict';
import { runJourney } from './live-journey.mjs';

function fixture({ leakList = false, leakOnSecondPage = false, leakFileList = false, failRemove = false, allowOverwrite = false } = {}) {
  const users = [{ username: 'owner' }, { username: 'other' }];
  let active;
  let entry;
  let file;
  const calls = [];
  const denied = { data: null, errors: [{ message: 'Not authorized' }] };
  const dependencies = {
    users,
    endpoint: 'https://example.invalid/graphql',
    signIn: async user => { active = user; },
    signOut: async () => { active = undefined; },
    fetchAuthSession: async () => ({ identityId: 'identity-owner' }),
    fetch: async () => ({ status: 401 }),
    client: {
      models: { Entry: {
        create: async values => { entry = { id: 'entry-1', ...values }; return { data: entry }; },
        update: async values => {
          if (active !== users[0]) return denied;
          entry = { ...entry, ...values };
          return { data: entry };
        },
        get: async () => ({ data: active === users[0] ? entry : null }),
        list: async ({ nextToken } = {}) => {
          if (leakOnSecondPage) return nextToken
            ? { data: [entry], nextToken: null }
            : { data: [], nextToken: 'page-two' };
          return { data: active === users[0] || leakList ? [entry] : [], nextToken: null };
        },
        delete: async () => { calls.push('delete-entry'); entry = null; return { data: { id: 'entry-1' } }; }
      } },
      queries: { inspectEntry: async () => ({ data: JSON.stringify({ words: 3, service: 'AWS Lambda' }) }) }
    },
    uploadData: ({ path, data }) => ({ result: active === users[0] || allowOverwrite
      ? Promise.resolve().then(() => { file = { path, data }; })
      : Promise.reject(new Error('Access denied')) }),
    downloadData: ({ path }) => ({ result: active === users[0] && file?.path === path
      ? Promise.resolve({ body: { text: async () => file.data } })
      : Promise.reject(new Error('Access denied')) }),
    list: async () => ({ items: (active === users[0] || leakFileList) && file ? [{ path: file.path }] : [] }),
    remove: async () => {
      if (active !== users[0]) throw new Error('Access denied');
      calls.push('remove-file');
      if (failRemove) throw new Error('Remove failed');
      file = null;
    }
  };
  return { dependencies, calls, state: () => ({ entry, file, active }) };
}

test('two-user journey passes and removes only its created resources', async () => {
  const f = fixture();
  const receipt = await runJourney(f.dependencies);
  assert.equal(receipt.passed, true);
  assert(receipt.results.some(item => item.name === 'Second user cannot list first user entry'));
  assert(receipt.results.some(item => item.name === 'Second user cannot list first user file'));
  assert.deepEqual(f.calls, ['remove-file', 'delete-entry']);
  assert.deepEqual(f.state(), { entry: null, file: null, active: undefined });
});

test('discovery leak fails the journey and still cleans up', async () => {
  const f = fixture({ leakList: true });
  const receipt = await runJourney(f.dependencies);
  assert.equal(receipt.passed, false);
  assert.deepEqual(f.calls, ['remove-file', 'delete-entry']);
  assert.equal(f.state().entry, null);
  assert.equal(f.state().file, null);
});

test('a leak on a later Data page also fails and cleans up', async () => {
  const f = fixture({ leakOnSecondPage: true });
  const receipt = await runJourney(f.dependencies);
  assert.equal(receipt.passed, false);
  assert.deepEqual(f.calls, ['remove-file', 'delete-entry']);
});

test('unauthorized file overwrite fails and owner cleanup still runs', async () => {
  const f = fixture({ allowOverwrite: true });
  const receipt = await runJourney(f.dependencies);
  assert.equal(receipt.passed, false);
  assert.deepEqual(f.calls, ['remove-file', 'delete-entry']);
});

test('a visible private file fails the second-user list check', async () => {
  const f = fixture({ leakFileList: true });
  const receipt = await runJourney(f.dependencies);
  assert.equal(receipt.passed, false);
  assert.deepEqual(f.calls, ['remove-file', 'delete-entry']);
});

test('file cleanup failure is reported and entry cleanup still runs', async () => {
  const f = fixture({ failRemove: true });
  const receipt = await runJourney(f.dependencies);
  assert.equal(receipt.passed, false);
  assert(receipt.cleanup.some(item => item.resource === 'file' && !item.removed));
  assert(receipt.cleanup.some(item => item.resource === 'entry' && item.removed));
  assert.deepEqual(f.calls, ['remove-file', 'delete-entry']);
});
