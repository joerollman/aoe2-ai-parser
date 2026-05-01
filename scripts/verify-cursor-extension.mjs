import fs from "node:fs";
import path from "node:path";

const repoRoot = process.cwd();
const extensionRoot = path.join(repoRoot, "extensions", "aoe2-aiscript-cursor-local-lab");
const packagePath = path.join(extensionRoot, "package.json");
const serverPath = path.join(extensionRoot, "languageExtension", "out", "server.js");
const clientPath = path.join(extensionRoot, "languageExtension", "out", "extension.js");
const completionsPath = path.join(extensionRoot, "data", "completions.json");
const diagnosticCodesPath = path.join(extensionRoot, "data", "diagnostic-codes.json");
const grammarPath = path.join(extensionRoot, "syntaxes", "aoe2aiscript.tmLanguage.json");
const workspaceSettingsPath = path.join(repoRoot, ".vscode", "settings.json");
const installScriptPath = path.join(repoRoot, "scripts", "install-cursor-extension.mjs");
const syncLabScriptPath = path.join(repoRoot, "scripts", "sync-extension-lab.mjs");
const completionSmokePath = path.join(repoRoot, "scripts", "smoke-cursor-completions.mjs");
const packageOutputSmokePath = path.join(repoRoot, "scripts", "smoke-cursor-package-output.mjs");
const symbolDocsPath = path.join(repoRoot, "docs", "reference", "generated", "ai-symbol-reference.md");
const symbolDocsDir = path.join(repoRoot, "docs", "reference", "generated", "symbols");

function readText(filePath) {
  return fs.readFileSync(filePath, "utf8");
}

function readJson(filePath) {
  return JSON.parse(readText(filePath));
}

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

function assertIncludes(text, needle, filePath) {
  assert(text.includes(needle), `${path.relative(repoRoot, filePath)} is missing: ${needle}`);
}

const packageData = readJson(packagePath);
const serverSource = readText(serverPath);
const clientSource = readText(clientPath);
const installScriptSource = readText(installScriptPath);
const syncLabScriptSource = readText(syncLabScriptPath);
const completionSmokeSource = readText(completionSmokePath);
const packageOutputSmokeSource = readText(packageOutputSmokePath);
const symbolDocsSource = readText(symbolDocsPath);
const completions = readJson(completionsPath);
const diagnosticCodes = readJson(diagnosticCodesPath);
const grammarSource = readText(grammarPath);
const workspaceSettings = readJson(workspaceSettingsPath);
const language = packageData.contributes.languages[0];
const commands = new Set(packageData.contributes.commands.map((command) => command.command));
const semanticTokenTypes = new Set((packageData.contributes.semanticTokenTypes || []).map((tokenType) => tokenType.id));
const completionLabels = new Set(completions.items.map((item) => item.label));

assert(language.extensions.includes(".per"), "extension must register .per files");
assert(language.extensions.includes(".ai"), "extension must register .ai files");

for (const command of [
  "aoe2AiScript.lintCurrentFile",
  "aoe2AiScript.lintPackage",
  "aoe2AiScript.generatePackageReport",
  "aoe2AiScript.openLatestPackageReport",
  "aoe2AiScript.openSymbolDocsPreview",
  "aoe2AiScript.openDiagnosticDocsPreview",
]) {
  assert(commands.has(command), `missing command contribution: ${command}`);
  assertIncludes(clientSource, `registerCommand("${command}"`, clientPath);
}

