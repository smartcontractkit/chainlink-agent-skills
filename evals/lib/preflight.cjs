const fs = require('node:fs');
const path = require('node:path');
const { execFileSync } = require('node:child_process');

const ROOT = path.resolve(__dirname, '../..');

function loadConfig(filename) {
  // Use the same YAML parser as the repository's existing config validator.
  return JSON.parse(execFileSync('ruby', ['-rpsych', '-rjson', '-e',
    'puts JSON.generate(Psych.safe_load(File.read(ARGV.fetch(0)), aliases: true))', filename],
  { encoding: 'utf8', maxBuffer: 10 * 1024 * 1024 }));
}

function requiredFile(root, relative) {
  if (typeof relative !== 'string' || !relative || path.isAbsolute(relative)) {
    throw new Error(`Expected a relative file path: ${relative}`);
  }
  const resolved = fs.realpathSync(path.resolve(root, relative));
  const inside = path.relative(fs.realpathSync(root), resolved);
  if (inside.startsWith(`..${path.sep}`) || inside === '..' || path.isAbsolute(inside) || !fs.statSync(resolved).isFile()) {
    throw new Error(`File escapes its root or is not a file: ${relative}`);
  }
  return resolved;
}

function assertions(config, test) {
  return [...(config.defaultTest?.assert || []), ...(test.assert || [])];
}

function guardFunction(assertion, configDir) {
  const match = /^file:\/\/(.+\.cjs):([A-Za-z][A-Za-z0-9]*)$/.exec(assertion.value || '');
  if (!match) throw new Error(`Deterministic assertion must use a shared module export: ${assertion.metric}`);
  const filename = path.resolve(configDir, match[1]);
  if (filename !== path.join(ROOT, 'evals/lib/deterministic-guards.cjs')) {
    throw new Error(`Unrecognized deterministic module: ${filename}`);
  }
  const fn = require(filename)[match[2]];
  if (typeof fn !== 'function') throw new Error(`Missing guard export: ${match[2]}`);
  return fn;
}

function select(options = {}) {
  const root = options.root || ROOT;
  const tier = options.tier || 'smoke';
  if (!['smoke', 'full'].includes(tier)) throw new Error(`Unknown tier: ${tier}`);
  const skills = fs.readdirSync(root).filter(name => /^chainlink-.+-skill$/.test(name) &&
    fs.statSync(path.join(root, name)).isDirectory()).sort();
  if (options.skill && !skills.includes(options.skill)) throw new Error(`Unknown skill: ${options.skill}`);
  const suites = [];
  for (const skill of skills.filter(name => !options.skill || name === options.skill)) {
    const configDir = path.join(root, 'evals', skill);
    const config = loadConfig(path.join(configDir, 'promptfooconfig.yaml'));
    if (!Array.isArray(config.tests) || !config.tests.length) throw new Error(`${skill}: no tests`);
    const smokeCount = config.tests.filter(test => test.metadata?.smoke === true).length;
    if (!smokeCount) throw new Error(`${skill}: empty smoke selection`);
    for (const test of config.tests) {
      requiredFile(configDir, test.vars?.case_file);
      // The confidential attester uses a different prompt context contract.
      if (skill !== 'chainlink-confidential-ai-attester-skill') {
        if (!Array.isArray(test.vars?.reference_files)) throw new Error(`${skill}: reference_files must be an array`);
        for (const file of test.vars.reference_files) requiredFile(path.join(root, skill), file);
      }
      for (const assertion of assertions(config, test).filter(a => a.type === 'javascript')) {
        guardFunction(assertion, configDir);
      }
    }
    const tests = config.tests.filter(test =>
      (tier === 'full' || test.metadata?.smoke === true) &&
      (!options.category || test.metadata?.category === options.category) &&
      (!options.workflow || (test.vars?.workflow || test.metadata?.workflow) === options.workflow) &&
      (!options.case || test.vars.case_file === options.case));
    if (!tests.length) throw new Error(`${skill}: empty ${tier} selection after filters`);
    suites.push({ skill, configDir, config, tests, smokeCount, total: config.tests.length });
  }
  return suites;
}

function parseArgs(argv) {
  const options = {};
  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    if (['--json', '--dry-run', '--no-cache'].includes(arg)) options[arg.slice(2)] = true;
    else if (['--skill', '--tier', '--category', '--workflow', '--case', '--output'].includes(arg) && argv[i + 1] && !argv[i + 1].startsWith('--')) {
      options[arg.slice(2)] = argv[++i];
    } else throw new Error(`Unknown or incomplete option: ${arg}`);
  }
  return options;
}

function report(suites, stream = process.stderr) {
  for (const suite of suites) stream.write(`${suite.skill}: ${suite.tests.length} selected; ${suite.smokeCount} smoke; ${suite.total} total\n`);
}

module.exports = { ROOT, loadConfig, requiredFile, assertions, guardFunction, select, parseArgs, report };

if (require.main === module) {
  try {
    const options = parseArgs(process.argv.slice(2));
    const suites = select(options);
    report(suites);
    if (options.json) console.log(JSON.stringify(suites.map(s => ({ skill: s.skill, tests: s.tests })), null, 2));
  } catch (error) { console.error(`Preflight failed: ${error.message}`); process.exitCode = 1; }
}
