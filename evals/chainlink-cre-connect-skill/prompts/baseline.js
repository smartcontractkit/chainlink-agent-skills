const fs = require("fs");
const path = require("path");

module.exports = function ({ vars }) {
  return fs.readFileSync(path.resolve(__dirname, "..", vars.case_file), "utf8").trim();
};
