const fs = require("fs");
const path = require("path");
const vscode = require("vscode");

function loadCompletionData(context) {
  const dataPath = path.join(context.extensionPath, "data", "completions.json");
  return JSON.parse(fs.readFileSync(dataPath, "utf8"));
}

function completionKind(kind) {
  switch (kind) {
    case "command":
      return vscode.CompletionItemKind.Function;
    case "strategic-number":
      return vscode.CompletionItemKind.Constant;
    case "object":
      return vscode.CompletionItemKind.Value;
    case "tech":
      return vscode.CompletionItemKind.Value;
    case "value":
      return vscode.CompletionItemKind.EnumMember;
    default:
      return vscode.CompletionItemKind.Text;
  }
}

function createCompletionItem(entry) {
  const item = new vscode.CompletionItem(entry.label, completionKind(entry.kind));
  item.detail = entry.detail || entry.kind;
  item.documentation = new vscode.MarkdownString(entry.documentation || "");
  if (entry.insertText) {
    item.insertText = new vscode.SnippetString(entry.insertText);
  }
  if (entry.sortText) {
    item.sortText = entry.sortText;
  }
  return item;
}

function activate(context) {
  const data = loadCompletionData(context);
  const provider = vscode.languages.registerCompletionItemProvider(
    { language: "aoe2-per", scheme: "file" },
    {
      provideCompletionItems() {
        return data.items.map(createCompletionItem);
      }
    },
    "(",
    " ",
    ":",
    "-"
  );
  context.subscriptions.push(provider);
}

function deactivate() {}

module.exports = { activate, deactivate };
