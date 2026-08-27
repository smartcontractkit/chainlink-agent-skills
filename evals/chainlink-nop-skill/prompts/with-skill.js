const fs = require("fs");
const path = require("path");
const withSkillPrompt = require("../../shared/with-skill-prompt");

module.exports = function ({ vars }) {
  const messages = withSkillPrompt({
    skillId: "chainlink-nop-skill",
    evalDir: path.resolve(__dirname, ".."),
    vars,
  });
  if (!vars.fixture_file) return messages;

  const fixture = fs.readFileSync(path.resolve(__dirname, "..", vars.fixture_file), "utf8").trim();
  messages[messages.length - 1].content += `\n\n# Synthetic replay fixture\n\n${fixture}`;
  return messages;
};
