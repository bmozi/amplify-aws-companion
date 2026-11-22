/* Small deterministic teaching models. No AWS calls, persistence, or networking. */
(function (root) {
  'use strict';
  const models = {
    request({ allowed, failure }) {
      if (!allowed) return { saved: false, known: true, steps: ['Browser sends the request.', 'The application refuses access.', 'No repair record is written.'], lesson: 'A working page does not grant permission to save a repair. The denial is the result in this model.' };
      if (failure === 'before') return { saved: false, known: false, steps: ['Browser sends the request.', 'Access is allowed.', 'The connection is lost before the write.'], lesson: 'This model shows that no record was saved. The customer sees a lost connection, which alone cannot reveal where processing stopped.' };
      if (failure === 'after') return { saved: true, known: false, steps: ['Browser sends the request.', 'Access is allowed.', 'The database commits one repair record.', 'The reply is lost before reaching the browser.'], lesson: 'The repair exists even though the browser has no confirmation. A status lookup tied to the original request can help resolve that uncertainty.' };
      return { saved: true, known: true, steps: ['Browser sends the request.', 'Access is allowed.', 'The database commits one repair record.', 'The browser receives its confirmation.'], lesson: 'The confirmation describes the saved request in this model. It does not establish that the repair itself has been completed.' };
    },
    retry({ firstSaved, retry, sameKey, deduplicate }) {
      const repeated = retry && !(firstSaved && sameKey && deduplicate);
      const records = Number(firstSaved) + Number(repeated);
      const lesson = !retry ? 'Without a retry or status check, the customer’s uncertainty remains.'
        : firstSaved && sameKey && deduplicate ? 'The atomic acceptance rule finds the original key and returns the same repair. The retry adds no new work.'
        : firstSaved ? 'The retry creates another repair. Reusing a key helps only when the server enforces an atomic duplicate check; a new key represents new work in this model.'
        : 'The retry creates the first repair because the original attempt never committed. Its confirmation still needs to reach the customer.';
      return { records, lesson };
    },
    recovery({ interval, restore, lossTarget, timeTarget }) {
      return { lossFits: interval <= lossTarget, timeFits: restore <= timeTarget,
        lesson: `With successful snapshots every ${interval} minutes, a failure just before the next snapshot could lose almost ${interval} minutes of updates. The assumed end-to-end recovery takes ${restore} minutes. These are separate promises. Delayed backups, invalid data, missing keys, and untested dependencies can make the real outcome worse.` };
    }
  };
  root.AwsLearningModels = models;
  if (typeof module !== 'undefined' && module.exports) module.exports = models;
})(globalThis);
