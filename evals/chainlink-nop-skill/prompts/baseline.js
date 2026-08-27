const fs = require("fs");
const path = require("path");

module.exports = function ({ vars }) {
  const caseText = fs.readFileSync(path.resolve(__dirname, "..", vars.case_file), "utf8").trim();
  if (!vars.fixture_file) return caseText;

  const fixture = fs.readFileSync(path.resolve(__dirname, "..", vars.fixture_file), "utf8").trim();
  return `${caseText}\n\n# Synthetic replay fixture\n\n${fixture}`;
};
