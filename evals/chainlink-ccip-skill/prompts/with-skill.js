const path = require("path");
const withSkillPrompt = require("../../shared/with-skill-prompt");

module.exports = function ({ vars }) {
  return withSkillPrompt({
    skillId: "chainlink-ccip-skill",
    evalDir: path.resolve(__dirname, ".."),
    vars,
  });
};
