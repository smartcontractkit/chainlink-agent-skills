const fs = require("fs");
const path = require("path");

module.exports = function ({ vars }) {
  const caseFile = vars.case_file;
  const content = fs.readFileSync(path.resolve(__dirname, "..", caseFile), "utf8").trim();

  const skillPath = path.resolve(__dirname, "../../chainlink-cre-skill/SKILL.md");
  const skillContent = fs.readFileSync(skillPath, "utf8").trim();

  return [
    { role: "system", content: skillContent },
    { role: "user", content: content },
  ];
};
