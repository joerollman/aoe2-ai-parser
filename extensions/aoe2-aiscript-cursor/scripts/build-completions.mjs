import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const extensionRoot = path.resolve(__dirname, "..");
const repoRoot = path.resolve(extensionRoot, "..", "..");
const inventoriesRoot = path.join(repoRoot, "docs", "extracted", "inventories");
const outputPath = path.join(extensionRoot, "data", "completions.json");

function readJson(relativePath) {
  return JSON.parse(fs.readFileSync(path.join(inventoriesRoot, relativePath), "utf8"));
}

function oneLine(value, maxLength = 240) {
  const text = String(value || "").replace(/\s+/g, " ").trim();
  if (maxLength <= 0) {
    return text;
  }
  if (text.length <= maxLength) {
    return text;
  }
  return `${text.slice(0, maxLength - 1)}...`;
}

function commandSnippet(command) {
  const syntax = command.syntax || `(${command.name})`;
  let tabIndex = 1;
  const body = syntax.replace(/<[^>]+>/g, (match) => {
    const label = match.slice(1, -1).replace(/[{}$\\]/g, "");
    return `\${${tabIndex++}:${label}}`;
  });
  return body;
}

function addItem(items, seen, item) {
  if (!item.label || seen.has(`${item.kind}:${item.label}`)) {
    return;
  }
  seen.add(`${item.kind}:${item.label}`);
  items.push(item);
}

function buildCommandItems(items, seen) {
  const data = readJson("airef-command-inventory.json");
  for (const command of data.commands || []) {
    const commandType = command.info_table?.["Command Type"] || command.command_type || "Command";
    addItem(items, seen, {
      label: command.name,
      kind: "command",
      detail: `${commandType} - ${command.info_table?.Category || "AI command"}`,
      documentation: [
        command.syntax ? `Syntax: \`${command.syntax}\`` : "",
        oneLine(command.description, 0),
        command.url ? `[AIRef](${command.url})` : ""
      ].filter(Boolean).join("\n\n"),
      insertText: commandSnippet(command),
      sortText: `0-${command.name}`
    });
  }
}

function buildStrategicNumberItems(items, seen) {
  const data = readJson("airef-strategic-number-inventory.json");
  for (const sn of data.strategic_numbers || []) {
    const hasDefault = sn.default_value !== undefined && sn.default_value !== null && sn.default_value !== "";
    addItem(items, seen, {
      label: sn.name,
      kind: "strategic-number",
      detail: `SN ${sn.sn_id || ""} - ${sn.category || "Strategic number"}`.trim(),
      documentation: [
        oneLine(sn.description || sn.short_description, 0),
        hasDefault ? `Default: \`${sn.default_value}\`` : "",
        sn.required_range ? `Required range: \`${sn.required_range}\`` : "",
        sn.allowable_range ? `Range: \`${sn.allowable_range}\`` : "",
        sn.url ? `[AIRef](${sn.url})` : ""
      ].filter(Boolean).join("\n\n"),
      sortText: `1-${sn.name}`
    });
  }
}

function buildObjectItems(items, seen) {
  const data = readJson("airef-object-inventory.json");
  for (const object of data.objects || []) {
    addItem(items, seen, {
      label: object.ai_name,
      kind: "object",
      detail: `Object ${object.object_id} - ${object.name}`,
      documentation: [
        object.object_class ? `Class: \`${object.object_class}\`` : "",
        object.line ? `Line: \`${object.line}\`` : "",
        object.building ? `Building: ${object.building}` : ""
      ].filter(Boolean).join("\n\n"),
      sortText: `2-${object.ai_name}`
    });
    if (object.line) {
      addItem(items, seen, {
        label: object.line,
        kind: "object",
        detail: `Object line - ${object.name}`,
        documentation: `Line token from ${object.name}.`,
        sortText: `2-${object.line}`
      });
    }
  }
}

function buildTechItems(items, seen) {
  const data = readJson("airef-tech-inventory.json");
  for (const tech of data.techs || []) {
    for (const token of String(tech.ai_name || "").split(",").map((part) => part.trim()).filter(Boolean)) {
      const label = token.replace(/\s+\(DE only\)$/i, "");
      addItem(items, seen, {
        label,
        kind: "tech",
        detail: `Tech ${tech.tech_id} - ${tech.name}`,
        documentation: [
          tech.building ? `Building: ${tech.building}` : "",
          tech.civilization ? `Civilization: ${tech.civilization}` : ""
        ].filter(Boolean).join("\n\n"),
        sortText: `3-${label}`
      });
    }
  }
}

function buildValueItems(items, seen) {
  const data = readJson("airef-value-family-inventory.json");
  for (const family of data.families || []) {
    for (const entry of family.entries || []) {
      addItem(items, seen, {
        label: entry.name,
        kind: "value",
        detail: `${family.parameter_name} value`,
        documentation: [
          oneLine(entry.description),
          entry.de_id ? `DE id: \`${entry.de_id}\`` : entry.id ? `Id: \`${entry.id}\`` : ""
        ].filter(Boolean).join("\n\n"),
        sortText: `4-${entry.name}`
      });
    }
  }
}

const items = [];
const seen = new Set();
buildCommandItems(items, seen);
buildStrategicNumberItems(items, seen);
buildObjectItems(items, seen);
buildTechItems(items, seen);
buildValueItems(items, seen);

items.sort((a, b) => a.sortText.localeCompare(b.sortText));
fs.mkdirSync(path.dirname(outputPath), { recursive: true });
fs.writeFileSync(
  outputPath,
  `${JSON.stringify({ generatedFrom: "docs/extracted/inventories", itemCount: items.length, items }, null, 2)}\n`,
  "utf8"
);
console.log(`${items.length} completion items -> ${path.relative(repoRoot, outputPath)}`);