assertIncludes(clientSource, "markdown.showPreviewToSide", clientPath);
assertIncludes(clientSource, "vscode.openWith", clientPath);
assertIncludes(clientSource, "vscode.markdown.preview.editor", clientPath);
assertIncludes(clientSource, "ViewColumn.Beside", clientPath);
assertIncludes(clientSource, "function openSymbolDocsPreview", clientPath);
assertIncludes(clientSource, "function symbolDocsHover", clientPath);
assertIncludes(clientSource, "function symbolDocPath", clientPath);
assertIncludes(clientSource, "registerHoverProvider", clientPath);
assertIncludes(clientSource, "Open in Markdown Preview", clientPath);
assertIncludes(clientSource, "markdown.isTrusted = true", clientPath);
assertIncludes(clientSource, "function commandUriForSymbolDocs", clientPath);
assertIncludes(clientSource, "function symbolReferencePath", clientPath);
assertIncludes(clientSource, "function diagnosticReferencePath", clientPath);
assertIncludes(clientSource, "function openDiagnosticDocsPreview", clientPath);
assertIncludes(clientSource, "function diagnosticAnchor", clientPath);
assertIncludes(clientSource, "validator-diagnostic-codes.md", clientPath);
assertIncludes(clientSource, "function markdownAnchor", clientPath);
assertIncludes(clientSource, "vscode_1.Uri.file(docsPath).with({ fragment })", clientPath);
assertIncludes(clientSource, "docs\", \"reference\", \"generated\", \"ai-symbol-reference.md", clientPath);
assertIncludes(clientSource, "SemanticTokensLegend", clientPath);
assertIncludes(clientSource, "registerDocumentSemanticTokensProvider", clientPath);
assertIncludes(clientSource, "function semanticTokensForDocument", clientPath);
assertIncludes(clientSource, "aoe2StrategicNumber", clientPath);
assertIncludes(grammarSource, "support.constant.strategic-number.aoe2aiscript", grammarPath);
assertIncludes(grammarSource, "constant.other.object.aoe2aiscript", grammarPath);
assertIncludes(grammarSource, "constant.other.value.aoe2aiscript", grammarPath);
assertIncludes(grammarSource, "variable.other.constant.aoe2aiscript", grammarPath);
assert(workspaceSettings["editor.semanticHighlighting.enabled"] === true, "workspace semantic highlighting must be enabled");
assert(workspaceSettings["editor.tokenColorCustomizations"], "workspace TextMate token colors must be configured");

for (const tokenType of [
  "aoe2Action",
  "aoe2Fact",
  "aoe2FactAction",
  "aoe2Command",
  "aoe2StrategicNumber",
  "aoe2Object",
  "aoe2Tech",
  "aoe2Value",
  "aoe2LocalConstant",
]) {
  assert(semanticTokenTypes.has(tokenType), `missing semantic token type ${tokenType}`);
}

for (const needle of [
  "function formatPackageIssueGroups",
  "stdout.indexOf(\"{\")",
  "payload.issue_groups || []",
  "documentation_markdown",
  '"lint-package", packageRoot, "--json", "--fail-level", "error"',
  'path.extname(filePath).toLowerCase() === ".ai"',
  'path.extname(filePath).toLowerCase() === ".per"',
  "return isPerFile ? filePath : undefined;",
  "exports._test",
]) {
  assertIncludes(clientSource, needle, clientPath);
}

for (const needle of [
  "cursor",
  "code",
  "--install-extension",
  "--editor",
  "--package-only",
  "--bump-patch",
  "bumpPatchVersion",
  "scripts/generate-diagnostic-registry.mjs",
  "scripts/verify-cursor-extension.mjs",
  "scripts/sync-extension-lab.mjs",
  "verifyInstalledExtension",
  "formatPackageIssueGroups",
  "Reload",
]) {
  assertIncludes(installScriptSource, needle, installScriptPath);
}

for (const needle of [
  "aoe2-aiscript-cursor-local-lab",
  "extensions",
  "lab",
  "docs",
  "extracted",
  "inventories",
  "reference",
  "generated",
  "src",
]) {
  assertIncludes(syncLabScriptSource, needle, syncLabScriptPath);
}

for (const needle of [
  "function runLabPackageLinter",
  '"lint-package", packageRoot, "--json", "--fail-level", "error"',
  'path.extname(filePath).toLowerCase() === ".ai"',
  'path.extname(filePath).toLowerCase() === ".per"',
  "return isPerFile ? filePath : null;",
  "function collectAiRootDiagnostics",
  "missing-load-target",
  "stale-ai-root",
  "skipped-load-random",
  "duplicate-root-target",
  "duplicate-ai-name",
  "function diagnosticRangeForLine(textDocument, lineNumber, code, message, span)",
  '"lint", filePath, "--json"',
  "finding.span",
  "function labSetupDiagnostic",
  "function bundledLabPath",
  "PYTHONPATH: path.join(labPath, \"src\")",
  "function addLabRegistryCompletions",
  "function contextualCompletionList",
  "function completionContextKind",
  "function currentCommandArgument",
  "function preferredKindsForParameter",
  "function completionItemFamily",
  "\"map-type\"",
  "function localDefconstCompletions",
  "function loadTargetCompletions",
  "function labRegistryHover",
  "hover = labRegistryHover(hover_txt);",
  "function labDiagnosticRegistryPath",
  "function labDiagnosticExplanations",
  "data\", \"diagnostic-codes.json",
  "definitionProvider: true",
  "declarationProvider: true",
  "function getDefinition",
  "connection.onDefinition",
  "textDocument/declaration",
  "function localDefconstDefinition",
  "function resolveLoadTarget",
  "function labRegistryDefinition",
  "function symbolReferencePath",
  "function symbolDocPath",
  "function markdownAnchor",
  "vscode_uri_1.URI.file(docsPath).with({ fragment: markdownAnchor(token) })",
  "docs\", \"reference\", \"generated\", \"symbols",
  "docs\", \"reference\", \"generated\", \"ai-symbol-reference.md",
  "function labRegistrySignatureHelp",
  "function labSignatureParameters",
  "let labSignature = labRegistrySignatureHelp(text, textDocPos.position, settings);",
  "codeActionProvider: true",
  "connection.onCodeAction",
  "function codeActionsForDiagnostic",
  "function explanationCodeAction",
  "labDiagnosticExplanations().get(code)",
  "title: \"Explain \" + code + \": \" + explanation",
  "aoe2AiScript.openDiagnosticDocsPreview",
  "function closestRegistryLabels",
  "function closestRegistryLabelsByFamilies",
  "function diagnosticReplacementFamilies",
  "function typeOpReplacementLabels",
  "function mathOpReplacementLabels",
]) {
  assertIncludes(serverSource, needle, serverPath);
}

