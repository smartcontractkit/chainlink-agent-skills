// Trusted harness input only. Never take action evidence from model response text.
const fs = require('node:fs');
const { select, parseArgs, assertions, guardFunction, report } = require('./lib/preflight.cjs');

function checkResponse(suite, test, output, actionEvidence) {
  if (typeof output !== 'string') throw new Error('output must be a string');
  const context = { vars: { ...suite.config.defaultTest?.vars, ...test.vars }, actionEvidence };
  const checks = assertions(suite.config, test).filter(a => a.type === 'javascript').map(a =>
    ({ metric: a.metric, ...guardFunction(a, suite.configDir)(output, context) }));
  const evidenceStatus = !checks.length ? 'not checked' : checks.some(c => c.evidenceStatus === 'invalid') ? 'invalid'
    : checks.every(c => c.evidenceStatus === 'complete') ? 'complete'
    : checks.some(c => c.evidenceStatus === 'incomplete') ? 'incomplete' : 'unknown';
  return { pass: checks.every(c => c.pass), checks,
    executionEvidence: evidenceStatus };
}

module.exports = { checkResponse };
if (require.main === module) {
  try {
    const options = parseArgs(process.argv.slice(2));
    if (!options.skill || !options.case) throw new Error('--skill and --case are required');
    const suites = select(options);
    report(suites);
    const input = JSON.parse(fs.readFileSync(0, 'utf8'));
    const result = checkResponse(suites[0], suites[0].tests[0], input.output, input.actionEvidence);
    console.log(JSON.stringify(result, null, 2));
    if (!result.pass) process.exitCode = 1;
  } catch (error) { console.error(`Guard check failed: ${error.message}`); process.exitCode = 1; }
}
