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
let semanticDecorationTypes = new Map();
let semanticDecorationTimers = new Map();
const semanticColorSettings = {
    aoe2Action: "semanticColors.action",
    aoe2Fact: "semanticColors.fact",
    aoe2FactAction: "semanticColors.factAction",
    aoe2Command: "semanticColors.command",
    aoe2StrategicNumber: "semanticColors.strategicNumber",
    aoe2Object: "semanticColors.object",
    aoe2Tech: "semanticColors.tech",
    aoe2Value: "semanticColors.value",
    aoe2LocalConstant: "semanticColors.localConstant"
};
function getOutputChannel() {
    if (!outputChannel) {
        outputChannel = vscode_1.window.createOutputChannel("AOE2 AI Parser");
    }
    return outputChannel;
}
function execFileText(command, args, options) {
    return new Promise((resolve, reject) => {
        child_process.execFile(command, args, options, (error, stdout, stderr) => {
            if (error) {
                error.stdout = stdout;
                error.stderr = stderr;
                reject(error);
                return;
            }
            resolve(stdout || "");
        });
    });
}
function execFileTextStreaming(command, args, options, onStderr) {
    return new Promise((resolve, reject) => {
        const child = child_process.spawn(command, args, options);
        let stdout = "";
        let stderr = "";
        child.stdout.on("data", chunk => stdout += chunk.toString());
        child.stderr.on("data", chunk => {
            let text = chunk.toString();
            stderr += text;
            if (onStderr) {
                onStderr(text);
            }
        });
        child.on("error", reject);
        child.on("close", code => {
            if (code) {
                let error = new Error("Command failed with exit code " + code);
                error.stdout = stdout;
                error.stderr = stderr;
                reject(error);
                return;
            }
            resolve(stdout || "");
        });
    });
}
function execFileTextInput(command, args, input, options) {
    return new Promise((resolve, reject) => {
        const child = child_process.spawn(command, args, options);
        let stdout = "";
        let stderr = "";
        child.stdout.on("data", chunk => stdout += chunk.toString());
        child.stderr.on("data", chunk => stderr += chunk.toString());
        child.on("error", reject);
        child.on("close", code => {
            if (code) {
                let error = new Error("Command failed with exit code " + code);
                error.stdout = stdout;
                error.stderr = stderr;
                reject(error);
                return;
            }
            resolve(stdout || "");
        });
        child.stdin.end(input);
    });
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
    let packageFailLevel = config.get("packageFailLevel") || "info";
    if (!["error", "warning", "info"].includes(packageFailLevel)) {
        packageFailLevel = "info";
    }
    return { labPath, pythonPath, workspacePath, configuredLabPath, packageFailLevel };
}
function getFormatSettings() {
    let config = vscode_1.workspace.getConfiguration("aoe2_AiScript");
    let maxLineLength = config.get("formatMaxLineLength") || 255;
    if (maxLineLength < 40) {
        maxLineLength = 40;
    }
    if (maxLineLength > 255) {
        maxLineLength = 255;
    }
    return {
        formatOnSave: !!config.get("formatOnSave"),
        maxLineLength,
        formatChat: !!config.get("formatChat")
    };
}
function semanticColorsEnabled() {
    let config = vscode_1.workspace.getConfiguration("aoe2_AiScript");
    return !!config.get("enableSemanticColors");
}
function semanticColorOverrides() {
    let config = vscode_1.workspace.getConfiguration("aoe2_AiScript");
    let colors = new Map();
    semanticTokenTypes.forEach(tokenType => {
        let color = config.get(semanticColorSettings[tokenType]) || "";
        if (typeof color === "string" && color.trim()) {
            colors.set(tokenType, color.trim());
        }
    });
    return colors;
}
function disposeSemanticDecorations() {
    semanticDecorationTimers.forEach(timer => clearTimeout(timer));
    semanticDecorationTimers = new Map();
    semanticDecorationTypes.forEach(decoration => decoration.dispose());
    semanticDecorationTypes = new Map();
}
function refreshSemanticDecorationTypes() {
    disposeSemanticDecorations();
    if (!semanticColorsEnabled()) {
        return;
    }
    semanticColorOverrides().forEach((color, tokenType) => {
        semanticDecorationTypes.set(tokenType, vscode_1.window.createTextEditorDecorationType({ color }));
    });
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
function semanticDecorationRanges(document) {
    let ranges = new Map();
    semanticTokenTypes.forEach(tokenType => ranges.set(tokenType, []));
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
            let tokenType;
            let item = registry.get(token);
            if (item) {
                tokenType = semanticTokenTypeForRegistryItem(item);
            }
            else if (localConstants.has(token)) {
                tokenType = "aoe2LocalConstant";
            }
            if (tokenType && ranges.has(tokenType)) {
                ranges.get(tokenType).push(new vscode_1.Range(line, match.index, line, match.index + token.length));
            }
        }
    }
    return ranges;
}
function updateSemanticDecorationsForEditor(editor) {
    if (!editor || editor.document.languageId !== "aoe2aiscript" || !semanticColorsEnabled()) {
        return;
    }
    let ranges = semanticDecorationRanges(editor.document);
    semanticDecorationTypes.forEach((decoration, tokenType) => {
        editor.setDecorations(decoration, ranges.get(tokenType) || []);
    });
}
function clearSemanticDecorationsForEditor(editor) {
    if (!editor) {
        return;
    }
    semanticDecorationTypes.forEach(decoration => editor.setDecorations(decoration, []));
}
function updateSemanticDecorationsForVisibleEditors() {
    vscode_1.window.visibleTextEditors.forEach(updateSemanticDecorationsForEditor);
}
function scheduleSemanticDecorationUpdate(document) {
    let key = document.uri.toString();
    let existing = semanticDecorationTimers.get(key);
    if (existing) {
        clearTimeout(existing);
    }
    semanticDecorationTimers.set(key, setTimeout(() => {
        semanticDecorationTimers.delete(key);
        vscode_1.window.visibleTextEditors
            .filter(editor => editor.document.uri.toString() === key)
            .forEach(updateSemanticDecorationsForEditor);
    }, 250));
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
function relativePackagePath(filePath, packagePath) {
    if (!filePath) {
        return "";
    }
    if (!packagePath) {
        return filePath;
    }
    let basePath = packagePath;
    try {
        if (fs.existsSync(basePath) && fs.statSync(basePath).isFile()) {
            basePath = path.dirname(basePath);
        }
    }
    catch (_error) {
        basePath = path.dirname(basePath);
    }
    let relative = path.relative(basePath, filePath);
    if (relative && !relative.startsWith("..") && !path.isAbsolute(relative)) {
        return relative || path.basename(filePath);
    }
    return filePath;
}
function formatSeveritySummary(summary) {
    if (!summary) {
        return "";
    }
    let pieces = [];
    if (summary.confidence) {
        pieces.push(summary.confidence);
    }
    let findingCount = summary.finding_count || 0;
    pieces.push(findingCount + " findings");
    let severity = formatCounts(summary.severity_counts || {});
    if (severity !== "none") {
        pieces.push(severity);
    }
    return " [" + pieces.join("; ") + "]";
}
function formatPackageLintTrace(payload) {
    let lines = [];
    let packagePath = payload.path || "";
    let roots = payload.roots || [];
    lines.push("Lint trace:");
    lines.push("  input: " + packagePath);
    lines.push("  profile: " + (payload.profile || "unknown"));
    lines.push("  fail level: " + (payload.fail_level || "unknown") + ", confidence: " + (payload.fail_confidence || "unknown"));
    lines.push("  roots:");
    if (roots.length === 0) {
        lines.push("    (none)");
    }
    roots.forEach((root, rootIndex) => {
        let rootPrefix = rootIndex === roots.length - 1 ? "    `-- " : "    |-- ";
        let rootChildPrefix = rootIndex === roots.length - 1 ? "        " : "    |   ";
        let fileSummaries = new Map();
        (root.file_summaries || []).forEach(summary => fileSummaries.set(path.resolve(summary.path), summary));
        lines.push(rootPrefix + "AI: " + relativePackagePath(root.ai_path, packagePath));
        lines.push(rootChildPrefix + "|-- root .per: " + relativePackagePath(root.per_path, packagePath));
        lines.push(rootChildPrefix + "|-- reachable .per files (" + ((root.files || []).length) + ")");
        (root.files || []).forEach((filePath, fileIndex, files) => {
            let filePrefix = fileIndex === files.length - 1 ? "`-- " : "|-- ";
            let summary = fileSummaries.get(path.resolve(filePath));
            lines.push(rootChildPrefix + "|   " + filePrefix + relativePackagePath(filePath, packagePath) + formatSeveritySummary(summary));
        });
        let xsFiles = root.xs_files || [];
        lines.push(rootChildPrefix + "|-- included .xs files (" + xsFiles.length + ")");
        if (xsFiles.length === 0) {
            lines.push(rootChildPrefix + "|   `-- (none)");
        }
        xsFiles.forEach((filePath, fileIndex) => {
            let filePrefix = fileIndex === xsFiles.length - 1 ? "`-- " : "|-- ";
            let summary = fileSummaries.get(path.resolve(filePath));
            lines.push(rootChildPrefix + "|   " + filePrefix + relativePackagePath(filePath, packagePath) + formatSeveritySummary(summary));
        });
        lines.push(rootChildPrefix + "`-- load/include graph");
        let graph = root.load_graph || [];
        if (graph.length === 0) {
            lines.push(rootChildPrefix + "    `-- (none)");
        }
        graph.forEach((entry, entryIndex) => {
            let entryPrefix = entryIndex === graph.length - 1 ? "`-- " : "|-- ";
            let entryChildPrefix = entryIndex === graph.length - 1 ? "    " : "|   ";
            let edges = [];
            (entry.loads || []).forEach(load => edges.push({
                label: load.source + " line " + load.line + ": " + load.include + " -> " + load.status + (load.resolved_path ? " (" + relativePackagePath(load.resolved_path, packagePath) + ")" : "") + (load.skipped_reason ? ", " + load.skipped_reason : "")
            }));
            (entry.includes || []).forEach(include => edges.push({
                label: "include line " + include.line + ": " + include.include + " -> " + include.status + (include.resolved_path ? " (" + relativePackagePath(include.resolved_path, packagePath) + ")" : "")
            }));
            lines.push(rootChildPrefix + "    " + entryPrefix + relativePackagePath(entry.path, packagePath) + " [" + (entry.confidence || "unknown") + "]");
            if (edges.length === 0) {
                lines.push(rootChildPrefix + "    " + entryChildPrefix + "`-- (no load/include edges)");
            }
            edges.forEach((edge, edgeIndex) => {
                let edgePrefix = edgeIndex === edges.length - 1 ? "`-- " : "|-- ";
                lines.push(rootChildPrefix + "    " + entryChildPrefix + edgePrefix + edge.label);
            });
        });
    });
    let integrity = payload.integrity || {};
    let manifest = integrity.root_manifest || [];
    lines.push("  root manifest:");
    if (manifest.length === 0) {
        lines.push("    (none)");
    }
    manifest.forEach((entry, index) => {
        let prefix = index === manifest.length - 1 ? "    `-- " : "    |-- ";
        let childPrefix = index === manifest.length - 1 ? "        " : "    |   ";
        lines.push(prefix + relativePackagePath(entry.ai_path, packagePath) + " -> " + entry.status);
        (entry.entries || []).forEach((loadEntry, loadIndex, entries) => {
            let entryPrefix = loadIndex === entries.length - 1 ? "`-- " : "|-- ";
            let lineLabel = loadEntry.line === null || loadEntry.line === undefined ? "" : " line " + loadEntry.line;
            lines.push(childPrefix + entryPrefix + loadEntry.source + lineLabel + ": " + loadEntry.include + " -> " + loadEntry.status);
        });
    });
    lines.push("");
    return lines;
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
    lines.push(...formatPackageLintTrace(payload));
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
async function runLabCommand(args, title, formatStdout) {
    let settings = getLabSettings();
    let channel = getOutputChannel();
    let startedAt = Date.now();
    channel.clear();
    channel.appendLine(title);
    channel.appendLine("status: running");
    channel.appendLine("labPath: " + settings.labPath);
    channel.appendLine("command: " + settings.pythonPath + " " + args.join(" "));
    channel.appendLine("");
    channel.show(false);
    function writeFinalOutput(ok, stdout, stderr) {
        let elapsedSeconds = ((Date.now() - startedAt) / 1000).toFixed(1);
        let body = stdout ? (formatStdout ? formatStdout(stdout) : stdout) : "No output.";
        channel.clear();
        channel.appendLine(title + " complete");
        channel.appendLine("status: " + (ok ? "completed" : "failed"));
        channel.appendLine("duration: " + elapsedSeconds + "s");
        channel.appendLine("labPath: " + settings.labPath);
        channel.appendLine("command: " + settings.pythonPath + " " + args.join(" "));
        channel.appendLine("");
        channel.append(body);
        if (stderr) {
            channel.appendLine("");
            channel.appendLine(stderr);
        }
        channel.show(false);
    }
    if (!settings.labPath || !fs.existsSync(settings.labPath)) {
        writeFinalOutput(false, "", "invalid labPath");
        vscode_1.window.showErrorMessage("AOE2 AI Parser runtime path does not exist. Set aoe2_AiScript.labPath.");
        return { ok: false, stdout: "", stderr: "invalid labPath" };
    }
    let env = Object.assign({}, process.env, { PYTHONPATH: path.join(settings.labPath, "src") });
    return await vscode_1.window.withProgress({
        location: vscode_1.ProgressLocation.Notification,
        title: title,
        cancellable: false
    }, async (progress) => {
        let timer = setInterval(() => {
            let elapsedSeconds = ((Date.now() - startedAt) / 1000).toFixed(0);
            progress.report({ message: "running... " + elapsedSeconds + "s" });
        }, 1000);
        progress.report({ message: "starting..." });
        try {
            let stdout = await execFileTextStreaming(settings.pythonPath, args, {
                cwd: settings.labPath,
                env,
                shell: false,
                windowsHide: true
            }, text => {
                channel.append(text);
            });
            clearInterval(timer);
            progress.report({ message: "complete" });
            writeFinalOutput(true, stdout || "", "");
            return { ok: true, stdout: stdout || "", stderr: "" };
        }
        catch (error) {
            clearInterval(timer);
            progress.report({ message: "failed" });
            let stdout = error.stdout ? String(error.stdout) : "";
            let stderr = error.stderr ? String(error.stderr) : "";
            if (!stdout && !stderr) {
                stderr = String(error.message || error);
            }
            writeFinalOutput(false, stdout, stderr);
            return { ok: false, stdout, stderr };
        }
    });
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
async function currentAiRoot() {
    let filePath = getActiveFilePath();
    if (!filePath) {
        return undefined;
    }
    if (path.extname(filePath).toLowerCase() === ".ai") {
        return filePath;
    }
    let settings = getLabSettings();
    if (settings.labPath && fs.existsSync(settings.labPath)) {
        try {
            let args = ["-m", "aoe2_ai_lab", "resolve-current-ai", filePath, "--json"];
            if (settings.workspacePath) {
                args.push("--search-root", settings.workspacePath);
            }
            let env = Object.assign({}, process.env, { PYTHONPATH: path.join(settings.labPath, "src") });
            let stdout = await execFileText(settings.pythonPath, args, {
                cwd: settings.labPath,
                env,
                shell: false,
                windowsHide: true
            });
            let payload = JSON.parse(stdout);
            let matches = payload.matches || [];
            if (matches.length === 1) {
                return matches[0].ai_path;
            }
            if (matches.length > 1) {
                let picked = await vscode_1.window.showQuickPick(matches.map(match => ({
                    label: path.basename(match.ai_path),
                    description: match.ai_path,
                    detail: "reaches " + path.basename(filePath),
                    file: match.ai_path
                })), {
                    placeHolder: "Multiple .ai roots reach this .per file. Select the AI root to format/lint."
                });
                return picked ? picked.file : undefined;
            }
            vscode_1.window.showWarningMessage("No candidate AI found: no nearby .ai load graph reaches the active file.");
            return undefined;
        }
        catch (error) {
            let channel = getOutputChannel();
            channel.appendLine("Current AI graph resolution failed.");
            channel.appendLine(String(error && error.stderr ? error.stderr : (error && error.message ? error.message : error)));
            vscode_1.window.showErrorMessage("Current AI graph resolution failed. See AOE2 AI Parser output.");
            return undefined;
        }
    }
    vscode_1.window.showWarningMessage("No candidate AI found: AOE2 AI Parser runtime is unavailable.");
    return undefined;
}
async function lintCurrentFile() {
    let filePath = getActiveFilePath();
    if (!filePath) {
        return;
    }
    let result = await runLabCommand(["-m", "aoe2_ai_lab", "lint", filePath], "AoE2: Lint Current File");
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
async function lintCurrentAi(aiRoot) {
    let target = aiRoot || await currentAiRoot();
    if (!target) {
        return { ok: false, stdout: "", stderr: "No current AI root selected." };
    }
    let settings = getLabSettings();
    let reportPath = packageReportPath(settings, target);
    let result = await runLabCommand(["-m", "aoe2_ai_lab", "lint-package", target, "--json", "--report", reportPath, "--fail-level", settings.packageFailLevel, "--trace-progress"], "AoE2: Lint Current AI", stdout => formatPackageIssueGroups(stdout, settings.labPath));
    await openPackageReportPreview(reportPath);
    return result;
}
async function lintFolder() {
    return await lintFolderScope(false);
}
async function lintRecursiveFolder() {
    return await lintFolderScope(true);
}
async function lintFolderScope(recursive) {
    let filePath = getActiveFilePath();
    if (!filePath) {
        return;
    }
    let folderPath = fs.statSync(filePath).isDirectory() ? filePath : path.dirname(filePath);
    let settings = getLabSettings();
    let reportPath = packageReportPath(settings, folderPath);
    let args = ["-m", "aoe2_ai_lab", "lint-package", folderPath, "--json", "--report", reportPath, "--fail-level", settings.packageFailLevel, "--trace-progress"];
    if (!recursive) {
        args.push("--no-recursive");
    }
    let title = recursive ? "AoE2: Lint Recursive Folder" : "AoE2: Lint Current Folder";
    let result = await runLabCommand(args, title, stdout => formatPackageIssueGroups(stdout, settings.labPath));
    let reportOpened = await openPackageReportPreview(reportPath);
    if (result.ok) {
        vscode_1.window.showInformationMessage(reportOpened ? title + " completed. Markdown report opened." : title + " completed. See AOE2 AI Parser output.");
    }
    else if (result.stdout) {
        vscode_1.window.showWarningMessage(reportOpened ? title + " completed with findings. Markdown report opened." : title + " completed with findings.");
    }
    else {
        vscode_1.window.showErrorMessage(title + " failed. See AOE2 AI Parser output.");
    }
    return result;
}
function timestampForReport() {
    return new Date().toISOString().replace(/[:.]/g, "-");
}
function packageReportPath(settings, rootPath) {
    let reportRoot = settings.configuredLabPath ? settings.labPath : (settings.workspacePath || settings.labPath);
    let reportDir = path.join(reportRoot, ".tmp", "lint-package");
    fs.mkdirSync(reportDir, { recursive: true });
    return path.join(reportDir, path.basename(rootPath) + "-" + timestampForReport() + ".md");
}
async function openPackageReportPreview(reportPath) {
    if (!fs.existsSync(reportPath)) {
        return false;
    }
    let reportUri = vscode_1.Uri.file(reportPath);
    try {
        await vscode_1.commands.executeCommand("markdown.showPreviewToSide", reportUri);
        return true;
    }
    catch (_error) {
        try {
            await vscode_1.commands.executeCommand("vscode.openWith", reportUri, "vscode.markdown.preview.editor", { viewColumn: vscode_1.ViewColumn.Beside, preview: false });
            return true;
        }
        catch (_fallbackError) {
            let document = await vscode_1.workspace.openTextDocument(reportPath);
            await vscode_1.window.showTextDocument(document, vscode_1.ViewColumn.Beside);
            return true;
        }
    }
}
async function generatePackageReport() {
    let packageRoot = getCurrentPackageRoot();
    if (!packageRoot) {
        return;
    }
    let settings = getLabSettings();
    let reportPath = packageReportPath(settings, packageRoot);
    let result = await runLabCommand(["-m", "aoe2_ai_lab", "lint-package", packageRoot, "--report", reportPath, "--fail-level", settings.packageFailLevel, "--trace-progress"], "AoE2: Generate Package Report");
    if (fs.existsSync(reportPath)) {
        await openPackageReportPreview(reportPath);
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
async function openLatestPackageReport() {
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
    await openPackageReportPreview(reports[0]);
}
function formatCommandArgs(filePath, stdout, options) {
    let settings = getFormatSettings();
    let args = ["-m", "aoe2_ai_lab", "format", filePath, "--max-line-length", String(settings.maxLineLength)];
    if (settings.formatChat) {
        args.push("--format-chat");
    }
    if (options && options.includeLoads) {
        args.push("--include-loads");
    }
    if (options && options.recursive === false) {
        args.push("--no-recursive");
    }
    if (stdout) {
        args.push("--stdin");
    }
    else {
        args.push("--write");
    }
    return args;
}
async function formattedTextForDocument(document) {
    let settings = getLabSettings();
    if (!settings.labPath || !fs.existsSync(settings.labPath)) {
        throw new Error("AOE2 AI Parser runtime path does not exist. Set aoe2_AiScript.labPath.");
    }
    let env = Object.assign({}, process.env, { PYTHONPATH: path.join(settings.labPath, "src") });
    return await execFileTextInput(settings.pythonPath, formatCommandArgs(document.uri.fsPath, true, {}), document.getText(), {
        cwd: settings.labPath,
        env,
        shell: false,
        windowsHide: true
    });
}
async function autoFormat() {
    let editor = vscode_1.window.activeTextEditor;
    if (!editor || editor.document.uri.scheme !== "file" || editor.document.languageId !== "aoe2aiscript") {
        vscode_1.window.showWarningMessage("Open an AoE2 .per or .ai file first.");
        return;
    }
    try {
        let formatted = await formattedTextForDocument(editor.document);
        if (formatted === editor.document.getText()) {
            vscode_1.window.showInformationMessage("AoE2 AutoFormat: no changes.");
            return { ok: true };
        }
        let fullRange = new vscode_1.Range(editor.document.positionAt(0), editor.document.positionAt(editor.document.getText().length));
        await editor.edit(editBuilder => editBuilder.replace(fullRange, formatted));
        vscode_1.window.showInformationMessage("AoE2 AutoFormat applied.");
        return { ok: true };
    }
    catch (error) {
        let channel = getOutputChannel();
        channel.clear();
        channel.appendLine("AoE2 AutoFormat failed.");
        channel.appendLine(String(error && error.stderr ? error.stderr : (error && error.message ? error.message : error)));
        channel.show(false);
        vscode_1.window.showErrorMessage("AoE2 AutoFormat failed. See AOE2 AI Parser output.");
        return { ok: false };
    }
}
async function saveOpenPackageDocuments(packageRoot) {
    let root = normalizeFsPath(packageRoot);
    let saves = vscode_1.workspace.textDocuments
        .filter(document => document.uri.scheme === "file" && document.languageId === "aoe2aiscript" && document.isDirty)
        .filter(document => {
        let filePath = normalizeFsPath(document.uri.fsPath);
        return filePath === root || filePath.startsWith(root + path.sep.toLowerCase());
    })
        .map(document => document.save());
    if (saves.length > 0) {
        await Promise.all(saves);
    }
}
async function autoFormatCurrentAi() {
    let aiRoot = await currentAiRoot();
    if (!aiRoot) {
        return;
    }
    await saveOpenPackageDocuments(path.dirname(aiRoot));
    let result = await runLabCommand(formatCommandArgs(aiRoot, false, { includeLoads: true }), "AoE2: AutoFormat Current AI");
    if (result.ok) {
        vscode_1.window.showInformationMessage(result.stdout ? "AoE2 AutoFormat Current AI applied." : "AoE2 AutoFormat Current AI: no changes.");
    }
    else {
        vscode_1.window.showErrorMessage("AoE2 AutoFormat Current AI failed. See AOE2 AI Parser output.");
    }
}
async function autoFormatFolder(recursive) {
    let filePath = getActiveFilePath();
    if (!filePath) {
        return;
    }
    let folderPath = fs.statSync(filePath).isDirectory() ? filePath : path.dirname(filePath);
    await saveOpenPackageDocuments(folderPath);
    let title = recursive ? "AoE2: AutoFormat Recursive Folder" : "AoE2: AutoFormat Current Folder";
    let result = await runLabCommand(formatCommandArgs(folderPath, false, { recursive }), title);
    if (result.ok) {
        vscode_1.window.showInformationMessage(result.stdout ? title + " applied." : title + ": no changes.");
    }
    else {
        vscode_1.window.showErrorMessage(title + " failed. See AOE2 AI Parser output.");
    }
}
async function formatThenLintCurrentFile() {
    let formatResult = await autoFormat();
    if (formatResult && formatResult.ok) {
        await lintCurrentFile();
    }
}
async function formatThenLintCurrentAi() {
    let aiRoot = await currentAiRoot();
    if (!aiRoot) {
        return;
    }
    await saveOpenPackageDocuments(path.dirname(aiRoot));
    let formatResult = await runLabCommand(formatCommandArgs(aiRoot, false, { includeLoads: true }), "AoE2: AutoFormat Current AI");
    if (formatResult.ok) {
        await lintCurrentAi(aiRoot);
    }
}
async function formatThenLintFolder(recursive) {
    let filePath = getActiveFilePath();
    if (!filePath) {
        return;
    }
    let folderPath = fs.statSync(filePath).isDirectory() ? filePath : path.dirname(filePath);
    await saveOpenPackageDocuments(folderPath);
    let formatTitle = recursive ? "AoE2: AutoFormat Recursive Folder" : "AoE2: AutoFormat Current Folder";
    let formatResult = await runLabCommand(formatCommandArgs(folderPath, false, { recursive }), formatTitle);
    if (!formatResult.ok) {
        return;
    }
    let settings = getLabSettings();
    let reportPath = packageReportPath(settings, folderPath);
    let lintTitle = recursive ? "AoE2: Lint Recursive Folder" : "AoE2: Lint Current Folder";
    let lintArgs = ["-m", "aoe2_ai_lab", "lint-package", folderPath, "--json", "--report", reportPath, "--fail-level", settings.packageFailLevel, "--trace-progress"];
    if (!recursive) {
        lintArgs.push("--no-recursive");
    }
    let lintResult = await runLabCommand(lintArgs, lintTitle, stdout => formatPackageIssueGroups(stdout, settings.labPath));
    await openPackageReportPreview(reportPath);
    return lintResult;
}
function autoFormatOnSave(event) {
    if (event.document.uri.scheme !== "file" || event.document.languageId !== "aoe2aiscript") {
        return;
    }
    if (!getFormatSettings().formatOnSave) {
        return;
    }
    event.waitUntil(formattedTextForDocument(event.document).then(formatted => {
        if (formatted === event.document.getText()) {
            return [];
        }
        let fullRange = new vscode_1.Range(event.document.positionAt(0), event.document.positionAt(event.document.getText().length));
        return [vscode_1.TextEdit.replace(fullRange, formatted)];
    }, error => {
        let channel = getOutputChannel();
        channel.clear();
        channel.appendLine("AoE2 AutoFormat on save failed.");
        channel.appendLine(String(error && error.stderr ? error.stderr : (error && error.message ? error.message : error)));
        channel.show(false);
        return [];
    }));
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
function markdownHeadingFragment(symbol) {
    return markdownAnchor(symbol);
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
    let fragment = markdownHeadingFragment(symbol);
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
    if (semanticColorsEnabled() && vscode_1.languages.registerDocumentSemanticTokensProvider && vscode_1.SemanticTokensBuilder && vscode_1.SemanticTokensLegend) {
        semanticTokenLegend = new vscode_1.SemanticTokensLegend(semanticTokenTypes, ["declaration"]);
        context.subscriptions.push(vscode_1.languages.registerDocumentSemanticTokensProvider({ language: 'aoe2aiscript', scheme: 'file' }, {
            provideDocumentSemanticTokens: semanticTokensForDocument
        }, semanticTokenLegend));
    }
    refreshSemanticDecorationTypes();
    updateSemanticDecorationsForVisibleEditors();
    context.subscriptions.push({
        dispose: disposeSemanticDecorations
    });
    context.subscriptions.push(vscode_1.window.onDidChangeVisibleTextEditors(updateSemanticDecorationsForVisibleEditors));
    context.subscriptions.push(vscode_1.workspace.onDidChangeTextDocument(event => {
        scheduleSemanticDecorationUpdate(event.document);
    }));
    context.subscriptions.push(vscode_1.workspace.onDidChangeConfiguration(event => {
        if (event.affectsConfiguration("aoe2_AiScript.enableSemanticColors") || event.affectsConfiguration("aoe2_AiScript.semanticColors")) {
            vscode_1.window.visibleTextEditors.forEach(clearSemanticDecorationsForEditor);
            refreshSemanticDecorationTypes();
            updateSemanticDecorationsForVisibleEditors();
        }
    }));
    context.subscriptions.push(vscode_1.languages.registerHoverProvider('aoe2aiscript', {
        provideHover: symbolDocsHover
    }));
    context.subscriptions.push(vscode_1.commands.registerCommand("aoe2AiScript.lintCurrentFile", lintCurrentFile));
    context.subscriptions.push(vscode_1.commands.registerCommand("aoe2AiScript.lintCurrentAi", () => lintCurrentAi()));
    context.subscriptions.push(vscode_1.commands.registerCommand("aoe2AiScript.lintFolder", lintFolder));
    context.subscriptions.push(vscode_1.commands.registerCommand("aoe2AiScript.lintRecursiveFolder", lintRecursiveFolder));
    context.subscriptions.push(vscode_1.commands.registerCommand("aoe2AiScript.generatePackageReport", generatePackageReport));
    context.subscriptions.push(vscode_1.commands.registerCommand("aoe2AiScript.openLatestPackageReport", openLatestPackageReport));
    context.subscriptions.push(vscode_1.commands.registerCommand("aoe2AiScript.autoFormat", autoFormat));
    context.subscriptions.push(vscode_1.commands.registerCommand("aoe2AiScript.autoFormatCurrentAi", autoFormatCurrentAi));
    context.subscriptions.push(vscode_1.commands.registerCommand("aoe2AiScript.autoFormatCurrentFolder", () => autoFormatFolder(false)));
    context.subscriptions.push(vscode_1.commands.registerCommand("aoe2AiScript.autoFormatRecursiveFolder", () => autoFormatFolder(true)));
    context.subscriptions.push(vscode_1.commands.registerCommand("aoe2AiScript.formatThenLintCurrentFile", formatThenLintCurrentFile));
    context.subscriptions.push(vscode_1.commands.registerCommand("aoe2AiScript.formatThenLintCurrentAi", formatThenLintCurrentAi));
    context.subscriptions.push(vscode_1.commands.registerCommand("aoe2AiScript.formatThenLintCurrentFolder", () => formatThenLintFolder(false)));
    context.subscriptions.push(vscode_1.commands.registerCommand("aoe2AiScript.formatThenLintRecursiveFolder", () => formatThenLintFolder(true)));
    context.subscriptions.push(vscode_1.workspace.onWillSaveTextDocument(autoFormatOnSave));
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
