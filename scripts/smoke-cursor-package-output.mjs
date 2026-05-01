import { execFileSync } from "node:child_process";
import Module from "node:module";
import path from "node:path";
import { createRequire } from "node:module";

const repoRoot = process.cwd();
const extensionPath = path.join(
  repoRoot,
  "extensions",
  "aoe2-aiscript-cursor-local-lab",
  "languageExtension",
  "out",
  "extension.js"
);
const samplesPath = path.join(repoRoot, "extensions", "aoe2-aiscript-cursor-local-lab", "samples");
const require = createRequire(import.meta.url);

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

const originalLoad = Module._load;
Module._load = function patchedLoad(request, parent, isMain) {
  if (request === "vscode") {
    return {
      window: {
        createOutputChannel: () => ({
          clear() {},
          append() {},
          appendLine() {},
          show() {},
        }),
        activeTextEditor: undefined,
        showWarningMessage() {},
        showErrorMessage() {},
        showInformationMessage() {},
        showTextDocument() {},
      },
      workspace: {
        workspaceFolders: [],
        getConfiguration: () => ({
          get: (_key, fallback) => fallback,
        }),
        createFileSystemWatcher: () => ({}),
        openTextDocument: () => Promise.resolve({}),
      },
      languages: {
        setLanguageConfiguration() {},
      },
      commands: {
        registerCommand: () => ({ dispose() {} }),
      },
    };
  }
  if (request === "vscode-languageclient") {
    return {
      TransportKind: { ipc: 0 },
      LanguageClient: class {
        start() {}
        stop() {}
      },
    };
  }
  return originalLoad.call(this, request, parent, isMain);
};

let extensionModule;
try {
  extensionModule = require(extensionPath);
} finally {
  Module._load = originalLoad;
}

assert(extensionModule._test, "extension test hooks are not exported");
assert(
  typeof extensionModule._test.formatPackageIssueGroups === "function",
  "formatPackageIssueGroups test hook is missing"
);

let stdout = "";
let stderr = "";
try {
  stdout = execFileSync(
    "python",
    ["-m", "aoe2_ai_lab", "lint-package", samplesPath, "--json", "--fail-level", "error"],
    {
      cwd: repoRoot,
      env: { ...process.env, PYTHONPATH: "src" },
      encoding: "utf8",
      windowsHide: true,
    }
  );
} catch (error) {
  stdout = String(error.stdout || "");
  stderr = String(error.stderr || "");
}

assert(stdout.includes("{"), `lint-package --json did not produce JSON stdout; stderr: ${stderr.slice(0, 500)}`);

const formatted = extensionModule._test.formatPackageIssueGroups(stdout, repoRoot);

for (const needle of [
  "Package summary:",
  "  roots: 5",
  "  reachable files: 7",
  "  lint findings: 11",
  "Issue categories:",
  "[lint] command-role-mismatch (2)",
  "[integrity] stale-ai-root (1)",
  "[integrity] duplicate-root-target (1)",
  "[integrity] unreachable-per-file (2)",
  "docs: [validator-diagnostic-codes.md#diagnostic-command-role-mismatch]",
  "extensions\\aoe2-aiscript-cursor-local-lab\\samples\\lab_diagnostics_sample.per:25",
]) {
  assert(formatted.includes(needle), `formatted package output is missing: ${needle}`);
}

assert(!formatted.includes("package integrity:\n"), "formatter should not return old summary output");
assert(!formatted.includes('"issue_groups"'), "formatter should not dump raw JSON");

console.log("Cursor package lint output smoke test passed.");
