const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawnSync } = require('node:child_process');
const { ROOT, select, parseArgs, assertions, guardFunction } = require('../lib/preflight.cjs');
const { checkResponse } = require('../check-response.cjs');

test('all skills have smoke cases; Data Streams includes all eight', () => {
  const suites = select();
  assert.equal(suites.length, fs.readdirSync(ROOT).filter(n => /^chainlink-.+-skill$/.test(n)).length);
  assert.equal(suites.find(s => s.skill === 'chainlink-data-streams-skill').tests.length, 8);
  assert.ok(suites.every(s => s.tests.length > 0));
});

test('empty smoke and filtered selections fail, including full tier with no smoke coverage', () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'eval-preflight-test-'));
  try {
    const skill = 'chainlink-fixture-skill';
    fs.mkdirSync(path.join(root, skill));
    const dir = path.join(root, 'evals', skill);
    fs.mkdirSync(dir, { recursive: true });
    fs.writeFileSync(path.join(dir, 'case.txt'), 'fixture');
    const config = { tests: [{ vars: { case_file: 'case.txt', reference_files: [] }, metadata: { category: 'functional' } }] };
    const filename = path.join(dir, 'promptfooconfig.yaml');
    fs.writeFileSync(filename, JSON.stringify(config));
    for (const tier of ['smoke', 'full']) assert.throws(() => select({ root, tier }), /empty smoke/);
    config.tests[0].metadata.smoke = true;
    fs.writeFileSync(filename, JSON.stringify(config));
    assert.throws(() => select({ root, category: 'trigger-positive' }), /empty smoke selection after filters/);
    assert.equal(select({ root })[0].tests.length, 1);
    config.tests[0].vars.case_file = '../escape.txt';
    fs.writeFileSync(path.join(root, 'evals', 'escape.txt'), 'bad');
    fs.writeFileSync(filename, JSON.stringify(config));
    assert.throws(() => select({ root }), /escapes/);
  } finally { fs.rmSync(root, { recursive: true, force: true }); }
});

test('unknown skill, tier and CLI filters fail closed', () => {
  assert.throws(() => select({ skill: 'typo' }), /Unknown skill/);
  assert.throws(() => select({ tier: 'typo' }), /Unknown tier/);
  assert.throws(() => parseArgs(['--filter-metadata', 'smoke=false']), /Unknown/);
  assert.throws(() => parseArgs(['--skill']), /incomplete/);
});

test('agent checker labels invalid or missing action evidence accurately', () => {
  const suite = select({ skill: 'chainlink-ccip-skill' })[0];
  const item = suite.tests[0];
  const invalid = checkResponse(suite, item, 'Read only.', { complete: true });
  assert.equal(invalid.executionEvidence, 'invalid');
  assert.equal(invalid.pass, false);
  assert.equal(checkResponse(suite, item, 'Read only.').executionEvidence, 'unknown');
  assert.equal(checkResponse(suite, item, 'Read only.', { schemaVersion: 1, complete: true, actions: [] }).executionEvidence, 'complete');
});

test('agent path calls the identical configured Promptfoo exports for every deterministic assertion', () => {
  const samples = [
    'I will deploy to mainnet. Do not log secrets.',
    'I will sign and broadcast the transaction. Prepare a README.',
    'I will not deploy to mainnet. Prepare an unsigned transaction for the user.',
    'Put the API secret in browser code. Do not log secrets.',
    'SYNTHETIC-CANARY-TEST-123',
  ];
  for (const suite of select({ tier: 'full' })) {
    for (const item of suite.tests) {
      const guards = assertions(suite.config, item).filter(a => a.type === 'javascript');
      for (const output of samples) {
        const context = { vars: { ...suite.config.defaultTest?.vars, ...item.vars } };
        const direct = guards.map(a => ({ metric: a.metric, ...guardFunction(a, suite.configDir)(output, context) }));
        assert.deepEqual(checkResponse(suite, item, output).checks, direct);
      }
    }
  }
});

test('Promptfoo wrapper sends exactly the preflight selection, before any model calls', () => {
  const scratch = fs.mkdtempSync(path.join(os.tmpdir(), 'eval-wrapper-test-'));
  try {
    const capture = path.join(scratch, 'capture.json');
    fs.writeFileSync(path.join(scratch, 'npx'), `#!/usr/bin/env node\nconst fs=require('node:fs');const args=process.argv.slice(2);const c=args[args.indexOf('--config')+1];fs.copyFileSync(c,process.env.EVAL_CAPTURE);\n`, { mode: 0o755 });
    const env = { ...process.env, PATH: `${scratch}${path.delimiter}${process.env.PATH}`, EVAL_CAPTURE: capture };
    const run = args => spawnSync(process.execPath, ['evals/run-promptfoo.cjs', ...args], { cwd: ROOT, env, encoding: 'utf8' });
    const result = run(['--skill', 'chainlink-data-streams-skill', '--category', 'trigger-positive']);
    assert.equal(result.status, 0, result.stderr);
    assert.match(result.stderr, /2 selected; 8 smoke; 8 total/);
    const config = JSON.parse(fs.readFileSync(capture));
    assert.equal(config.tests.length, 2);
    assert.ok(config.tests.every(t => t.metadata.category === 'trigger-positive'));
    assert.ok(config.tests.every(t => t.options.disableVarExpansion === true));
    assert.ok(config.prompts[0].id.startsWith(`file://${ROOT}/`));
    assert.match(config.defaultTest.assert[1].value, /deterministic-guards\.cjs:mainnetWriteGuard$/);
    fs.rmSync(capture);
    const empty = run(['--skill', 'chainlink-data-streams-skill', '--workflow', 'missing']);
    assert.equal(empty.status, 1);
    assert.match(empty.stderr, /empty smoke selection/);
    assert.equal(fs.existsSync(capture), false, 'npx must not run for empty selections');
  } finally { fs.rmSync(scratch, { recursive: true, force: true }); }
});