assert(completions.itemCount > 2000, "registry completion data should contain more than 2000 items");
for (const label of ["up-find-local", "sn-maximum-town-size", "villager", "ri-loom"]) {
  assert(completionLabels.has(label), `registry completions missing ${label}`);
  assert(symbolDocsSource.includes(`## \`${label}\``), `symbol docs missing ${label}`);
  assert(symbolDocsSource.includes(`id="symbol-${label}"`), `symbol docs missing anchor for ${label}`);
  assert(fs.existsSync(path.join(symbolDocsDir, `${label}.md`)), `symbol page missing ${label}`);
}

const byLabel = new Map(completions.items.map((item) => [item.label, item]));
assertIncludes(byLabel.get("sn-maximum-town-size").documentation, "Default: `20`", completionsPath);
assertIncludes(byLabel.get("up-gaia-type-count").documentation, "This command does not work with relics.", completionsPath);
assert(!byLabel.get("up-gaia-type-count").documentation.includes("r..."), "up-gaia-type-count hover docs should not be generator-truncated");
assertIncludes(symbolDocsSource, "## Table Of Contents", symbolDocsPath);
assertIncludes(symbolDocsSource, "- [command](#section-command)", symbolDocsPath);
assertIncludes(symbolDocsSource, "- [strategic-number](#section-strategic-number)", symbolDocsPath);
assert(!symbolDocsSource.includes("[`up-gaia-type-count`](#symbol-up-gaia-type-count)"), "symbol reference TOC should stay section-level");
const diagnosticDocsPath = path.join(repoRoot, "docs", "workflows", "validator-diagnostic-codes.md");
assertIncludes(readText(diagnosticDocsPath), '<a id="diagnostic-command-argument-mismatch"></a>', diagnosticDocsPath);

const diagnosticCodeLabels = new Set((diagnosticCodes.codes || []).map((entry) => entry.code));
for (const code of ["unsafe-set-target-object", "command-typed-prefix-mismatch", "missing-load-target", "duplicate-ai-name"]) {
  assert(diagnosticCodeLabels.has(code), `diagnostic registry missing ${code}`);
}

for (const sample of [
  "lab_diagnostics_sample.ai",
  "lab_diagnostics_sample.per",
  "lab_bad_load_sample.ai",
  "lab_load_random_sample.ai",
  "lab_duplicate_one.ai",
  "lab_duplicate_two.ai",
  "lab_duplicate_shared.per",
  "semantic_coloring_sample.per",
]) {
  assert(fs.existsSync(path.join(extensionRoot, "samples", sample)), `missing sample ${sample}`);
}

for (const needle of [
  "textDocument/completion",
  "textDocument/signatureHelp",
  "textDocument/codeAction",
  "up-find-local object argument",
  "up-find-local signature help",
  "missing load target code action",
  "unsafe set target explanation action",
  "typed prefix explanation action",
  ".ai load target completion",
]) {
  assertIncludes(completionSmokeSource, needle, completionSmokePath);
}

for (const needle of [
  "formatPackageIssueGroups",
  "lint-package",
  "--json",
  "Package summary:",
  "Issue categories:",
  "[integrity] stale-ai-root (1)",
]) {
  assertIncludes(packageOutputSmokeSource, needle, packageOutputSmokePath);
}

console.log(`Editor extension verified: ${packageData.name} ${packageData.version}`);
