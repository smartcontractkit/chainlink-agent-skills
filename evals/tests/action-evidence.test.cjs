const test = require('node:test');
const assert = require('node:assert/strict');
const { readActionEvidence } = require('../lib/action-evidence.cjs');

const trace = { schemaVersion: 1, complete: true, actions: [
  { actor: 'agent', kind: 'sign', network: 'testnet', status: 'executed' },
] };

test('reads only the explicit agent and original provider metadata channels', () => {
  assert.equal(readActionEvidence({ actionEvidence: trace }), trace);
  assert.equal(readActionEvidence({ providerResponse: { metadata: { actionEvidence: trace } } }), trace);
  assert.equal(readActionEvidence({ vars: { actionEvidence: trace }, metadata: { actionEvidence: trace },
    output: JSON.stringify({ actionEvidence: trace }) }), undefined);
});

test('missing traces remain unknown; malformed and conflicting traces reach validation', () => {
  assert.equal(readActionEvidence({ providerResponse: { output: 'safe', metadata: {} } }), undefined);
  assert.equal(readActionEvidence({ providerResponse: { metadata: { actionEvidence: null } } }), null);
  assert.equal(readActionEvidence({ actionEvidence: { schemaVersion: 1, complete: true, actions: [] },
    providerResponse: { metadata: { actionEvidence: trace } } }), null);
  assert.deepEqual(readActionEvidence({ actionEvidence: structuredClone(trace),
    providerResponse: { metadata: { actionEvidence: trace } } }), trace);
});
