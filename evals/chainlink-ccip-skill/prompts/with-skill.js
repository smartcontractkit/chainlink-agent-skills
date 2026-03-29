const fs = require('fs');
const path = require('path');

module.exports = async function ({ vars }) {
  const casePath = path.resolve(__dirname, '..', vars.case_file);
  const skillPath = path.resolve(__dirname, '..', '..', '..', 'chainlink-ccip-skill', 'SKILL.md');

  return [
    {
      role: 'system',
      content: fs.readFileSync(skillPath, 'utf8'),
    },
    {
      role: 'user',
      content: fs.readFileSync(casePath, 'utf8').trim(),
    },
  ];
};
