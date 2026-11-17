// Read the Python producer's exact JSON strings; this exercise makes no network calls.
import { readFileSync } from 'node:fs';

const cases = JSON.parse(readFileSync(0, 'utf8'));
const observations = Object.fromEntries(cases.map(({ name, value }) => [name, {
  raw: value,
  nfc: value.normalize('NFC'),
  nfkc: value.normalize('NFKC'),
  utf16_units: value.length,
  code_points: Array.from(value).length,
  utf8_bytes: Buffer.byteLength(value, 'utf8'),
}]));
process.stdout.write(`${JSON.stringify({ unicode_version: process.versions.unicode, observations })}\n`);
