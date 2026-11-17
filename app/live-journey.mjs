import assert from 'node:assert/strict';
import { randomUUID } from 'node:crypto';

// AWS calls are injected so failure and cleanup paths can be tested offline.
export async function runJourney(d) {
  const results = [];
  const cleanup = [];
  let entryId;
  let path;
  let ownerSignedIn = false;
  let failure;
  const mark = name => results.push({ name, passed: true });
  const data = response => {
    if (response.errors?.length) throw new Error(response.errors.map(x => x.message).join('; '));
    return response.data;
  };
  const asUser = async user => {
    await d.signOut().catch(() => {});
    ownerSignedIn = false;
    await d.signIn(user);
    ownerSignedIn = user === d.users[0];
  };
  try {
    await asUser(d.users[0]);
    const session = await d.fetchAuthSession();
    assert(session.identityId, 'Owner must have an identity-pool identity');
    mark('Cognito sign-in and identity-pool credentials');
    const entry = data(await d.client.models.Entry.create({ title: `Isolation check ${randomUUID()}`, notes: 'Temporary integration check', explored: false }));
    assert(entry?.id, 'Entry create returned no ID');
    entryId = entry.id;
    mark('Create private entry');
    const updated = data(await d.client.models.Entry.update({ id: entryId, notes: 'Updated by owner', explored: true }));
    assert(updated?.explored);
    mark('Update private entry');
    await asUser(d.users[0]);
    assert.equal(data(await d.client.models.Entry.get({ id: entryId }))?.notes, 'Updated by owner');
    mark('Entry persists across sign-out/sign-in');
    const inspection = JSON.parse(data(await d.client.queries.inspectEntry({ text: 'one two three' })));
    assert.equal(inspection.words, 3);
    assert.equal(inspection.service, 'AWS Lambda');
    mark('Authenticated GraphQL-to-Lambda response');
    path = `private/${session.identityId}/integration-${randomUUID()}.txt`;
    await d.uploadData({ path, data: 'private verification bytes', options: { contentType: 'text/plain' } }).result;
    const file = await d.downloadData({ path }).result;
    assert.equal(await file.body.text(), 'private verification bytes');
    mark('Owner uploads and downloads private file');
    await asUser(d.users[1]);
    assert(!data(await d.client.models.Entry.get({ id: entryId })));
    mark('Second user cannot read first user entry');
    let nextToken;
    const seenTokens = new Set();
    for (let page = 0; page < 20; page += 1) {
      const response = await d.client.models.Entry.list({ limit: 100, ...(nextToken ? { nextToken } : {}) });
      const listed = data(response);
      assert(Array.isArray(listed), 'Entry list returned no item array');
      assert(!listed.some(item => item.id === entryId));
      nextToken = response.nextToken;
      if (!nextToken) break;
      assert(!seenTokens.has(nextToken), 'Entry list repeated a page token');
      seenTokens.add(nextToken);
      assert(page < 19, 'Entry list exceeded the bounded check; visibility remains unverified');
    }
    mark('Second user cannot list first user entry');
    const deniedUpdate = await d.client.models.Entry.update({ id: entryId, title: 'Unauthorized update' });
    assert(deniedUpdate.errors?.length);
    mark('Second user cannot update first user entry');
    let denied = false;
    try { await d.downloadData({ path }).result; } catch { denied = true; }
    assert(denied);
    mark('Second user cannot download first user file');
    denied = false;
    try { await d.uploadData({ path, data: 'unauthorized replacement' }).result; } catch { denied = true; }
    assert(denied);
    mark('Second user cannot overwrite first user file');
    denied = false;
    try { await d.remove({ path }); } catch { denied = true; }
    assert(denied);
    mark('Second user cannot delete first user file');
    let visible = false;
    try {
      const listing = await d.list({ path: `private/${session.identityId}/`, options: { listAll: true } });
      visible = listing.items?.some(item => item.path === path) ?? false;
    } catch { /* An access error is also a successful denial. */ }
    assert(!visible);
    mark('Second user cannot list first user file');
    await d.signOut();
    ownerSignedIn = false;
    const unauthorized = await d.fetch(d.endpoint, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ query: 'query { listEntries { items { id } } }' }) });
    assert([401, 403].includes(unauthorized.status));
    mark('Unauthenticated API request rejected');
  } catch (error) {
    failure = error;
    results.push({ name: 'Journey stopped', passed: false, detail: error.message });
  } finally {
    if (entryId || path) {
      if (!ownerSignedIn) {
        try { await asUser(d.users[0]); } catch (error) {
          cleanup.push({ resource: 'owner sign-in', removed: false, detail: error.message });
          failure ??= error;
        }
      }
      if (ownerSignedIn && path) {
        try {
          await d.remove({ path });
          const after = await d.list({ path: `private/${path.split('/')[1]}/`, options: { listAll: true } });
          assert(!after.items?.some(item => item.path === path));
          cleanup.push({ resource: 'file', removed: true });
        } catch (error) {
          cleanup.push({ resource: 'file', removed: false, detail: error.message });
          failure ??= error;
        }
      }
      if (ownerSignedIn && entryId) {
        try {
          data(await d.client.models.Entry.delete({ id: entryId }));
          assert(!data(await d.client.models.Entry.get({ id: entryId })));
          cleanup.push({ resource: 'entry', removed: true });
        } catch (error) {
          cleanup.push({ resource: 'entry', removed: false, detail: error.message });
          failure ??= error;
        }
      }
    }
    try { await d.signOut(); } catch (error) {
      cleanup.push({ resource: 'session', removed: false, detail: error.message });
      failure ??= error;
    }
  }
  return { passed: !failure, results, cleanup };
}
