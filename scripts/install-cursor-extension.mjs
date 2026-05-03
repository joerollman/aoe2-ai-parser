import { execFileSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";

const repoRoot = process.cwd();
const extensionRoot = path.join(repoRoot, "extensions", "aoe2-aiscript-cursor-local-lab");
const packagePath = path.join(extensionRoot, "package.json");
const args = new Set(process.argv.slice(2));
const editorArgIndex = process.argv.indexOf("--editor");
const editorCommand = editorArgIndex >= 0 ? process.argv[editorArgIndex + 1] : "cursor";
const packageOnly = args.has("--package-only");

function readPackageData() {
  return JSON.parse(fs.readFileSync(packagePath, "utf8"));
}

function bumpPatchVersion(version) {
  const parts = version.split(".").map((part) => Number.parseInt(part, 10));
  assert(parts.length === 3 && parts.every((part) => Number.isInteger(part) && part >= 0), `unsupported semver version: ${version}`);
  parts[2] += 1;
  return parts.join(".");
}

function writePackageData(packageData) {
  fs.writeFileSync(packagePath, `${JSON.stringify(packageData, null, "\t")}\n`, "utf8");
}

function maybeBumpPackageVersion() {
  const packageData = readPackageData();
  if (!args.has("--bump-patch")) {
    return packageData;
  }
  const nextVersion = bumpPatchVersion(packageData.version);
  packageData.version = nextVersion;
  writePackageData(packageData);
  console.log(`Bumped ${packageData.name} to ${nextVersion}`);
  return packageData;
}

const packageData = maybeBumpPackageVersion();
const extensionId = `${packageData.publisher}.${packageData.name}`;
const vsixName = `${packageData.name}-${packageData.version}.vsix`;
const vsixPath = path.join(extensionRoot, vsixName);

function run(command, args, options = {}) {
  console.log([command, ...args].join(" "));
  const usesWindowsCommandShim = process.platform === "win32" && ["npx", "cursor", "code"].includes(command);
  return execFileSync(command, args, {
    cwd: options.cwd || repoRoot,
    encoding: "utf8",
    stdio: options.stdio || "pipe",
    shell: usesWindowsCommandShim,
    windowsHide: true,
  });
}

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

assert(["cursor", "code"].includes(editorCommand), "--editor must be either cursor or code");

function removeOldVsixFiles() {
  for (const entry of fs.readdirSync(extensionRoot)) {
    if (entry.endsWith(".vsix")) {
      fs.rmSync(path.join(extensionRoot, entry), { force: true });
    }
  }
}

function installedExtensionRoot() {
  if (process.platform === "win32") {
    const userProfile = process.env.USERPROFILE || "";
    if (editorCommand === "cursor") {
      return path.join(userProfile, ".cursor", "extensions");
    }
    return path.join(userProfile, ".vscode", "extensions");
  }
  const home = process.env.HOME || "";
  if (editorCommand === "cursor") {
    return path.join(home, ".cursor", "extensions");
  }
  return path.join(home, ".vscode", "extensions");
}

function verifyInstalledExtension() {
  const installedExtensionPath = path.join(installedExtensionRoot(), `${extensionId}-${packageData.version}`);
  const installedClientPath = path.join(installedExtensionPath, "languageExtension", "out", "extension.js");
  assert(fs.existsSync(installedClientPath), `installed extension.js not found: ${installedClientPath}`);
  const clientSource = fs.readFileSync(installedClientPath, "utf8");
  for (const needle of [
    "function formatPackageIssueGroups",
    "function bundledLabPath",
    "payload.issue_groups || []",
    '"lint-package", packageRoot, "--json", "--report", reportPath, "--fail-level", settings.packageFailLevel',
  ]) {
    assert(clientSource.includes(needle), `installed extension is missing: ${needle}`);
  }
}

run("node", ["scripts/generate-diagnostic-registry.mjs", "--check"]);
run("node", ["scripts/verify-cursor-extension.mjs"]);
run("node", ["scripts/sync-extension-lab.mjs"]);
removeOldVsixFiles();
run("npx", ["@vscode/vsce", "package"], { cwd: extensionRoot, stdio: "inherit" });
assert(fs.existsSync(vsixPath), `VSIX was not created: ${vsixPath}`);
if (packageOnly) {
  console.log(`Packaged ${vsixPath}`);
  process.exit(0);
}

run(editorCommand, ["--install-extension", vsixPath, "--force"], { stdio: "inherit" });
verifyInstalledExtension();

console.log(`Installed and verified ${extensionId}@${packageData.version} for ${editorCommand}`);
console.log(`Reload ${editorCommand === "cursor" ? "Cursor" : "VS Code"} before testing the command palette.`);
