import fs from 'node:fs';
import { Amplify } from 'aws-amplify';
import { signIn, signOut, fetchAuthSession } from 'aws-amplify/auth';
import { generateClient } from 'aws-amplify/data';
import { uploadData, downloadData, remove, list } from 'aws-amplify/storage';
import { runJourney } from './live-journey.mjs';

const outputs = JSON.parse(fs.readFileSync('amplify_outputs.json', 'utf8'));
const users = JSON.parse(fs.readFileSync('../evidence/live/test-users.json', 'utf8'));
if (!Array.isArray(users) || users.length < 2 || !users[0]?.username || !users[1]?.username || users[0].username === users[1].username) {
  throw new Error('Provide two distinct test users in evidence/live/test-users.json');
}
Amplify.configure(outputs);
const client = generateClient();
const receipt = await runJourney({ users, client, signIn, signOut, fetchAuthSession, uploadData, downloadData, remove, list, fetch, endpoint: outputs.data.url });
fs.writeFileSync('../evidence/live/integration-results.json', JSON.stringify({ at: new Date().toISOString(), ...receipt }, null, 2), { mode: 0o600 });
fs.chmodSync('../evidence/live/integration-results.json', 0o600);
for (const result of receipt.results) console.log(result.passed ? 'PASS' : 'FAIL', result.name);
if (!receipt.passed) {
  console.error('Live check failed; see private receipt for check and cleanup status.');
  process.exitCode = 1;
}
