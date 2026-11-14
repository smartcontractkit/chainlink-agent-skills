'use strict';

const { isDeepStrictEqual } = require('node:util');

// These are harness-owned channels, never response text or test/model vars.
// Promptfoo passes the provider's original response into assertion context.
// A provider must construct metadata.actionEvidence from its own tool log.
function readActionEvidence(context = {}) {
  const direct = context.actionEvidence;
  const provider = context.providerResponse?.metadata?.actionEvidence;
  // Reject conflicting traces rather than let a clean trace mask a violation.
  if (direct !== undefined && provider !== undefined && !isDeepStrictEqual(direct, provider)) return null;
  return provider !== undefined ? provider : direct;
}

module.exports = { readActionEvidence };
