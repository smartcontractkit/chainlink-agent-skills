// Run this entry point instead of a direct, unchecked promptfoo invocation.
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawnSync } = require('node:child_process');
const { select, parseArgs, report } = require('./lib/preflight.cjs');

function absoluteFiles(value, configDir) {
  if (typeof value === 'string' && value.startsWith('file://')) return `file://${path.resolve(configDir, value.slice(7))}`;
  if (Array.isArray(value)) return value.map(v => absoluteFiles(v, configDir));
  if (value && typeof value === 'object') return Object.fromEntries(Object.entries(value).map(([k, v]) => [k, absoluteFiles(v, configDir)]));
  return value;
}

function selectedConfig(suite) {
  // reference_files is one array-valued input, not a matrix of test variants.
  const tests = suite.tests.map(t => ({ ...t, options: { ...t.options, disableVarExpansion: true } }));
  return absoluteFiles({ ...suite.config, tests }, suite.configDir);
}

function run(argv) {
  const options = parseArgs(argv);
  if (!options.skill) throw new Error('--skill is required for model runs');
  const suites = select(options);
  report(suites); // Complete all preflight checks before starting any model process.
  if (options['dry-run']) return 0;
  const suite = suites[0];
  const scratch = fs.mkdtempSync(path.join(os.tmpdir(), 'chainlink-eval-'));
  try {
    const configPath = path.join(scratch, 'config.json');
    fs.writeFileSync(configPath, JSON.stringify(selectedConfig(suite)));
    const args = ['--no-install', 'promptfoo', 'eval', '--config', configPath];
    if (options['no-cache']) args.push('--no-cache');
    if (options.output) args.push('--output', path.resolve(options.output));
    const result = spawnSync('npx', args, { cwd: suite.configDir, stdio: 'inherit' });
    if (result.error) throw result.error;
    return result.status ?? 1;
  } finally { fs.rmSync(scratch, { recursive: true, force: true }); }
}

module.exports = { absoluteFiles, selectedConfig, run };
if (require.main === module) {
  try { process.exitCode = run(process.argv.slice(2)); }
  catch (error) { console.error(`Eval failed: ${error.message}`); process.exitCode = 1; }
}
