const fs = require('fs');
const path = require('path');

module.exports = async function ({ vars }) {
  const casePath = path.resolve(__dirname, '..', vars.case_file);
  return fs.readFileSync(casePath, 'utf8').trim();
};
