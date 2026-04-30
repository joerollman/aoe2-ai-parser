import fs from "node:fs";
import path from "node:path";

const repoRoot = process.cwd();
const completionsPath = path.join(
  repoRoot,
  "extensions",
  "aoe2-aiscript-cursor-local-lab",
  "data",
  "completions.json",
);
const outputDir = path.join(repoRoot, "docs", "reference", "generated");
const symbolDir = path.join(outputDir, "symbols");
const outputPath = path.join(outputDir, "ai-symbol-reference.md");
const readmePath = path.join(outputDir, "README.md");

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

function normalizeDocText(value) {
  return String(value || "")
    .replace(/\r\n/g, "\n")
    .trim();
}

function markdownAnchor(label) {
  return `symbol-${String(label).toLowerCase().replace(/[^#a-z0-9_-]+/g, "-")}`;
}

function renderEntry(item) {
  const lines = [];
  lines.push(`<a id="${markdownAnchor(item.label)}"></a>`);
  lines.push("");
  lines.push(`## \`${item.label}\``);
  lines.push("");
  if (item.kind || item.detail) {
    lines.push(`- Kind: \`${item.kind || "unknown"}\``);
    if (item.detail) {
      lines.push(`- Detail: ${item.detail}`);
    }
    lines.push("");
  }
  const documentation = normalizeDocText(item.documentation);
  if (documentation) {
    lines.push(documentation);
    lines.push("");
  }
  if (item.insertText && item.insertText !== item.label) {
    lines.push("Completion insert text:");
    lines.push("");
    lines.push("```text");
    lines.push(String(item.insertText));
    lines.push("```");
    lines.push("");
  }
  return lines.join("\n");
}

function symbolFileName(label) {
  return `${String(label).replace(/[^#A-Za-z0-9_-]+/g, "_")}.md`;
}

const payload = readJson(completionsPath);
const items = [...(payload.items || [])].sort((left, right) => {
  const kindCompare = String(left.kind || "").localeCompare(String(right.kind || ""));
  if (kindCompare !== 0) {
    return kindCompare;
  }
  return String(left.label || "").localeCompare(String(right.label || ""));
});
const groupedItems = new Map();
for (const item of items.filter((entry) => entry.label)) {
  const kind = item.kind || "unknown";
  if (!groupedItems.has(kind)) {
    groupedItems.set(kind, []);
  }
  groupedItems.get(kind).push(item);
}

fs.mkdirSync(outputDir, { recursive: true });
fs.rmSync(symbolDir, { recursive: true, force: true });
fs.mkdirSync(symbolDir, { recursive: true });

const toc = [
  "## Table Of Contents",
  "",
  ...Array.from(groupedItems.keys()).map((kind) => `- [${kind}](#section-${kind.toLowerCase().replace(/[^a-z0-9_-]+/g, "-")})`),
  "",
];

const output = [
  "# AI Symbol Reference",
  "",
  "Generated from `extensions/aoe2-aiscript-cursor-local-lab/data/completions.json`.",
  "Edit the source inventories or completion generator, then run `npm run generate:symbol-docs`.",
  "",
  "This file is the formatted local documentation target for Cursor definition navigation.",
  "",
  ...toc,
  ...Array.from(groupedItems.entries()).flatMap(([kind, entries]) => [
    `<a id="section-${kind.toLowerCase().replace(/[^a-z0-9_-]+/g, "-")}"></a>`,
    "",
    `# ${kind}`,
    "",
    ...entries.map(renderEntry),
  ]),
  "",
].join("\n");

const readme = [
  "# Generated Reference",
  "",
  "This folder contains formatted local documentation generated from the compact",
  "registry data used by Cursor completions, hovers, signatures, and definition",
  "navigation.",
  "",
  "- [ai-symbol-reference.md](./ai-symbol-reference.md): all known AI scripting",
  "  symbols from the local completion registry, with a generated table of",
  "  contents and stable per-symbol anchors.",
  "- [symbols/](./symbols/): compatibility per-symbol files generated from the",
  "  same entries. Prefer the combined reference for cross-navigation.",
  "",
  "Regenerate with:",
  "",
  "```powershell",
  "npm run generate:symbol-docs",
  "```",
  "",
].join("\n");

fs.writeFileSync(outputPath, output, "utf8");
fs.writeFileSync(readmePath, readme, "utf8");

for (const item of items.filter((entry) => entry.label)) {
  const filePath = path.join(symbolDir, symbolFileName(item.label));
  fs.writeFileSync(
    filePath,
    [
      `# \`${item.label}\``,
      "",
      "[All symbols](../ai-symbol-reference.md)",
      "",
      renderEntry(item).replace(/^## /, "## "),
      "",
    ].join("\n"),
    "utf8",
  );
}

console.log(`Wrote ${path.relative(repoRoot, outputPath)}`);
console.log(`Wrote ${path.relative(repoRoot, readmePath)}`);
console.log(`Wrote ${items.filter((entry) => entry.label).length} symbol files to ${path.relative(repoRoot, symbolDir)}`);
