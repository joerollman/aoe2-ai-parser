import fs from "node:fs";
import path from "node:path";

const repoRoot = process.cwd();
const jsonPath = path.join(repoRoot, "docs", "workflows", "validator-diagnostic-codes.json");
const markdownPath = path.join(repoRoot, "docs", "workflows", "validator-diagnostic-codes.md");
const extensionJsonPath = path.join(
  repoRoot,
  "extensions",
  "aoe2-aiscript-cursor-local-lab",
  "data",
  "diagnostic-codes.json"
);
const checkOnly = process.argv.includes("--check");

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

function tableEscape(value) {
  return String(value).replace(/\|/g, "\\|");
}

function renderReference(reference) {
  if (typeof reference === "string") {
    return reference;
  }
  if (!reference || typeof reference !== "object") {
    return "";
  }
  const label = reference.label || reference.path || reference.url || "";
  if (reference.url) {
    return `[${label}](${reference.url})`;
  }
  if (reference.path) {
    const anchor = reference.anchor ? `#${reference.anchor}` : "";
    return `[${label}](${reference.path}${anchor})`;
  }
  return label;
}

function renderMarkdown(registry) {
  const lines = [];
  lines.push(`# ${registry.title}`);
  lines.push("");
  for (const paragraph of registry.intro) {
    lines.push(paragraph);
  }
  lines.push("");
  lines.push("## Profile Suppression");
  lines.push("");
  lines.push("The `corpus` profile suppresses these compatibility/style codes:");
  lines.push("");
  for (const code of registry.corpus_suppressed) {
    lines.push(`- \`${code}\``);
  }
  lines.push("");
  lines.push(registry.profile_suppression_note);
  lines.push("");
  lines.push("## Codes");
  lines.push("");
  lines.push("| Code | Source | Severity | Corpus | Cursor action | Meaning |");
  lines.push("| --- | --- | --- | --- | --- | --- |");
  for (const entry of registry.codes) {
    lines.push(
      `| \`${entry.code}\` | ${tableEscape(entry.source)} | ${tableEscape(entry.severity)} | ${tableEscape(entry.corpus)} | ${tableEscape(entry.cursor_action)} | ${tableEscape(entry.meaning)} |`
    );
  }
  lines.push("");
  lines.push("## Code Details");
  for (const entry of registry.codes) {
    lines.push("");
    lines.push(`<a id="diagnostic-${entry.code}"></a>`);
    lines.push("");
    lines.push(`### \`${entry.code}\``);
    lines.push("");
    lines.push(`- Source: ${entry.source}`);
    lines.push(`- Default severity: ${entry.severity}`);
    lines.push(`- Corpus profile: ${entry.corpus}`);
    lines.push(`- Cursor action: ${entry.cursor_action}`);
    lines.push(`- Meaning: ${entry.meaning}`);
    if (Array.isArray(entry.references) && entry.references.length > 0) {
      lines.push("- References:");
      for (const reference of entry.references) {
        const rendered = renderReference(reference);
        if (rendered) {
          lines.push(`  - ${rendered}`);
        }
      }
    }
  }
  lines.push("");
  lines.push("## Triage Notes");
  lines.push("");
  for (const note of registry.triage_notes) {
    lines.push(`- ${note}`);
  }
  return `${lines.join("\n")}\n`;
}

function stableJson(registry) {
  return `${JSON.stringify(registry, null, 2)}\n`;
}

const registry = readJson(jsonPath);
const rendered = renderMarkdown(registry);
const renderedJson = stableJson(registry);

if (checkOnly) {
  const existing = fs.readFileSync(markdownPath, "utf8");
  if (existing !== rendered) {
    throw new Error(`${path.relative(repoRoot, markdownPath)} is stale; run node scripts/generate-diagnostic-registry.mjs`);
  }
  const existingExtensionJson = fs.readFileSync(extensionJsonPath, "utf8");
  if (existingExtensionJson !== renderedJson) {
    throw new Error(`${path.relative(repoRoot, extensionJsonPath)} is stale; run node scripts/generate-diagnostic-registry.mjs`);
  }
  console.log("Diagnostic registry Markdown and extension copy are up to date.");
} else {
  fs.writeFileSync(markdownPath, rendered, "utf8");
  fs.writeFileSync(extensionJsonPath, renderedJson, "utf8");
  console.log(`Wrote ${path.relative(repoRoot, markdownPath)}`);
  console.log(`Wrote ${path.relative(repoRoot, extensionJsonPath)}`);
}
