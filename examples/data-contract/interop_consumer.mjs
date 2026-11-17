// Inspect exactly the JSON text supplied by the Python producer; no network.
import { readFileSync } from 'node:fs';

const cases = JSON.parse(readFileSync(0, 'utf8'));
const results = {};
for (const item of cases) {
  const value = JSON.parse(item.raw);
  if (item.name === 'safe_update') {
    results[item.name] = {
      part_id: value.part_id,
      price_cents: value.price_cents,
      has_note: Object.hasOwn(value, 'note'),
    };
  } else if (item.name === 'numeric_event_id' || item.name === 'text_event_id') {
    results[item.name] = {
      type: typeof value.event_id,
      value: String(value.event_id),
      safe_integer: Number.isSafeInteger(value.event_id),
    };
  } else if (item.name === 'duplicate_price') {
    results[item.name] = { price_cents: value.price_cents };
  } else if (item.name === 'emoji_note') {
    results[item.name] = {
      utf16_units: value.note.length,
      code_points: Array.from(value.note).length,
      utf8_bytes: Buffer.byteLength(value.note, 'utf8'),
    };
  } else {
    throw new Error(`Unknown case: ${item.name}`);
  }
}
process.stdout.write(`${JSON.stringify(results)}\n`);
