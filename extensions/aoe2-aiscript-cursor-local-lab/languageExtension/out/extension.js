"use strict";
/* --------------------------------------------------------------------------------------------
 * Copyright (c) Microsoft Corporation. All rights reserved.
 * Licensed under the MIT License. See License.txt in the project root for license information.
 * ------------------------------------------------------------------------------------------ */
Object.defineProperty(exports, "__esModule", { value: true });
const child_process = require("child_process");
const fs = require("fs");
const path = require("path");
const vscode_1 = require("vscode");
const vscode_languageclient_1 = require("vscode-languageclient");
let client;
let outputChannel;
const semanticTokenTypes = ["aoe2Action", "aoe2Fact", "aoe2FactAction", "aoe2Command", "aoe2StrategicNumber", "aoe2Object", "aoe2Tech", "aoe2Value", "aoe2LocalConstant"];
let semanticTokenLegend;
function getOutputChannel() {
    if (!outputChannel) {
        outputChannel = vscode_1.window.createOutputChannel("AOE2 AI Parser");
    }
    return outputChannel;
}
function getWorkspacePath() {
    let folders = vscode_1.workspace.workspaceFolders;
    if (!folders || folders.length === 0) {
        return undefined;
    }
    return folders[0].uri.fsPath;
}
function extensionRootPath() {
    return path.resolve(__dirname, "..", "..");
}
function bundledLabPath() {
    let labPath = path.join(extensionRootPath(), "lab");
    return fs.existsSync(path.join(labPath, "src", "aoe2_ai_lab")) ? labPath : undefined;
}
function getLabSettings() {
    let workspacePath = getWorkspacePath();
    let config = vscode_1.workspace.getConfiguration("aoe2_AiScript");
    let configuredLabPath = config.get("labPath") || "";
    let labPath = configuredLabPath || bundledLabPath() || workspacePath;
    let pythonPath = config.get("pythonPath") || "python";
    let packageFailLevel = config.get("packageFailLevel") || "error";
    if (!["error", "warning", "info"].includes(packageFailLevel)) {
        packageFailLevel = "error";
    }
    return { labPath, pythonPath, workspacePath, configuredLabPath, packageFailLevel };
}
let labRegistryLabelSet;
let labRegistryKindMap;
function labRegistryPath() {
    return path.resolve(__dirname, "..", "..", "data", "completions.json");
}
function labRegistryLabels() {
    if (labRegistryLabelSet !== undefined) {
        return labRegistryLabelSet;
    }
    labRegistryLabelSet = new Set();
    let registryPath = labRegistryPath();
    if (!fs.existsSync(registryPath)) {
        return labRegistryLabelSet;
    }
    try {
        let payload = JSON.parse(fs.readFileSync(registryPath, "utf8"));
        (payload.items || []).forEach(item => {
            if (item.label) {
                labRegistryLabelSet.add(item.label);
            }
        });
    }
    catch (_error) {
        return labRegistryLabelSet;
    }
    return labRegistryLabelSet;
}
function labRegistryKinds() {
    if (labRegistryKindMap !== undefined) {
        return labRegistryKindMap;
    }
    labRegistryKindMap = new Map();
    let registryPath = labRegistryPath();
    if (!fs.existsSync(registryPath)) {
        return labRegistryKindMap;
    }
    try {
        let payload = JSON.parse(fs.readFileSync(registryPath, "utf8"));
        (payload.items || []).forEach(item => {
            if (item.label && item.kind) {
                labRegistryKindMap.set(item.label, { kind: item.kind, detail: item.detail || "" });
            }
        });
    }
    catch (_error) {
        return labRegistryKindMap;
    }
    return labRegistryKindMap;
}
function semanticTokenTypeForRegistryItem(item) {
    if (!item) {
        return "aoe2Value";
    }
    if (item.kind === "command") {
        if (/^Action\b/.test(item.detail)) {
            return "aoe2Action";
        }
        if (/^FactAction\b/.test(item.detail)) {
            return "aoe2FactAction";
        }
        if (/^Fact\b/.test(item.detail)) {
            return "aoe2Fact";
        }
        return "aoe2Command";
    }
    switch (item.kind) {
        case "command":
            return "aoe2Command";
        case "strategic-number":
            return "aoe2StrategicNumber";
        case "object":
            return "aoe2Object";
        case "tech":
            return "aoe2Tech";
        case "value":
            return "aoe2Value";
        default:
            return "aoe2Value";
    }
}
function semanticTokensForDocument(document) {
    if (!semanticTokenLegend || !vscode_1.SemanticTokensBuilder) {
        return undefined;
    }
    let builder = new vscode_1.SemanticTokensBuilder(semanticTokenLegend);
    let registry = labRegistryKinds();
    let text = document.getText();
    let tokenPattern = /[#A-Za-z_][#A-Za-z0-9_-]*/g;
    let localConstants = new Set();
    let defconstPattern = /\(\s*defconst\s+([A-Za-z_][A-Za-z0-9_-]*)\b/g;
    let defconstMatch;
    while ((defconstMatch = defconstPattern.exec(text)) !== null) {
        localConstants.add(defconstMatch[1]);
    }
    for (let line = 0; line < document.lineCount; line++) {
        let lineText = document.lineAt(line).text;
        let commentIndex = lineText.indexOf(";");
        let scanText = commentIndex >= 0 ? lineText.slice(0, commentIndex) : lineText;
        let match;
        while ((match = tokenPattern.exec(scanText)) !== null) {
            let token = match[0];
            let item = registry.get(token);
            if (item) {
                builder.push(line, match.index, token.length, semanticTokenTypeForRegistryItem(item), []);
                continue;
            }
            if (localConstants.has(token)) {
                let modifiers = /\(\s*defconst\s+$/.test(scanText.slice(0, match.index)) ? ["declaration"] : [];
                builder.push(line, match.index, token.length, "aoe2LocalConstant", modifiers);
            }
        }
    }
    return builder.build();
}
function normalizeFsPath(filePath) {
    return path.resolve(filePath).toLowerCase();
}
function findNearestPackageRoot(filePath, workspacePath) {
    if (path.extname(filePath).toLowerCase() === ".ai") {
        return filePath;
    }
    let isPerFile = path.extname(filePath).toLowerCase() === ".per";
    let current = fs.statSync(filePath).isDirectory() ? filePath : path.dirname(filePath);
    let workspaceRoot = path.resolve(workspacePath);
    while (true) {
        try {
            let entries = fs.readdirSync(current);
            if (entries.some(entry => entry.toLowerCase().endsWith(".ai"))) {
                return current;
            }
        }
        catch (_error) {
            return undefined;
        }
        let parent = path.dirname(current);
        if (current === parent) {
            return isPerFile ? filePath : undefined;
        }
        if (path.relative(workspaceRoot, parent).startsWith("..")) {
            return isPerFile ? filePath : undefined;
        }
        current = parent;
    }
}
function getActiveFilePath() {
    let editor = vscode_1.window.activeTextEditor;
    if (!editor || editor.document.uri.scheme !== "file") {
        let channel = getOutputChannel();
        channel.clear();
        channel.appendLine("AoE2 command did not run.");
        channel.appendLine("Open an AoE2 .per or .ai file first.");
        channel.show(false);
        vscode_1.window.showWarningMessage("Open an AoE2 .per or .ai file first.");
        return undefined;
    }
    return editor.document.uri.fsPath;
}
function formatCounts(counts) {
    if (!counts || Object.keys(counts).length === 0) {
        return "none";
    }
    return Object.keys(counts)
        .sort()
        .map(key => key + ": " + counts[key])
        .join(", ");
}
function relativeDisplayPath(filePath, labPath) {
    if (!filePath) {
        return "";
    }
    let resolved = path.resolve(filePath);
    let relative = path.relative(labPath, resolved);
    if (relative && !relative.startsWith("..") && !path.isAbsolute(relative)) {
        return relative;
    }
    return filePath;
}
function formatPackageLoadGraph(roots, labPath) {
    let lines = [];
    let graphEntries = [];
    (roots || []).forEach(root => {
        (root.load_graph || []).forEach(entry => {
            graphEntries.push(entry);
        });
    });
    if (graphEntries.length === 0) {
        return lines;
    }
    lines.push("");
    lines.push("Load graph:");
    graphEntries.slice(0, 12).forEach(entry => {
        let filePath = relativeDisplayPath(entry.path, labPath);
        let loads = entry.loads || [];
        let includes = entry.includes || [];
        lines.push("  " + filePath + " (" + loads.length + " loads, " + includes.length + " includes)");
        loads.slice(0, 4).forEach(load => {
            let suffix = load.skipped_reason ? ", " + load.skipped_reason : "";
            lines.push("    - " + load.source + " line " + load.line + ": " + load.include + " -> " + load.status + suffix);
        });
        includes.slice(0, 4).forEach(include => {
            lines.push("    - include line " + include.line + ": " + include.include + " -> " + include.status);
        });
        if (loads.length + includes.length > 8) {
            lines.push("    - ...");
        }
    });
    if (graphEntries.length > 12) {
        lines.push("  ...");
    }
    return lines;
}
function formatPackageIssueGroups(stdout, labPath) {
    let payload;
    let jsonText = stdout;
    let jsonStart = stdout.indexOf("{");
    if (jsonStart > 0) {
        jsonText = stdout.slice(jsonStart);
    }
    try {
        payload = JSON.parse(jsonText);
    }
    catch (_error) {
        return stdout || "No output.";
    }
    let totals = payload.totals || {};
    let issueGroups = payload.issue_groups || [];
    let lines = [];
    lines.push("Package summary:");
    lines.push("  roots: " + ((payload.roots || []).length || 0));
    lines.push("  reachable files: " + (totals.reachable_file_count || 0));
    lines.push("  lint findings: " + (totals.finding_count || 0));
    lines.push("  lint severity: " + formatCounts(totals.severity_counts || {}));
    lines.push("  integrity severity: " + formatCounts(totals.integrity_severity_counts || {}));
    lines.push("");
    if (issueGroups.length === 0) {
        lines.push("Issue categories: none");
        lines.push(...formatPackageLoadGraph(payload.roots || [], labPath));
        return lines.join("\n") + "\n";
    }
    lines.push("Issue categories:");
    issueGroups.forEach(group => {
        let severity = formatCounts(group.severity_counts || {});
        let confidence = formatCounts(group.confidence_counts || {});
        let unique = group.unique_occurrence_count && group.unique_occurrence_count !== group.count ? ", " + group.unique_occurrence_count + " unique" : "";
        lines.push("  [" + (group.source || "lint") + "] " + group.code + " (" + group.count + unique + ")");
        lines.push("    severity: " + severity);
        lines.push("    confidence: " + confidence);
        if (group.explanation) {
            lines.push("    " + group.explanation);
        }
        if (group.documentation_markdown) {
            lines.push("    docs: " + group.documentation_markdown);
        }
        (group.examples || []).slice(0, 5).forEach(example => {
            let location = relativeDisplayPath(example.path || example.ai_path || example.per_path, labPath);
            if (example.line) {
                location += ":" + example.line;
            }
            let message = example.message || example.include || "";
            lines.push("    - " + location + (message ? ": " + message : ""));
        });
    });
    lines.push(...formatPackageLoadGraph(payload.roots || [], labPath));
    return lines.join("\n") + "\n";
}
function runLabCommand(args, title, formatStdout) {
    let settings = getLabSettings();
    let channel = getOutputChannel();
    channel.clear();
    channel.appendLine(title);
    channel.appendLine("labPath: " + settings.labPath);
    channel.appendLine("command: " + settings.pythonPath + " " + args.join(" "));
    channel.appendLine("");
    channel.show(false);
    if (!settings.labPath || !fs.existsSync(settings.labPath)) {
        vscode_1.window.showErrorMessage("AOE2 AI Parser runtime path does not exist. Set aoe2_AiScript.labPath.");
        return { ok: false, stdout: "", stderr: "invalid labPath" };
    }
    let env = Object.assign({}, process.env, { PYTHONPATH: path.join(settings.labPath, "src") });
    try {
        let stdout = child_process.execFileSync(settings.pythonPath, args, {
            cwd: settings.labPath,
            env,
            encoding: "utf8",
            windowsHide: true
        });
        channel.append(formatStdout ? formatStdout(stdout || "") : (stdout || "No output."));
        return { ok: true, stdout: stdout || "", stderr: "" };
    }
    catch (error) {
        let stdout = error.stdout ? String(error.stdout) : "";
        let stderr = error.stderr ? String(error.stderr) : "";
        if (stdout) {
            channel.append(formatStdout ? formatStdout(stdout) : stdout);
        }
        if (!stdout && !stderr) {
            stderr = String(error.message || error);
        }
        if (stderr) {
            channel.appendLine("");
            channel.appendLine(stderr);
        }
        return { ok: false, stdout, stderr };
    }
}
function getCurrentPackageRoot() {
    let filePath = getActiveFilePath();
    if (!filePath) {
        return undefined;
    }
    let settings = getLabSettings();
    if (!settings.workspacePath) {
        let channel = getOutputChannel();
        channel.clear();
        channel.appendLine("AoE2 package command did not run.");
        channel.appendLine("Open a workspace folder before linting a package.");
        channel.show(false);
        vscode_1.window.showWarningMessage("Open a workspace folder before linting a package.");
        return undefined;
    }
    let packageRoot = findNearestPackageRoot(filePath, settings.workspacePath);
    if (!packageRoot) {
        let channel = getOutputChannel();
        channel.clear();
        channel.appendLine("AoE2 package command did not run.");
        channel.appendLine("No .ai package root found at or above the current file.");
        channel.appendLine("Open a .ai file, or open a .per file inside a folder that contains an .ai root.");
        channel.show(false);
        vscode_1.window.showWarningMessage("No .ai package root found at or above the current file.");
        return undefined;
    }
    return packageRoot;
}
function lintCurrentFile() {
    let filePath = getActiveFilePath();
    if (!filePath) {
        return;
    }
    let result = runLabCommand(["-m", "aoe2_ai_lab", "lint", filePath], "AoE2: Lint Current File");
    if (result.ok) {
        vscode_1.window.showInformationMessage("AoE2 lint current file: no findings.");
    }
    else if (result.stdout) {
        vscode_1.window.showWarningMessage("AoE2 lint current file: findings found.");
    }
    else {
        vscode_1.window.showErrorMessage("AoE2 lint current file failed. See AOE2 AI Parser output.");
    }
}
function lintPackage() {
    let packageRoot = getCurrentPackageRoot();
    if (!packageRoot) {
        return;
    }
    let settings = getLabSettings();
    let result = runLabCommand(["-m", "aoe2_ai_lab", "lint-package", packageRoot, "--json", "--fail-level", settings.packageFailLevel], "AoE2: Lint Package", stdout => formatPackageIssueGroups(stdout, settings.labPath));
    if (result.ok) {
        vscode_1.window.showInformationMessage("AoE2 lint package completed. See AOE2 AI Parser output.");
    }
    else if (result.stdout) {
        vscode_1.window.showWarningMessage("AoE2 lint package completed with findings.");
    }
    else {
        vscode_1.window.showErrorMessage("AoE2 lint package failed. See AOE2 AI Parser output.");
    }
}
function lintFolder() {
    let filePath = getActiveFilePath();
    if (!filePath) {
        return;
    }
    let folderPath = fs.statSync(filePath).isDirectory() ? filePath : path.dirname(filePath);
    let settings = getLabSettings();
    let result = runLabCommand(["-m", "aoe2_ai_lab", "lint-package", folderPath, "--json", "--fail-level", settings.packageFailLevel], "AoE2: Lint Folder", stdout => formatPackageIssueGroups(stdout, settings.labPath));
    if (result.ok) {
        vscode_1.window.showInformationMessage("AoE2 lint folder completed. See AOE2 AI Parser output.");
    }
    else if (result.stdout) {
        vscode_1.window.showWarningMessage("AoE2 lint folder completed with findings.");
    }
    else {
        vscode_1.window.showErrorMessage("AoE2 lint folder failed. See AOE2 AI Parser output.");
    }
}
function timestampForReport() {
    return new Date().toISOString().replace(/[:.]/g, "-");
}
function generatePackageReport() {
    let packageRoot = getCurrentPackageRoot();
    if (!packageRoot) {
        return;
    }
    let settings = getLabSettings();
    let reportRoot = settings.configuredLabPath ? settings.labPath : (settings.workspacePath || settings.labPath);
    let reportDir = path.join(reportRoot, ".tmp", "lint-package");
    fs.mkdirSync(reportDir, { recursive: true });
    let reportName = path.basename(packageRoot) + "-" + timestampForReport() + ".md";
    let reportPath = path.join(reportDir, reportName);
    let result = runLabCommand(["-m", "aoe2_ai_lab", "lint-package", packageRoot, "--report", reportPath, "--fail-level", settings.packageFailLevel], "AoE2: Generate Package Report");
    if (fs.existsSync(reportPath)) {
        vscode_1.workspace.openTextDocument(reportPath).then(document => vscode_1.window.showTextDocument(document));
        if (result.ok) {
            vscode_1.window.showInformationMessage("AoE2 package report generated.");
        }
        else {
            vscode_1.window.showWarningMessage("AoE2 package report generated with findings.");
        }
    }
    else if (!result.ok) {
        vscode_1.window.showErrorMessage("AoE2 package report failed. See AOE2 AI Parser output.");
    }
}
function openLatestPackageReport() {
    let settings = getLabSettings();
    let reportRoot = settings.configuredLabPath ? settings.labPath : (settings.workspacePath || settings.labPath);
    let reportDir = path.join(reportRoot, ".tmp", "lint-package");
    if (!fs.existsSync(reportDir)) {
        vscode_1.window.showWarningMessage("No AoE2 package reports found.");
        return;
    }
    let reports = fs.readdirSync(reportDir)
        .filter(name => name.toLowerCase().endsWith(".md"))
        .map(name => path.join(reportDir, name))
        .sort((a, b) => fs.statSync(b).mtimeMs - fs.statSync(a).mtimeMs);
    if (reports.length === 0) {
        vscode_1.window.showWarningMessage("No AoE2 package reports found.");
        return;
    }
    vscode_1.workspace.openTextDocument(reports[0]).then(document => vscode_1.window.showTextDocument(document));
}
function symbolReferencePath() {
    let settings = getLabSettings();
    return path.join(settings.labPath, "docs", "reference", "generated", "ai-symbol-reference.md");
}
function diagnosticReferencePath() {
    let settings = getLabSettings();
    return path.join(settings.labPath, "docs", "workflows", "validator-diagnostic-codes.md");
}
function symbolDocPath(symbol) {
    let settings = getLabSettings();
    return path.join(settings.labPath, "docs", "reference", "generated", "symbols", symbol.replace(/[^#A-Za-z0-9_-]+/g, "_") + ".md");
}
function markdownAnchor(symbol) {
    return "symbol-" + symbol.toLowerCase().replace(/[^#a-z0-9_-]+/g, "-");
}
function diagnosticAnchor(code) {
    return "diagnostic-" + String(code || "").toLowerCase().replace(/[^a-z0-9_-]+/g, "-");
}
function currentToken() {
    let editor = vscode_1.window.activeTextEditor;
    if (!editor) {
        return undefined;
    }
    let range = editor.document.getWordRangeAtPosition(editor.selection.active, /[#A-Za-z_][#A-Za-z0-9_-]*/);
    if (!range) {
        return undefined;
    }
    return editor.document.getText(range);
}
function commandUriForSymbolDocs(symbol) {
    return vscode_1.Uri.parse("command:aoe2AiScript.openSymbolDocsPreview?" + encodeURIComponent(JSON.stringify([symbol])));
}
function symbolDocsHover(document, position) {
    let range = document.getWordRangeAtPosition(position, /[#A-Za-z_][#A-Za-z0-9_-]*/);
    if (!range) {
        return undefined;
    }
    let symbol = document.getText(range);
    if (!labRegistryLabels().has(symbol)) {
        return undefined;
    }
    let markdown = new vscode_1.MarkdownString("[Open in Markdown Preview](" + commandUriForSymbolDocs(symbol).toString() + ")");
    markdown.isTrusted = true;
    return new vscode_1.Hover(markdown, range);
}
function openSymbolDocsPreview(token) {
    let symbol = token || currentToken();
    if (!symbol) {
        vscode_1.window.showWarningMessage("Place the cursor on an AoE2 AI symbol first.");
        return;
    }
    let referencePath = symbolReferencePath();
    let docsPath = referencePath;
    let fragment = markdownAnchor(symbol);
    if (!fs.existsSync(referencePath)) {
        docsPath = symbolDocPath(symbol);
        fragment = "";
        if (!fs.existsSync(docsPath)) {
            vscode_1.window.showWarningMessage("Generated symbol docs were not found. Run npm run generate:symbol-docs.");
            return;
        }
    }
    else {
        let text = fs.readFileSync(referencePath, "utf8");
        if (!new RegExp("^## `" + symbol.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + "`", "m").test(text)) {
            docsPath = symbolDocPath(symbol);
            fragment = "";
            if (!fs.existsSync(docsPath)) {
                vscode_1.window.showWarningMessage("No local docs entry found for " + symbol + ".");
                return;
            }
        }
    }
    let uri = fragment ? vscode_1.Uri.file(docsPath).with({ fragment }) : vscode_1.Uri.file(docsPath);
    vscode_1.commands.executeCommand("vscode.openWith", uri, "vscode.markdown.preview.editor", vscode_1.ViewColumn.Beside).then(undefined, () => {
        vscode_1.commands.executeCommand("markdown.showPreviewToSide", uri);
    });
}
function openDiagnosticDocsPreview(code) {
    let diagnosticCode = code ? String(code) : "";
    let docsPath = diagnosticReferencePath();
    if (!fs.existsSync(docsPath)) {
        vscode_1.window.showWarningMessage("Diagnostic docs were not found. Run npm run generate:diagnostic-registry.");
        return;
    }
    let fragment = diagnosticCode ? diagnosticAnchor(diagnosticCode) : "";
    let uri = fragment ? vscode_1.Uri.file(docsPath).with({ fragment }) : vscode_1.Uri.file(docsPath);
    vscode_1.commands.executeCommand("vscode.openWith", uri, "vscode.markdown.preview.editor", vscode_1.ViewColumn.Beside).then(undefined, () => {
        vscode_1.commands.executeCommand("markdown.showPreviewToSide", uri);
    });
}
function activate(context) {
    // The server is implemented in node
    let serverModule = context.asAbsolutePath(path.join('languageExtension', 'out', 'server.js'));
    // The debug options for the server
    // --inspect=6009: runs the server in Node's Inspector mode so VS Code can attach to the server for debugging
    let debugOptions = { execArgv: ['--nolazy', '--inspect=6009'] };
    // If the extension is launched in debug mode then the debug server options are used
    // Otherwise the run options are used
    let serverOptions = {
        run: { module: serverModule, transport: vscode_languageclient_1.TransportKind.ipc },
        debug: {
            module: serverModule,
            transport: vscode_languageclient_1.TransportKind.ipc,
            options: debugOptions
        }
    };
    // Options to control the language client
    let clientOptions = {
        // Register the server for plain text documents
        documentSelector: [{ scheme: 'file', language: 'aoe2aiscript' }],
        synchronize: {
            // Notify the server about file changes to '.clientrc files contained in the workspace
            fileEvents: vscode_1.workspace.createFileSystemWatcher('**/.clientrc')
        }
    };
    // Create the language client and start the client.
    client = new vscode_languageclient_1.LanguageClient('aoe2AiScript', 'Aoe2 AiScript Client', serverOptions, clientOptions);
    // Start the client. This will also launch the server
    client.start();
    let langConf = {
        "wordPattern": /(#{0,1}([a-zA-Z0-9]+-){0,}[a-zA-Z0-9]+)/g
    };
    vscode_1.languages.setLanguageConfiguration('aoe2aiscript', langConf);
    if (vscode_1.languages.registerDocumentSemanticTokensProvider && vscode_1.SemanticTokensBuilder && vscode_1.SemanticTokensLegend) {
        semanticTokenLegend = new vscode_1.SemanticTokensLegend(semanticTokenTypes, ["declaration"]);
        context.subscriptions.push(vscode_1.languages.registerDocumentSemanticTokensProvider({ language: 'aoe2aiscript', scheme: 'file' }, {
            provideDocumentSemanticTokens: semanticTokensForDocument
        }, semanticTokenLegend));
    }
    context.subscriptions.push(vscode_1.languages.registerHoverProvider('aoe2aiscript', {
        provideHover: symbolDocsHover
    }));
    context.subscriptions.push(vscode_1.commands.registerCommand("aoe2AiScript.lintCurrentFile", lintCurrentFile));
    context.subscriptions.push(vscode_1.commands.registerCommand("aoe2AiScript.lintPackage", lintPackage));
    context.subscriptions.push(vscode_1.commands.registerCommand("aoe2AiScript.lintFolder", lintFolder));
    context.subscriptions.push(vscode_1.commands.registerCommand("aoe2AiScript.generatePackageReport", generatePackageReport));
    context.subscriptions.push(vscode_1.commands.registerCommand("aoe2AiScript.openLatestPackageReport", openLatestPackageReport));
    context.subscriptions.push(vscode_1.commands.registerCommand("aoe2AiScript.openSymbolDocsPreview", openSymbolDocsPreview));
    context.subscriptions.push(vscode_1.commands.registerCommand("aoe2AiScript.openDiagnosticDocsPreview", openDiagnosticDocsPreview));
}
exports.activate = activate;
function deactivate() {
    if (!client) {
        return undefined;
    }
    return client.stop();
}
exports.deactivate = deactivate;
exports._test = {
    formatPackageIssueGroups
};
//# sourceMappingURL=extension.js.map
