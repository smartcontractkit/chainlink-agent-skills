const fs = require("fs");
const path = require("path");

function readRequiredFile(filePath, description) {
  try {
    return fs.readFileSync(filePath, "utf8").trim();
  } catch (error) {
    throw new Error(`Unable to read ${description} at ${filePath}: ${error.message}`);
  }
}

function resolveReferencePath(skillRoot, referenceFile) {
  if (typeof referenceFile !== "string" || referenceFile.length === 0) {
    throw new Error("vars.reference_files must contain only non-empty string paths.");
  }

  if (path.isAbsolute(referenceFile)) {
    throw new Error(`Reference path must be relative to the skill root: ${referenceFile}`);
  }

  const resolvedPath = path.resolve(skillRoot, referenceFile);
  const relativePath = path.relative(skillRoot, resolvedPath);
  if (relativePath === "" || relativePath === ".." || relativePath.startsWith(`..${path.sep}`)) {
    throw new Error(`Reference path escapes the skill root: ${referenceFile}`);
  }

  let canonicalPath;
  try {
    canonicalPath = fs.realpathSync(resolvedPath);
  } catch (error) {
    throw new Error(`Unable to resolve reference ${referenceFile}: ${error.message}`);
  }

  const canonicalRelativePath = path.relative(skillRoot, canonicalPath);
  if (canonicalRelativePath === "" || canonicalRelativePath === ".." || canonicalRelativePath.startsWith(`..${path.sep}`)) {
    throw new Error(`Reference path escapes the skill root: ${referenceFile}`);
  }

  return canonicalPath;
}

module.exports = function withSkillPrompt({ skillId, evalDir, vars }) {
  if (!vars || !Array.isArray(vars.reference_files)) {
    throw new Error("vars.reference_files must be an array.");
  }

  const casePath = path.resolve(evalDir, vars.case_file);
  const skillRoot = fs.realpathSync(path.resolve(evalDir, "..", "..", skillId));
  const skillPath = path.join(skillRoot, "SKILL.md");
  const skillContent = readRequiredFile(skillPath, `${skillId} SKILL.md`);
  const references = vars.reference_files.map((referenceFile) => {
    const referencePath = resolveReferencePath(skillRoot, referenceFile);
    const referenceContent = readRequiredFile(referencePath, `reference ${referenceFile}`);
    return `# Reference: ${referenceFile}\n\n${referenceContent}`;
  });

  return [
    { role: "system", content: [skillContent, ...references].join("\n\n") },
    { role: "user", content: readRequiredFile(casePath, `case ${vars.case_file}`) },
  ];
};
