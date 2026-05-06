import { execFileSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";

const repoRoot = process.cwd();
const extensionRoot = path.join(repoRoot, "extensions", "aoe2-ai-parser-extension");
const packageData = JSON.parse(fs.readFileSync(path.join(extensionRoot, "package.json"), "utf8"));
const vsixPath = path.join(extensionRoot, `${packageData.name}-${packageData.version}.vsix`);
const target = process.argv[2];

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

function run(command, args, options = {}) {
  console.log([command, ...args].join(" "));
  const usesWindowsCommandShim = process.platform === "win32" && ["npm", "npx"].includes(command);
  execFileSync(command, args, {
    cwd: options.cwd || repoRoot,
    stdio: "inherit",
    shell: usesWindowsCommandShim,
    windowsHide: true,
  });
}

assert(target === "vscode" || target === "openvsx", "usage: node scripts/publish-extension.mjs vscode|openvsx");
run("npm", ["run", "package:editor-extension"]);
assert(fs.existsSync(vsixPath), `VSIX was not created: ${vsixPath}`);

if (target === "vscode") {
  run("npx", ["@vscode/vsce", "publish", "--packagePath", vsixPath], { cwd: extensionRoot });
} else {
  run("npx", ["ovsx", "publish", vsixPath], { cwd: extensionRoot });
}
