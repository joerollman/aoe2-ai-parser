"use strict";
/* --------------------------------------------------------------------------------------------
 * Copyright (c) Microsoft Corporation. All rights reserved.
 * Licensed under the MIT License. See License.txt in the project root for license information.
 * ------------------------------------------------------------------------------------------ */
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : new P(function (resolve) { resolve(result.value); }).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
Object.defineProperty(exports, "__esModule", { value: true });
const child_process_1 = require("child_process");
const fs = require("fs");
const path = require("path");
const vscode_languageserver_1 = require("vscode-languageserver");
const vscode_uri_1 = require("vscode-uri");
// Import the needed methods and objects
const aiScriptResources_1 = require("./aiScriptResources");
const aiScriptParser_1 = require("./aiScriptParser");
// Create a connection for the server. The connection uses Node's IPC as a transport.
// Also include all preview / proposed LSP features.
let connection = vscode_languageserver_1.createConnection(vscode_languageserver_1.ProposedFeatures.all);
// Create a simple text document manager. The text document manager
// supports full document sync only
let documents = new vscode_languageserver_1.TextDocuments();
let hasConfigurationCapability = false;
let hasWorkspaceFolderCapability = false;
let hasDiagnosticRelatedInformationCapability = false;
// List of parameters
let aiScriptTypes = aiScriptResources_1.loadAoE2Parameters();
let aiScriptCompletionList = { items: [], isIncomplete: false };
let labRegistryHoverMap = undefined;
let labRegistryItemByLabelMap = undefined;
let labCommandParameterMap = undefined;
let labCommandItemMap = undefined;
let labRegistryItemsByKindMap = undefined;
let labDiagnosticExplanationMap = undefined;
function labRegistryPath() {
    return path.resolve(__dirname, "..", "..", "data", "completions.json");
}
function labDiagnosticRegistryPath() {
    return path.resolve(__dirname, "..", "..", "data", "diagnostic-codes.json");
}
function extensionRootPath() {
    return path.resolve(__dirname, "..", "..");
}
function bundledLabPath() {
    let labPath = path.join(extensionRootPath(), "lab");
    return fs.existsSync(path.join(labPath, "src", "aoe2_ai_lab")) ? labPath : undefined;
}
function loadLabRegistryItems() {
    let completionsPath = labRegistryPath();
    if (!fs.existsSync(completionsPath)) {
        connection.console.log("aoe2-ai-lab completions not found: " + completionsPath);
        return [];
    }
    try {
        let payload = JSON.parse(fs.readFileSync(completionsPath, "utf8"));
        return payload.items || [];
    }
    catch (error) {
        connection.console.error("could not load aoe2-ai-lab completions: " + String(error.message || error));
        return [];
    }
}
function labCommandParameters() {
    if (labCommandParameterMap !== undefined) {
        return labCommandParameterMap;
    }
    labCommandParameterMap = new Map();
    loadLabRegistryItems().forEach(item => {
        if (item.kind !== "command" || !item.documentation) {
            return;
        }
        let match = /Syntax:\s*`[\(#]?([#A-Za-z0-9_-]+)\s*([^`]*)`/.exec(item.documentation);
        if (!match) {
            return;
        }
        let params = [];
        let pattern = /<([^>]+)>/g;
        let paramMatch;
        while ((paramMatch = pattern.exec(match[2])) !== null) {
            params.push(paramMatch[1]);
        }
        labCommandParameterMap.set(item.label, params);
    });
    return labCommandParameterMap;
}
function labRegistryItemByLabel() {
    if (labRegistryItemByLabelMap !== undefined) {
        return labRegistryItemByLabelMap;
    }
    labRegistryItemByLabelMap = new Map();
    loadLabRegistryItems().forEach(item => {
        if (item.label && !labRegistryItemByLabelMap.has(item.label)) {
            labRegistryItemByLabelMap.set(item.label, item);
        }
    });
    return labRegistryItemByLabelMap;
}
function labCommandItems() {
    if (labCommandItemMap !== undefined) {
        return labCommandItemMap;
    }
    labCommandItemMap = new Map();
    loadLabRegistryItems().forEach(item => {
        if (item.kind === "command" && item.label) {
            labCommandItemMap.set(item.label, item);
        }
    });
    return labCommandItemMap;
}
function labRegistryItemsByKind() {
    if (labRegistryItemsByKindMap !== undefined) {
        return labRegistryItemsByKindMap;
    }
    labRegistryItemsByKindMap = new Map();
    loadLabRegistryItems().forEach(item => {
        if (!item.kind || !item.label) {
            return;
        }
        if (!labRegistryItemsByKindMap.has(item.kind)) {
            labRegistryItemsByKindMap.set(item.kind, []);
        }
        labRegistryItemsByKindMap.get(item.kind).push(item);
    });
    return labRegistryItemsByKindMap;
}
function labCompletionKind(kind) {
    switch (kind) {
        case "command":
            return vscode_languageserver_1.CompletionItemKind.Function;
        case "strategic-number":
            return vscode_languageserver_1.CompletionItemKind.Constant;
        case "object":
            return vscode_languageserver_1.CompletionItemKind.Unit;
        case "tech":
            return vscode_languageserver_1.CompletionItemKind.Class;
        case "value":
            return vscode_languageserver_1.CompletionItemKind.Value;
        default:
            return vscode_languageserver_1.CompletionItemKind.Text;
    }
}
function addLabRegistryCompletions(existingLabels) {
    loadLabRegistryItems().forEach(item => {
        if (!item.label || existingLabels.has(item.label)) {
            return;
        }
        existingLabels.add(item.label);
        aiScriptCompletionList.items.push({
            label: item.label,
            detail: item.detail,
            documentation: item.documentation ? { value: item.documentation, kind: 'markdown' } : undefined,
            insertText: item.insertText || item.label,
            sortText: item.sortText,
            kind: labCompletionKind(item.kind),
            data: { labKind: item.kind }
        });
    });
}
function labRegistryHovers() {
    if (labRegistryHoverMap !== undefined) {
        return labRegistryHoverMap;
    }
    labRegistryHoverMap = new Map();
    loadLabRegistryItems().forEach(item => {
        if (!item.label || labRegistryHoverMap.has(item.label)) {
            return;
        }
        let parts = [];
        if (item.detail) {
            parts.push("**" + item.label + "**  \n" + item.detail);
        }
        else {
            parts.push("**" + item.label + "**");
        }
        if (item.documentation) {
            parts.push(item.documentation);
        }
        labRegistryHoverMap.set(item.label, parts.join("\n\n"));
    });
    return labRegistryHoverMap;
}
function labRegistryHover(hoverText) {
    let value = labRegistryHovers().get(hoverText);
    if (!value) {
        return undefined;
    }
    return {
        contents: { kind: 'markdown', value }
    };
}
function labDiagnosticExplanations() {
    if (labDiagnosticExplanationMap !== undefined) {
        return labDiagnosticExplanationMap;
    }
    labDiagnosticExplanationMap = new Map();
    let registryPath = labDiagnosticRegistryPath();
    if (!fs.existsSync(registryPath)) {
        connection.console.log("aoe2-ai-lab diagnostic registry not found: " + registryPath);
        return labDiagnosticExplanationMap;
    }
    try {
        let payload = JSON.parse(fs.readFileSync(registryPath, "utf8"));
        (payload.codes || []).forEach(entry => {
            if (entry.code && entry.meaning) {
                labDiagnosticExplanationMap.set(entry.code, entry.meaning);
            }
        });
    }
    catch (error) {
        connection.console.error("could not load aoe2-ai-lab diagnostic registry: " + String(error.message || error));
    }
    return labDiagnosticExplanationMap;
}
/**********************************************************************/ /**
 * Initialize the server connection
 * 	@param params 			Parameters for initialization
 **************************************************************************/
connection.onInitialize((params) => {
    let capabilities = params.capabilities;
    // Fill the list of completion items
    fillCompletions();
    // Does the client support the `workspace/configuration` request?
    // If not, we will fall back using global settings
    hasConfigurationCapability = !!(capabilities.workspace && !!capabilities.workspace.configuration);
    hasWorkspaceFolderCapability = !!(capabilities.workspace && !!capabilities.workspace.workspaceFolders);
    hasDiagnosticRelatedInformationCapability =
        !!(capabilities.textDocument &&
            capabilities.textDocument.publishDiagnostics &&
            capabilities.textDocument.publishDiagnostics.relatedInformation);
    connection.console.log("workspacefoldercapability: " + hasWorkspaceFolderCapability);
    return {
        capabilities: {
            textDocumentSync: documents.syncKind,
            // Tell the client that the server supports code completion
            completionProvider: { resolveProvider: false },
            // Tell the client we can offer quick fixes for lab diagnostics
            codeActionProvider: true,
            // Tell the client we can navigate to local declarations/docs
            definitionProvider: true,
            declarationProvider: true,
            // Tell the client we support hover text
            hoverProvider: true,
            // Tell client we support signature help
            signatureHelpProvider: { triggerCharacters: [' '] }
        }
    };
});
/**********************************************************************/ /**
 * Register some things after initializing server connection
 **************************************************************************/
connection.onInitialized(() => {
    if (hasConfigurationCapability) {
        // Register for all configuration changes.
        connection.client.register(vscode_languageserver_1.DidChangeConfigurationNotification.type, undefined);
    }
    if (hasWorkspaceFolderCapability) {
        connection.workspace.onDidChangeWorkspaceFolders(_event => {
            connection.console.log('Workspace folder change event received.');
        });
    }
});
/**********************************************************************/ /**
 * The global settings, used when the `workspace/configuration` request is
 * not supported by the client.
 **************************************************************************/
const defaultSettings = {
    updateErrorsWhen: "onSave",
    maxErrorsReported: 100,
    enableCompletionHelp: false,
    enableHoverHelp: false,
    enableParameterHelp: "off",
    aiName: "",
    aiDirectory: "",
    useLabLinter: true,
    usePackageLint: true,
    labPath: "",
    pythonPath: "python"
};
let globalSettings = defaultSettings;
// Cache the settings of all open documents
let documentSettings = new Map();
/**********************************************************************/ /**
 * Update configuration parameters when user changes them
 * 	@param change			New configuration settings
 **************************************************************************/
connection.onDidChangeConfiguration(change => {
    if (hasConfigurationCapability) {
        // Reset all cached document settings
        documentSettings.clear();
        connection.console.log("Registered config change");
    }
    else {
        globalSettings = ((change.settings.aoe2_AiScript || defaultSettings));
    }
    // Re-generate the list of completions
    fillCompletions();
    // Revalidate all open text documents
    documents.all().forEach(validateTextDocument);
});
/**********************************************************************/ /**
 * Return the current document settings. Also caches them for future reference.
 * 	@param resource			URI of the document in question
 **************************************************************************/
function getDocumentSettings(resource) {
    if (!hasConfigurationCapability) {
        return Promise.resolve(globalSettings);
    }
    let result = documentSettings.get(resource);
    if (!result) {
        result = connection.workspace.getConfiguration({
            scopeUri: resource,
            section: 'aoe2_AiScript'
        });
        documentSettings.set(resource, result);
    }
    return result;
}
/**********************************************************************/ /**
 * Deletes cached settings when a document is closed
 * 	@param e				TextDocumentChangeEvent
 **************************************************************************/
documents.onDidClose(e => {
    documentSettings.delete(e.document.uri);
});
/**********************************************************************/ /**
 * The content of a text document has changed. This event is emitted
 * when the text document first opened or when its content has changed.
 * 	@param change			TextDocumentChangeEvent
 **************************************************************************/
documents.onDidChangeContent(change => {
    // Check that we want to update 'onChange'
    validateTextDocumentOnChange(change.document);
});
/**********************************************************************/ /**
 * Re-evaluate a document for errors if the user has specified
 * 'updateErrorsWhen === "onChnage".
 * 	@param textDocument		Document to be re-evaluated
 **************************************************************************/
function validateTextDocumentOnChange(textDocument) {
    return __awaiter(this, void 0, void 0, function* () {
        let settings = yield getDocumentSettings(textDocument.uri);
        if (settings.updateErrorsWhen === "onChange") {
            validateTextDocument(textDocument);
        }
    });
}
/**********************************************************************/ /**
 * When a file is saved, re-evaluate the document for errors
 * 	@param change			TextDocumentChangeEvent
 **************************************************************************/
documents.onDidSave(change => {
    validateTextDocumentOnSave(change.document);
});
/**********************************************************************/ /**
 * Re-evaluate a document for errors if the user has specified
 * 'updateErrorsWhen === "onChnage".
 * 	@param textDocument		Document to be re-evaluated
 **************************************************************************/
function validateTextDocumentOnSave(textDocument) {
    return __awaiter(this, void 0, void 0, function* () {
        let settings = yield getDocumentSettings(textDocument.uri);
        if (settings.updateErrorsWhen === "onSave") {
            validateTextDocument(textDocument);
        }
    });
}
/**********************************************************************/ /**
 * When a file is opened, evaluate the document for errors
 * 	@param change			TextDocumentChangeEvent
 **************************************************************************/
documents.onDidOpen(change => {
    //connection.console.log("Openned "+change.document.uri);
    validateTextDocument(change.document);
});
function labSeverityToDiagnosticSeverity(severity) {
    if (severity === "error") {
        return vscode_languageserver_1.DiagnosticSeverity.Error;
    }
    if (severity === "warning") {
        return vscode_languageserver_1.DiagnosticSeverity.Warning;
    }
    return vscode_languageserver_1.DiagnosticSeverity.Information;
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
            return null;
        }
        let parent = path.dirname(current);
        if (current === parent) {
            return isPerFile ? filePath : null;
        }
        if (path.relative(workspaceRoot, parent).startsWith("..")) {
            return isPerFile ? filePath : null;
        }
        current = parent;
    }
}
function diagnosticRangeForLine(textDocument, lineNumber, code, message, span) {
    if (span && span.start_line && span.end_line && span.start_col !== undefined && span.end_col !== undefined) {
        return {
            start: { line: Math.max(0, Number(span.start_line) - 1), character: Math.max(0, Number(span.start_col)) },
            end: { line: Math.max(0, Number(span.end_line) - 1), character: Math.max(1, Number(span.end_col)) }
        };
    }
    let lineIndex = Math.max(0, Number(lineNumber) - 1);
    let sourceLine = textDocument.getText({
        start: { line: lineIndex, character: 0 },
        end: { line: lineIndex + 1, character: 0 }
    });
    let trimmedLine = sourceLine.trimEnd();
    let quotedToken = /'([^']+)'/.exec(message);
    if (quotedToken) {
        let tokenIndex = trimmedLine.indexOf(quotedToken[1]);
        if (tokenIndex >= 0) {
            return {
                start: { line: lineIndex, character: tokenIndex },
                end: { line: lineIndex, character: tokenIndex + quotedToken[1].length }
            };
        }
    }
    if (code === "repeat-chat") {
        let chatMatch = /\(\s*(chat-to-all|chat-to-player)\b/.exec(trimmedLine);
        if (chatMatch) {
            let tokenIndex = chatMatch.index + chatMatch[0].indexOf(chatMatch[1]);
            return {
                start: { line: lineIndex, character: tokenIndex },
                end: { line: lineIndex, character: tokenIndex + chatMatch[1].length }
            };
        }
    }
    let commandMatch = /\(\s*([#A-Za-z][A-Za-z0-9_-]*)\b/.exec(trimmedLine);
    if (commandMatch) {
        let tokenIndex = commandMatch.index + commandMatch[0].indexOf(commandMatch[1]);
        return {
            start: { line: lineIndex, character: tokenIndex },
            end: { line: lineIndex, character: tokenIndex + commandMatch[1].length }
        };
    }
    return {
        start: { line: lineIndex, character: 0 },
        end: { line: lineIndex, character: Math.max(1, trimmedLine.length) }
    };
}
function labFindingToDiagnostic(textDocument, severity, code, message, line, span) {
    return {
        severity: labSeverityToDiagnosticSeverity(severity),
        code: severity + ":" + code,
        range: diagnosticRangeForLine(textDocument, line, code, message, span),
        message: "[" + severity + "] " + code + ": " + message,
        source: "aoe2-ai-lab"
    };
}
function labSetupDiagnostic(message, labPath, pythonPath, commandArgs) {
    return [{
            severity: vscode_languageserver_1.DiagnosticSeverity.Error,
            code: "error:aoe2-ai-lab-setup",
            range: {
                start: { line: 0, character: 0 },
                end: { line: 0, character: 1 }
            },
            message: "[error] aoe2-ai-lab setup: " + message.trim() + "\npythonPath: " + pythonPath + "\nlabPath: " + labPath + "\ncommand: " + pythonPath + " " + commandArgs.join(" "),
            source: "aoe2-ai-lab"
        }];
}
function collectAiRootDiagnostics(textDocument, payload, currentPath) {
    let diagnostics = [];
    let currentFileIsAiRoot = false;
    (((payload.integrity || {}).root_manifest) || []).forEach(root => {
        if (normalizeFsPath(root.ai_path) !== currentPath) {
            return;
        }
        currentFileIsAiRoot = true;
        (root.entries || []).forEach(entry => {
            if (entry.status !== "unresolved") {
                return;
            }
            let includeName = entry.include || "unknown-load-target";
            let line = entry.line || 1;
            diagnostics.push(labFindingToDiagnostic(textDocument, "error", "missing-load-target", "'" + includeName + "' does not resolve to a reachable .per file", line));
        });
        (root.entries || []).forEach(entry => {
            if (entry.status !== "skipped") {
                return;
            }
            let includeName = entry.include || "unknown-load-target";
            let line = entry.line || 1;
            let reason = entry.skipped_reason || "skipped";
            diagnostics.push(labFindingToDiagnostic(textDocument, "info", "skipped-load-random", "'" + includeName + "' is skipped by load-random manifest resolution: " + reason, line));
        });
        (((payload.integrity || {}).duplicate_root_targets) || []).forEach(duplicate => {
            if (!(duplicate.ai_paths || []).some(aiPath => normalizeFsPath(aiPath) === currentPath)) {
                return;
            }
            let duplicatePath = normalizeFsPath(duplicate.per_path || "");
            let matchingEntry = (root.entries || []).find(entry => entry.resolved_path && normalizeFsPath(entry.resolved_path) === duplicatePath);
            let line = matchingEntry && matchingEntry.line ? matchingEntry.line : 1;
            let includeName = matchingEntry && matchingEntry.include ? matchingEntry.include : path.basename(duplicate.per_path || "duplicate-root");
            let roots = (duplicate.ai_paths || []).map(aiPath => path.basename(aiPath)).join(", ");
            diagnostics.push(labFindingToDiagnostic(textDocument, "warning", "duplicate-root-target", "'" + includeName + "' is loaded as a root by multiple .ai files: " + roots, line));
        });
        (((payload.integrity || {}).duplicate_ai_names) || []).forEach(duplicate => {
            if (!(duplicate.ai_paths || []).some(aiPath => normalizeFsPath(aiPath) === currentPath)) {
                return;
            }
            let roots = (duplicate.ai_paths || []).map(aiPath => path.basename(aiPath)).join(", ");
            diagnostics.push(labFindingToDiagnostic(textDocument, "warning", "duplicate-ai-name", "AI display name '" + (duplicate.name || path.basename(currentPath, ".ai")) + "' is shared by multiple .ai files: " + roots, 1));
        });
        (((payload.integrity || {}).duplicate_load_targets) || []).forEach(duplicate => {
            if (normalizeFsPath(duplicate.ai_path) !== currentPath) {
                return;
            }
            let references = duplicate.references || [];
            let line = references.length > 1 && references[1].line ? references[1].line : (references[0] && references[0].line ? references[0].line : 1);
            diagnostics.push(labFindingToDiagnostic(textDocument, "warning", "duplicate-load-target", "AI loads '" + path.basename(duplicate.target_path || "duplicate-load-target") + "' more than once", line));
        });
    });
    (((payload.integrity || {}).stale_ai_roots) || []).forEach(stale => {
        if (normalizeFsPath(stale.ai_path) !== currentPath) {
            return;
        }
        currentFileIsAiRoot = true;
        diagnostics.push(labFindingToDiagnostic(textDocument, "error", "stale-ai-root", stale.message || "AI root has no reachable .per file", 1));
    });
    return { currentFileIsAiRoot, diagnostics };
}
function runLabPackageLinter(textDocument, settings, labPath, pythonPath, env, workspacePath, filePath) {
    if (settings.usePackageLint === false) {
        return null;
    }
    let packageRoot = findNearestPackageRoot(filePath, workspacePath);
    if (!packageRoot) {
        return null;
    }
    let stdout = "";
    try {
        stdout = child_process_1.execFileSync(pythonPath, ["-m", "aoe2_ai_lab", "lint-package", packageRoot, "--json", "--fail-level", "error"], {
            cwd: labPath,
            env,
            encoding: "utf8",
            windowsHide: true
        });
    }
    catch (error) {
        stdout = error.stdout ? String(error.stdout) : "";
        if (!stdout) {
            return null;
        }
    }
    let payload;
    try {
        payload = JSON.parse(stdout);
    }
    catch (_error) {
        return null;
    }
    let currentPath = normalizeFsPath(filePath);
    let diagnostics = [];
    let aiRootDiagnostics = collectAiRootDiagnostics(textDocument, payload, currentPath);
    if (aiRootDiagnostics.currentFileIsAiRoot) {
        return aiRootDiagnostics.diagnostics;
    }
    let currentFileIsReachable = false;
    (payload.roots || []).forEach(root => {
        (root.file_summaries || []).forEach(summary => {
            if (normalizeFsPath(summary.path) === currentPath) {
                currentFileIsReachable = true;
            }
        });
        (root.findings || []).forEach(finding => {
            if (normalizeFsPath(finding.path) !== currentPath) {
                return;
            }
            currentFileIsReachable = true;
            diagnostics.push(labFindingToDiagnostic(textDocument, finding.severity, finding.code, finding.message, finding.line, finding.span));
        });
    });
    (((payload.integrity || {}).duplicate_per_names) || []).forEach(duplicate => {
        if (!(duplicate.per_paths || []).some(perPath => normalizeFsPath(perPath) === currentPath)) {
            return;
        }
        currentFileIsReachable = true;
        let files = (duplicate.per_paths || []).map(perPath => path.basename(perPath)).join(", ");
        diagnostics.push(labFindingToDiagnostic(textDocument, "warning", "duplicate-per-name", ".per basename '" + (duplicate.name || path.basename(currentPath, ".per")) + "' is shared by multiple files: " + files, 1));
    });
    if (!currentFileIsReachable) {
        return null;
    }
    return diagnostics;
}
function runLabLinter(textDocument, settings, workspaceFolder) {
    let labPath = settings.labPath || bundledLabPath() || vscode_uri_1.URI.parse(workspaceFolder).fsPath;
    let pythonPath = settings.pythonPath || "python";
    let filePath = vscode_uri_1.URI.parse(textDocument.uri).fsPath;
    let workspacePath = vscode_uri_1.URI.parse(workspaceFolder).fsPath;
    let env = Object.assign({}, process.env, { PYTHONPATH: path.join(labPath, "src") });
    if (!fs.existsSync(labPath)) {
        return labSetupDiagnostic("aoe2-ai-lab runtime does not exist. Reinstall the extension or set aoe2_AiScript.labPath to an aoe2-ai-lab checkout.", labPath, pythonPath, ["-m", "aoe2_ai_lab", "lint", filePath]);
    }
    let packageDiagnostics = runLabPackageLinter(textDocument, settings, labPath, pythonPath, env, workspacePath, filePath);
    if (packageDiagnostics !== null) {
        if (settings.maxErrorsReported >= 0) {
            return packageDiagnostics.slice(0, settings.maxErrorsReported);
        }
        return packageDiagnostics;
    }
    let stdout = "";
    let lintArgs = ["-m", "aoe2_ai_lab", "lint", filePath, "--json"];
    try {
        stdout = child_process_1.execFileSync(pythonPath, lintArgs, {
            cwd: labPath,
            env,
            encoding: "utf8",
            windowsHide: true
        });
    }
    catch (error) {
        stdout = error.stdout ? String(error.stdout) : "";
        if (!stdout) {
            let message = error.stderr ? String(error.stderr) : String(error.message || error);
            return labSetupDiagnostic("linter failed before producing diagnostics. " + message, labPath, pythonPath, lintArgs);
        }
    }
    let diagnostics = [];
    try {
        let payload = JSON.parse(stdout);
        (payload.findings || []).forEach(finding => {
            diagnostics.push(labFindingToDiagnostic(textDocument, finding.severity, finding.code, finding.message, finding.line, finding.span));
        });
    }
    catch (_error) {
        let pattern = /^(.+?):(\d+):\s+(error|warning|info):\s+([^:]+):\s+(.+)$/;
        stdout.split(/\r?\n/).forEach(line => {
            let match = pattern.exec(line);
            if (!match) {
                return;
            }
            let labSeverity = match[3];
            let labCode = match[4];
            diagnostics.push(labFindingToDiagnostic(textDocument, labSeverity, labCode, match[5], match[2]));
        });
    }
    if (settings.maxErrorsReported >= 0) {
        diagnostics = diagnostics.slice(0, settings.maxErrorsReported);
    }
    return diagnostics;
}
/**********************************************************************/ /**
 * Evaluates a given text document for errors
 * 	@param textDocument		Document to be evaluated
 **************************************************************************/
function validateTextDocument(textDocument) {
    return __awaiter(this, void 0, void 0, function* () {
        // In this simple example we get the settings for every validate run.
        let settings = yield getDocumentSettings(textDocument.uri);
        let diagnostics = [];
        // Quit if no checks were actually requested
        connection.console.log(settings.aiName);
        if ((settings.maxErrorsReported === 0) || (settings.updateErrorsWhen === "never")) {
            return;
        }
        let folders = yield connection.workspace.getWorkspaceFolders();
        let workspaceFolder = folders[0].uri;
        if (settings.useLabLinter) {
            diagnostics = runLabLinter(textDocument, settings, workspaceFolder);
            connection.sendDiagnostics({ uri: textDocument.uri, diagnostics });
            return;
        }
        else if (settings.aiName === "") {
            return;
        }
        //let loadfile = textDocument.uri.substring(7);
        // Script text
        let text = textDocument.getText();
        let filepath = vscode_uri_1.URI.parse(workspaceFolder).fsPath;
        connection.console.log("dir : " + filepath);
        // Get the errors
        let parser = new aiScriptParser_1.AiScriptParser(settings.aiName, workspaceFolder, aiScriptTypes);
        parser.parse();
        connection.console.log("file:\n" + parser.logger);
        let errors = parser.getErrors();
        let scopes = parser.getScopes();
        connection.console.log("" + Object.keys(scopes).length);
        Object.keys(scopes).forEach(scp => {
            connection.console.log(scopes[scp].filename);
        });
        connection.console.log("NumErrs: " + errors.length);
        // Define the diagnostic information
        errors.forEach(error => {
            // Assemble the error message
            let errMsg = error.message.long;
            if (error.severity === 1) {
                errMsg = "ERR" + error.code + ": " + errMsg;
            }
            else if (error.severity === 2) {
                errMsg = "WARN" + error.code + ": " + errMsg;
            }
            else if (error.severity === 3) {
                errMsg = "INFO: " + errMsg;
            }
            // Push append the new diagnostic
            diagnostics.push({
                severity: error.severity,
                code: error.code,
                range: { start: textDocument.positionAt(error.position.start),
                    end: textDocument.positionAt(error.position.stop) },
                message: errMsg,
                source: 'Aoe2AiScript'
            });
        });
        /*
    
        //let command_pattern: RegExp = /(\(\s*)\w[^\(\)]*(\".*\")*[^\(\)]*(?=\))/g;
        //let m: RegExpExecArray;
    
        while ((m = command_pattern.exec(text)) && problems < settings.maxErrorsReported) {
            connection.console.log(m.index + ": " + m.join('|'));
    
            let char = m.index;
            let isComment = false;
            while ((text[char--] !== "\n") && !isComment) {
                if (text[char] === ";")
                    isComment = true;
            }
            // Skip comments
            if (isComment) continue;
    
            // Search for matching command
            let test_str = m[0].slice(m[1].length,);
            //connection.console.log(test_str);
            let offset = m[0].length - test_str.length;
    
            // Replace strings with a single word, for ease of parsing
            test_str      = test_str.replace(/"[\s\S]*"/g, '"string"');
            let test_arr  = test_str.split(/\s+/g);
            let com_match = aiScriptPars[test_arr[0]];
            
            // Note the match
            let diagnostic: Diagnostic = undefined;
            if (com_match == undefined) {
                // Failure to find a match for the command
                diagnostic = {
                    severity: DiagnosticSeverity.Error,
                    range: {
                        start: textDocument.positionAt(m.index+offset),
                        end: textDocument.positionAt(m.index + offset + test_arr[0].length)
                    },
                    message: 'Unknown command: `'+test_arr[0]+'`',
                    source: 'Aoe2AiScript'
                };
                problems++;
            }
            // ... otherwise if no command is found, produce an error
            else {
                let diagnosic: Diagnostic = {
                    severity: DiagnosticSeverity.Warning,
                    range: {
                        start: textDocument.positionAt(m.index+offset),
                        end: textDocument.positionAt(m.index + m[0].length)
                    },
                    message: `${test_str}\n${com_match}`,
                    source: 'Aoe2AiScript'
                };
                if (hasDiagnosticRelatedInformationCapability) {
                    diagnosic.relatedInformation = [
                        {
                            location: {
                                uri: textDocument.uri,
                                range: Object.assign({}, diagnosic.range)
                            },
                            message: 'Spelling matters'
                        },
                        {
                            location: {
                                uri: textDocument.uri,
                                range: Object.assign({}, diagnosic.range)
                            },
                            message: 'Particularly for names'
                        }
                    ];
                }
            }
    
            if (diagnostic != undefined) {
                diagnostics.push(diagnostic);
            }
            
        }
        */
        // Send the computed diagnostics to VSCode.
        connection.sendDiagnostics({ uri: textDocument.uri, diagnostics });
    });
}
/**********************************************************************/ /**
 * Registers when a watched file has been changed
 * 	@param change			Parameters related to the watched file change
 **************************************************************************/
connection.onDidChangeWatchedFiles(_change => {
    // Monitored files have change in VSCode
    connection.console.log('We received a file change event');
});
/**********************************************************************/ /**
 * Provides the initial list of the completion items.
 * 	@param _textDocumentPosition	Document to be evaluated
 * 	@returns List of completion items (or [undefined] if completions are turned off)
 **************************************************************************/
connection.onCompletion((_textDocumentPosition) => {
    // The pass parameter contains the position of the text document in
    // which code complete got requested. We ignore this info and always
    // provide the same list of completion items.
    return getCompletions(_textDocumentPosition);
});
/**********************************************************************/ /**
 * Returns a list of completion items
 * 	@param textDocument		Document to be evaluated
 * 	@returns List of completion items (or [undefined] if completions are turned off)
 **************************************************************************/
function getCompletions(_textDocumentPosition) {
    return __awaiter(this, void 0, void 0, function* () {
        // Check if completions are turned on
        let settings = yield getDocumentSettings(_textDocumentPosition.textDocument.uri);
        if (settings.enableCompletionHelp) {
            let textDocument = documents.get(_textDocumentPosition.textDocument.uri);
            if (!textDocument) {
                return aiScriptCompletionList;
            }
            return contextualCompletionList(textDocument, _textDocumentPosition.position);
        }
        else {
            return undefined;
        }
    });
}
function lineBeforePosition(textDocument, position) {
    return textDocument.getText({
        start: { line: position.line, character: 0 },
        end: position
    });
}
function completionContextKind(textDocument, position) {
    let before = lineBeforePosition(textDocument, position);
    let filePath = vscode_uri_1.URI.parse(textDocument.uri).fsPath.toLowerCase();
    if (filePath.endsWith(".ai") && /\(\s*load(?:-random)?\b[^\)]*$/i.test(before)) {
        return "load-target";
    }
    if (/\(\s*up-target-(objects|point)\s+\S+\s+[^\)]*$/i.test(before)) {
        return "duc-action";
    }
    if (/\(\s*up-modify-sn\s+\S+\s+[^\)]*$/i.test(before)) {
        return "math-op";
    }
    let commandArg = currentCommandArgument(textDocument, position);
    if (commandArg && commandArg.paramType) {
        return "parameter";
    }
    if (/\(\s*(set-strategic-number|up-modify-sn|up-compare-sn)\s+[^\)]*$/i.test(before)) {
        return "strategic-number";
    }
    if (/\bc:\s*[A-Za-z0-9_-]*$/i.test(before)) {
        return "constant";
    }
    if (/\(\s*[#A-Za-z0-9_-]*$/i.test(before)) {
        return "command";
    }
    return "general";
}
function currentCommandArgument(textDocument, position) {
    let before = lineBeforePosition(textDocument, position).replace(/;.*$/, "");
    let openIndex = before.lastIndexOf("(");
    if (openIndex < 0) {
        return null;
    }
    let segment = before.slice(openIndex + 1);
    if (segment.indexOf(")") >= 0) {
        return null;
    }
    let commandMatch = /^([#A-Za-z0-9_-]+)([\s\S]*)$/.exec(segment);
    if (!commandMatch || !/\s/.test(commandMatch[2])) {
        return null;
    }
    let commandName = commandMatch[1];
    let rest = commandMatch[2];
    let trimmedRest = rest.trim();
    let tokenCount = trimmedRest ? trimmedRest.split(/\s+/).length : 0;
    let argIndex = /\s$/.test(rest) ? tokenCount : Math.max(0, tokenCount - 1);
    let params = labCommandParameters().get(commandName);
    if (!params || argIndex >= params.length) {
        return { commandName, argIndex, paramType: undefined };
    }
    return { commandName, argIndex, paramType: params[argIndex] };
}
function localDefconstCompletions(textDocument) {
    let text = textDocument.getText();
    let items = [];
    let labels = new Set();
    let pattern = /\(\s*defconst\s+([A-Za-z_][A-Za-z0-9_-]*)\b/g;
    let match;
    while ((match = pattern.exec(text)) !== null) {
        let label = match[1];
        if (labels.has(label)) {
            continue;
        }
        labels.add(label);
        items.push({
            label,
            detail: "local defconst",
            kind: vscode_languageserver_1.CompletionItemKind.Constant,
            sortText: "00-local-" + label,
            data: { labKind: "local-constant" }
        });
    }
    return items;
}
function completionPackageRoot(textDocument) {
    let filePath = vscode_uri_1.URI.parse(textDocument.uri).fsPath;
    try {
        let current = fs.existsSync(filePath) && fs.statSync(filePath).isDirectory() ? filePath : path.dirname(filePath);
        while (true) {
            let entries = fs.readdirSync(current);
            if (entries.some(entry => entry.toLowerCase().endsWith(".ai"))) {
                return current;
            }
            let parent = path.dirname(current);
            if (current === parent) {
                return path.dirname(filePath);
            }
            current = parent;
        }
    }
    catch (_error) {
        return path.dirname(filePath);
    }
}
function loadTargetCompletions(textDocument, position) {
    let root = completionPackageRoot(textDocument);
    let before = lineBeforePosition(textDocument, position);
    let insertQuoted = !/"[^"]*$/.test(before);
    let items = [];
    let stack = [root];
    let seen = 0;
    while (stack.length > 0 && seen < 500) {
        let current = stack.pop();
        let entries = [];
        try {
            entries = fs.readdirSync(current, { withFileTypes: true });
        }
        catch (_error) {
            continue;
        }
        entries.forEach(entry => {
            if (entry.name === ".git" || entry.name === "node_modules" || entry.name === ".tmp") {
                return;
            }
            let entryPath = path.join(current, entry.name);
            if (entry.isDirectory()) {
                stack.push(entryPath);
                return;
            }
            if (!entry.isFile() || !entry.name.toLowerCase().endsWith(".per")) {
                return;
            }
            seen++;
            let target = path.relative(root, entryPath).replace(/\\/g, "/").replace(/\.per$/i, "");
            items.push({
                label: target,
                insertText: insertQuoted ? "\"" + target + "\"" : target,
                detail: "package .per load target",
                kind: vscode_languageserver_1.CompletionItemKind.File,
                sortText: "00-load-" + target,
                data: { labKind: "load-target" }
            });
        });
    }
    return items;
}
function labKindForOriginalSection(section) {
    switch (section) {
        case "Action":
        case "Fact":
        case "FactAction":
        case "Control":
            return "command";
        case "StrategicNumber":
            return "strategic-number";
        case "BuildingId":
        case "BuildingClass":
        case "UnitId":
        case "UnitClass":
        case "UnitLine":
        case "UnitSet":
        case "WallId":
        case "WallLine":
            return "object";
        case "TechId":
            return "tech";
        default:
            return "value";
    }
}
function preferredKindsForParameter(paramType) {
    let normalized = String(paramType || "").toLowerCase();
    const valueFamilies = new Set([
        "age",
        "civ",
        "commodity",
        "difficulty",
        "factid",
        "gametype",
        "mapsize",
        "objectdata",
        "objectlist",
        "objectstatus",
        "placementtype",
        "playerstance",
        "positiontype",
        "researchstate",
        "resource",
        "resourcetype",
        "searchorder",
        "subgametype",
        "timerstate",
        "victorycondition"
    ]);
    if (normalized === "snid" || normalized === "strategicnumber") {
        return new Set(["strategic-number", "local-constant"]);
    }
    if (normalized === "ducaction") {
        return new Set(["duc-action"]);
    }
    if (normalized === "mathop") {
        return new Set(["math-op"]);
    }
    if (normalized === "compareop" || normalized === "typeop" || normalized === "relop") {
        return new Set(["compare-op", "math-op"]);
    }
    if (normalized === "unitid" || normalized === "buildingid" || normalized === "unitclass" || normalized === "buildingclass" || normalized === "objectid") {
        return new Set(["object", "local-constant"]);
    }
    if (normalized === "techid") {
        return new Set(["tech", "local-constant"]);
    }
    if (normalized === "formation") {
        return new Set(["formation"]);
    }
    if (normalized === "attackstance") {
        return new Set(["attack-stance"]);
    }
    if (normalized === "maptype") {
        return new Set(["map-type", "local-constant"]);
    }
    if (valueFamilies.has(normalized)) {
        return new Set([normalized, "local-constant"]);
    }
    if (normalized.indexOf("value") >= 0 || normalized.indexOf("goal") >= 0 || normalized.indexOf("option") >= 0) {
        return new Set(["value", "local-constant"]);
    }
    return new Set(["value", "local-constant"]);
}
function completionItemFamily(item) {
    let label = item.label || "";
    let labKind = item.data && item.data.labKind ? item.data.labKind : "";
    let detail = String(item.detail || "").toLowerCase();
    if (labKind === "local-constant") {
        return labKind;
    }
    let registryItem = labRegistryItemByLabel().get(label);
    if (registryItem && registryItem.detail && detail.indexOf(" value") < 0) {
        detail = String(registryItem.detail).toLowerCase();
    }
    if (detail.indexOf("ducaction") >= 0 || label.indexOf("action-") === 0) {
        return "duc-action";
    }
    if (detail.indexOf("mathop") >= 0 || /^([cgst]:)?(\+|-|\*|\/|max|min|mod|:=|=)$/.test(label) || /^c:[+\-*\/]/.test(label)) {
        return "math-op";
    }
    if (detail.indexOf("compareop") >= 0 || detail.indexOf("typeop") >= 0 || ["<", "<=", "==", "!=", ">=", ">", "c:", "g:", "s:", "t:"].indexOf(label) >= 0) {
        return "compare-op";
    }
    if (detail.indexOf("formation") >= 0) {
        return "formation";
    }
    if (detail.indexOf("attackstance") >= 0 || label.indexOf("stance-") === 0) {
        return "attack-stance";
    }
    if (detail.indexOf("maptype") >= 0) {
        return "map-type";
    }
    let valueFamilyMatch = /^([a-z]+) value$/.exec(detail);
    if (valueFamilyMatch) {
        return valueFamilyMatch[1].toLowerCase();
    }
    return labKind;
}
function contextualCompletionList(textDocument, position) {
    let contextKind = completionContextKind(textDocument, position);
    let dynamicItems = localDefconstCompletions(textDocument);
    if (contextKind === "load-target") {
        return { items: loadTargetCompletions(textDocument, position), isIncomplete: false };
    }
    let preferredKinds = {
        "command": new Set(["command"]),
        "strategic-number": new Set(["strategic-number"]),
        "duc-action": new Set(["duc-action"]),
        "math-op": new Set(["math-op"]),
        "constant": new Set(["object", "value", "tech", "strategic-number", "local-constant"]),
        "general": new Set(["local-constant"])
    }[contextKind] || new Set();
    let commandArg = currentCommandArgument(textDocument, position);
    if (commandArg && commandArg.paramType) {
        preferredKinds = preferredKindsForParameter(commandArg.paramType);
    }
    let items = dynamicItems.concat(aiScriptCompletionList.items).map(item => {
        let labKind = completionItemFamily(item);
        let cloned = Object.assign({}, item);
        let baseSort = item.sortText || item.label;
        cloned.sortText = (preferredKinds.has(labKind) ? "00-" : "90-") + baseSort;
        return cloned;
    });
    return { items, isIncomplete: false };
}
function labDiagnosticCode(diagnostic) {
    let code = diagnostic && diagnostic.code ? String(diagnostic.code) : "";
    return code.indexOf(":") >= 0 ? code.split(":").pop() : code;
}
function textForRange(textDocument, range) {
    return textDocument.getText(range).replace(/^["']|["']$/g, "");
}
function levenshteinDistance(left, right) {
    left = String(left || "");
    right = String(right || "");
    let previous = [];
    for (let j = 0; j <= right.length; j++) {
        previous[j] = j;
    }
    for (let i = 1; i <= left.length; i++) {
        let current = [i];
        for (let j = 1; j <= right.length; j++) {
            let cost = left[i - 1] === right[j - 1] ? 0 : 1;
            current[j] = Math.min(current[j - 1] + 1, previous[j] + 1, previous[j - 1] + cost);
        }
        previous = current;
    }
    return previous[right.length];
}
function closestRegistryLabels(token, kinds, limit) {
    let itemsByKind = labRegistryItemsByKind();
    let candidates = [];
    kinds.forEach(kind => {
        (itemsByKind.get(kind) || []).forEach(item => candidates.push(item.label));
    });
    let seen = new Set();
    return candidates
        .filter(label => {
        if (seen.has(label)) {
            return false;
        }
        seen.add(label);
        return true;
    })
        .map(label => ({ label, distance: levenshteinDistance(token.toLowerCase(), label.toLowerCase()) }))
        .sort((left, right) => left.distance - right.distance || left.label.localeCompare(right.label))
        .slice(0, limit)
        .map(item => item.label);
}
function registryLabelsByFamilies(families) {
    let wanted = new Set(families);
    let seen = new Set();
    let labels = [];
    loadLabRegistryItems().forEach(item => {
        if (!item.label || seen.has(item.label)) {
            return;
        }
        let family = completionItemFamily({
            label: item.label,
            detail: item.detail,
            data: { labKind: item.kind }
        });
        if (!wanted.has(family)) {
            return;
        }
        seen.add(item.label);
        labels.push(item.label);
    });
    return labels;
}
function closestRegistryLabelsByFamilies(token, families, limit) {
    return registryLabelsByFamilies(families)
        .map(label => ({ label, distance: levenshteinDistance(token.toLowerCase(), label.toLowerCase()) }))
        .sort((left, right) => left.distance - right.distance || left.label.localeCompare(right.label))
        .slice(0, limit)
        .map(item => item.label);
}
function replacementActionsForLabels(labels, textDocument, range, diagnostic) {
    return labels.map(label => replacementCodeAction("Replace with " + label, textDocument.uri, range, label, diagnostic));
}
function diagnosticReplacementFamilies(textDocument, diagnostic, code) {
    if (code === "undefined-strategic-number") {
        return new Set(["strategic-number"]);
    }
    let commandArg = currentCommandArgument(textDocument, diagnostic.range.start);
    if (commandArg && commandArg.paramType) {
        return preferredKindsForParameter(commandArg.paramType);
    }
    if (code === "undefined-constant" || code === "undefined-identifier" || code === "undefined-position-constant") {
        return new Set(["object", "tech", "value", "strategic-number"]);
    }
    return new Set();
}
function typeOpReplacementLabels(token) {
    let prefix = String(token || "").charAt(0).toLowerCase();
    let labels = ["c:", "g:", "s:"];
    if (labels.indexOf(prefix + ":") >= 0) {
        return [prefix + ":"].concat(labels.filter(label => label !== prefix + ":"));
    }
    return labels;
}
function mathOpReplacementLabels(token) {
    let prefix = String(token || "").charAt(0).toLowerCase();
    if (["c", "g", "s"].indexOf(prefix) < 0) {
        prefix = "c";
    }
    return [prefix + ":=", prefix + ":+", prefix + ":-"];
}
function replacementCodeAction(title, uri, range, newText, diagnostic) {
    return {
        title,
        kind: "quickfix",
        diagnostics: diagnostic ? [diagnostic] : [],
        edit: {
            changes: {
                [uri]: [{
                        range,
                        newText
                    }]
            }
        }
    };
}
function explanationCodeAction(code, diagnostic) {
    let explanation = labDiagnosticExplanations().get(code);
    if (!explanation) {
        return undefined;
    }
    return {
        title: "Explain " + code + ": " + explanation,
        kind: "quickfix",
        diagnostics: diagnostic ? [diagnostic] : [],
        command: {
            title: "Open diagnostic docs for " + code,
            command: "aoe2AiScript.openDiagnosticDocsPreview",
            arguments: [code]
        }
    };
}
function lineRemovalRange(textDocument, range) {
    let line = range.start.line;
    let nextLineText = textDocument.getText({
        start: { line, character: 0 },
        end: { line: line + 1, character: 0 }
    });
    if (nextLineText.length > 0) {
        return {
            start: { line, character: 0 },
            end: { line: line + 1, character: 0 }
        };
    }
    return {
        start: { line, character: 0 },
        end: { line, character: Number.MAX_SAFE_INTEGER }
    };
}
function codeActionsForDiagnostic(textDocument, diagnostic) {
    let code = labDiagnosticCode(diagnostic);
    let token = textForRange(textDocument, diagnostic.range);
    let actions = [];
    if (code === "missing-load-target") {
        loadTargetCompletions(textDocument, diagnostic.range.start).slice(0, 5).forEach(item => {
            actions.push(replacementCodeAction("Replace load target with " + item.label, textDocument.uri, diagnostic.range, item.label, diagnostic));
        });
    }
    else if (code === "undefined-strategic-number") {
        actions = actions.concat(replacementActionsForLabels(closestRegistryLabelsByFamilies(token, ["strategic-number"], 3), textDocument, diagnostic.range, diagnostic));
    }
    else if (code === "undefined-constant" || code === "undefined-identifier" || code === "undefined-position-constant") {
        let families = Array.from(diagnosticReplacementFamilies(textDocument, diagnostic, code)).filter(family => family !== "local-constant");
        actions = actions.concat(replacementActionsForLabels(closestRegistryLabelsByFamilies(token, families, 3), textDocument, diagnostic.range, diagnostic));
    }
    else if (code === "command-typed-prefix-mismatch") {
        actions = actions.concat(replacementActionsForLabels(typeOpReplacementLabels(token), textDocument, diagnostic.range, diagnostic));
    }
    else if (code === "command-argument-mismatch") {
        let families = Array.from(diagnosticReplacementFamilies(textDocument, diagnostic, code)).filter(family => family !== "local-constant");
        let labels = families.length === 1 && families[0] === "math-op" ? mathOpReplacementLabels(token) : closestRegistryLabelsByFamilies(token, families, 3);
        actions = actions.concat(replacementActionsForLabels(labels, textDocument, diagnostic.range, diagnostic));
    }
    else if (code === "redundant-built-in-defconst") {
        actions.push(replacementCodeAction("Remove redundant built-in defconst line", textDocument.uri, lineRemovalRange(textDocument, diagnostic.range), "", diagnostic));
    }
    else if (code === "command-role-mismatch") {
        actions.push(explanationCodeAction(code, diagnostic));
    }
    let explanation = explanationCodeAction(code, diagnostic);
    if (explanation && !actions.some(action => action && action.title === explanation.title)) {
        actions.push(explanation);
    }
    return actions.filter(action => action !== undefined);
}
connection.onCodeAction((params) => {
    let textDocument = documents.get(params.textDocument.uri);
    if (!textDocument) {
        return [];
    }
    let actions = [];
    (params.context.diagnostics || []).forEach(diagnostic => {
        actions = actions.concat(codeActionsForDiagnostic(textDocument, diagnostic));
    });
    return actions;
});
function positionAtTextOffset(text, offset) {
    let line = 0;
    let character = 0;
    for (let index = 0; index < offset; index++) {
        if (text[index] === "\n") {
            line++;
            character = 0;
        }
        else if (text[index] !== "\r") {
            character++;
        }
    }
    return { line, character };
}
function locationForTextOffset(uri, text, startOffset, length) {
    let start = positionAtTextOffset(text, startOffset);
    let end = positionAtTextOffset(text, startOffset + length);
    return {
        uri,
        range: { start, end }
    };
}
function wordAtPosition(textDocument, position) {
    let line = textDocument.getText({
        start: { line: position.line, character: 0 },
        end: { line: position.line, character: 10000 }
    });
    let tokenPattern = /[#A-Za-z_][#A-Za-z0-9_-]*/g;
    let match;
    while ((match = tokenPattern.exec(line)) !== null) {
        if (position.character >= match.index && position.character <= match.index + match[0].length) {
            return match[0];
        }
    }
    return undefined;
}
function loadTargetAtPosition(textDocument, position) {
    let line = textDocument.getText({
        start: { line: position.line, character: 0 },
        end: { line: position.line, character: 10000 }
    });
    if (!/\(\s*load(?:-random)?\b/i.test(line)) {
        return undefined;
    }
    let loadPattern = /"([^"]+)"/g;
    let match;
    while ((match = loadPattern.exec(line)) !== null) {
        let targetStart = match.index + match[0].lastIndexOf(match[1]);
        let targetEnd = targetStart + match[1].length;
        if (position.character >= targetStart && position.character <= targetEnd) {
            return match[1];
        }
    }
    return undefined;
}
function resolveLoadTarget(textDocument, target) {
    let currentPath = vscode_uri_1.URI.parse(textDocument.uri).fsPath;
    let root = completionPackageRoot(textDocument);
    let candidates = [
        path.resolve(path.dirname(currentPath), target + ".per"),
        path.resolve(root, target + ".per")
    ];
    for (let index = 0; index < candidates.length; index++) {
        if (fs.existsSync(candidates[index])) {
            return {
                uri: vscode_uri_1.URI.file(candidates[index]).toString(),
                range: {
                    start: { line: 0, character: 0 },
                    end: { line: 0, character: 0 }
                }
            };
        }
    }
    return undefined;
}
function defconstLocationInText(uri, text, token) {
    let escaped = token.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    let pattern = new RegExp("\\(\\s*defconst\\s+(" + escaped + ")\\b", "g");
    let match = pattern.exec(text);
    if (!match) {
        return undefined;
    }
    let startOffset = match.index + match[0].lastIndexOf(match[1]);
    return locationForTextOffset(uri, text, startOffset, token.length);
}
function packagePerFiles(textDocument) {
    let root = completionPackageRoot(textDocument);
    let files = [];
    let stack = [root];
    let visited = 0;
    while (stack.length > 0 && visited < 500) {
        let current = stack.pop();
        let entries = [];
        try {
            entries = fs.readdirSync(current, { withFileTypes: true });
        }
        catch (_error) {
            continue;
        }
        entries.forEach(entry => {
            if (entry.name === ".git" || entry.name === "node_modules" || entry.name === ".tmp") {
                return;
            }
            let entryPath = path.join(current, entry.name);
            if (entry.isDirectory()) {
                stack.push(entryPath);
                return;
            }
            if (entry.isFile() && entry.name.toLowerCase().endsWith(".per")) {
                visited++;
                files.push(entryPath);
            }
        });
    }
    return files;
}
function localDefconstDefinition(textDocument, token) {
    let currentLocation = defconstLocationInText(textDocument.uri, textDocument.getText(), token);
    if (currentLocation) {
        return currentLocation;
    }
    let currentPath = normalizeFsPath(vscode_uri_1.URI.parse(textDocument.uri).fsPath);
    let files = packagePerFiles(textDocument);
    for (let index = 0; index < files.length; index++) {
        if (normalizeFsPath(files[index]) === currentPath) {
            continue;
        }
        let text = "";
        try {
            text = fs.readFileSync(files[index], "utf8");
        }
        catch (_error) {
            continue;
        }
        let location = defconstLocationInText(vscode_uri_1.URI.file(files[index]).toString(), text, token);
        if (location) {
            return location;
        }
    }
    return undefined;
}
function symbolReferencePath(labPath) {
    return path.resolve(labPath, "docs", "reference", "generated", "ai-symbol-reference.md");
}
function symbolDocPath(labPath, token) {
    return path.resolve(labPath, "docs", "reference", "generated", "symbols", token.replace(/[^#A-Za-z0-9_-]+/g, "_") + ".md");
}
function markdownAnchor(token) {
    return "symbol-" + token.toLowerCase().replace(/[^#a-z0-9_-]+/g, "-");
}
function labRegistryDefinition(token, labPath) {
    if (!labRegistryHovers().has(token)) {
        return undefined;
    }
    let docsPath = symbolReferencePath(labPath);
    let text = "";
    if (fs.existsSync(docsPath)) {
        try {
            text = fs.readFileSync(docsPath, "utf8");
        }
        catch (_error) {
            text = "";
        }
        let escaped = token.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
        let match = new RegExp("^## `" + escaped + "`", "m").exec(text);
        if (match) {
            let tokenOffset = match.index + match[0].indexOf(token);
            return locationForTextOffset(vscode_uri_1.URI.file(docsPath).with({ fragment: markdownAnchor(token) }).toString(), text, tokenOffset, token.length);
        }
    }
    let symbolPath = symbolDocPath(labPath, token);
    if (fs.existsSync(symbolPath)) {
        return {
            uri: vscode_uri_1.URI.file(symbolPath).toString(),
            range: {
                start: { line: 0, character: 0 },
                end: { line: 0, character: 0 }
            }
        };
    }
    return undefined;
}
function getDefinition(params) {
    return __awaiter(this, void 0, void 0, function* () {
        let textDocument = documents.get(params.textDocument.uri);
        if (!textDocument) {
            return undefined;
        }
        let loadTarget = loadTargetAtPosition(textDocument, params.position);
        if (loadTarget) {
            return resolveLoadTarget(textDocument, loadTarget);
        }
        let token = wordAtPosition(textDocument, params.position);
        if (!token) {
            return undefined;
        }
        let defconstLocation = localDefconstDefinition(textDocument, token);
        if (defconstLocation) {
            return defconstLocation;
        }
        let settings = yield getDocumentSettings(params.textDocument.uri);
        let folders = yield connection.workspace.getWorkspaceFolders();
        let workspaceFolder = folders && folders.length > 0 ? vscode_uri_1.URI.parse(folders[0].uri).fsPath : process.cwd();
        let labPath = settings.labPath || bundledLabPath() || workspaceFolder;
        return labRegistryDefinition(token, labPath);
    });
}
connection.onDefinition((params) => {
    return getDefinition(params);
});
connection.onRequest("textDocument/declaration", (params) => {
    return getDefinition(params);
});
/**********************************************************************/ /**
 * Returns a Hover item based on the current document position
 * 	@param textDocPos		Position in current document (line & char)
 * 	@returns A single Hover item
 **************************************************************************/
connection.onHover((textDocPos) => {
    return getHover(textDocPos);
});
/**********************************************************************/ /**
 * Returns a Hover item based on the current document position
 * 	@param textDocPos		Position in current document (line & char)
 * 	@returns A single Hover item
 *
 * Based on the current position of the cursor, this method returns a Hover
 * object to be displayed. If the item is not in the list of AoE2 script
 * parameters or HoverHelp is not enabled, an [undefined] is returned
 * resulting in nothing being displayed.
 **************************************************************************/
function getHover(textDocPos) {
    return __awaiter(this, void 0, void 0, function* () {
        // Make sure hover text is requested
        let settings = yield getDocumentSettings(textDocPos.textDocument.uri);
        if (settings.enableHoverHelp === false) {
            return undefined;
        }
        // Need to get the word that we're hovering over
        let hoverWord = "**Line:** " + textDocPos.position.line + "\n";
        "**Char:** " + textDocPos.position.character;
        // Define the signature to be returned
        let hover = undefined;
        // Get the document position
        let line = textDocPos.position.line;
        let col = textDocPos.position.character;
        // Get the range of the current line
        let line_range = {
            start: { line: line, character: 0 },
            end: { line: line, character: 10000 }
        };
        // An AiScript command is defined as: (commandName par1 par2 <etc...>)
        // We need to get all of the text back to the nearest '(' and up to the
        // cursor position
        let text = documents.get(textDocPos.textDocument.uri);
        let line_text = text.getText(line_range).trimRight();
        // Skip if we're hovering inside a comment
        let comment_regex = /;/g;
        if (comment_regex.test(line_text.substr(0, col))) {
            hover = undefined;
        }
        // ... otherwise get the string
        else {
            // Loop until we have the end of the current command/parameter name.
            // This helps to identify what command or parameter we're looking at
            let word_end = /(\s+|\(|\)|\n|;)$/g;
            while ((!word_end.test(line_text.substr(0, ++col))) && (col <= line_text.length)) {
                // If there are a rediculous number of characters, there's a problem
                if (col > 1000) {
                    connection.console.error("Command is unreasonably long...");
                    return undefined;
                }
            }
            // Update the text
            line_text = line_text.substr(0, col - 1);
            // Now get only the text from the closest '(' until the end
            //let word_begin      = /(\s|\()[a-zA-Z0-9-:<>*\/+]+(\s|\)|\n|;)$/g;
            let word_begin = /(\(|\s|^)[^\(\s]+$/g;
            let hover_txt_array = word_begin.exec(line_text);
            let hover_txt = "";
            // Handle the case where the object doesn't begin with a '('
            if (hover_txt_array === null) {
                return undefined;
            }
            else {
                hover_txt = hover_txt_array[0];
                if (/(\(|\s)/g.test(hover_txt))
                    hover_txt = hover_txt.substr(1);
            }
            hover = labRegistryHover(hover_txt);
            if (hover !== undefined) {
                return hover;
            }
            // Search for command
            let hover_par = undefined;
            Object.keys(aiScriptTypes).forEach(typekey => {
                if (hover_par === undefined) {
                    hover_par = aiScriptTypes[typekey].values[hover_txt];
                }
            });
            if (hover_par !== undefined) {
                // Generate the output hover text
                let hover_str = "(" + hover_par.section + ") " + hover_par.label +
                    "\n\n" + hover_par.description;
                // Initialize the signature object
                hover = {
                    contents: { kind: 'markdown', value: hover_str }
                };
            }
        }
        // Return the signature
        return hover;
    });
}
/**********************************************************************/ /**
 * Provides parameter information when typing an action or fact
 * 	@param textDocPos		Position of cursor in current document
 * 	@returns List of a single Hover item
 *
 * Based on the current position of the cursor, this method returns a Hover
 * object to be displayed. If the item is not in the list of AoE2 script
 * parameters or HoverHelp is not enabled, an [undefined] is returned
 * resulting in nothing being displayed.
 **************************************************************************/
connection.onSignatureHelp((textDocPos) => {
    return getSignatureHelp(textDocPos);
});
function labCommandSyntax(item) {
    if (!item || !item.documentation) {
        return undefined;
    }
    let match = /Syntax:\s*`([^`]+)`/.exec(item.documentation);
    return match ? match[1] : undefined;
}
function labSignatureParameters(label) {
    let parameters = [];
    let pattern = /<[^>]+>/g;
    let match;
    while ((match = pattern.exec(label)) !== null) {
        parameters.push({
            label: [match.index, match.index + match[0].length],
            documentation: {
                value: match[0],
                kind: 'markdown'
            }
        });
    }
    return parameters;
}
function labSignatureDocumentation(item, settings) {
    if (settings.enableParameterHelp !== "full" || !item.documentation) {
        return { value: "", kind: 'markdown' };
    }
    return {
        value: item.documentation,
        kind: 'markdown'
    };
}
function labRegistrySignatureHelp(textDocument, position, settings) {
    let commandArg = currentCommandArgument(textDocument, position);
    if (!commandArg || !commandArg.commandName) {
        return undefined;
    }
    let item = labCommandItems().get(commandArg.commandName);
    let label = labCommandSyntax(item);
    if (!item || !label) {
        return undefined;
    }
    let parameters = labSignatureParameters(label);
    return {
        signatures: [{
                label,
                documentation: labSignatureDocumentation(item, settings),
                parameters
            }],
        activeSignature: 0,
        activeParameter: Math.max(0, Math.min(commandArg.argIndex, Math.max(0, parameters.length - 1)))
    };
}
/**********************************************************************/ /**
 * Get the signature help in an asynchronous way
 * 	@param textDocPos		Current line/character of cursor in document
 * 	@returns List of a single Hover item
 *
 * Based on the current position of the cursor, this method returns a
 * SignatureHelp object to be displayed. If the item is not in the list of
 * AoE2 script parameters or HoverHelp is not enabled, an [undefined] is
 * returned resulting in nothing being displayed.
 **************************************************************************/
function getSignatureHelp(textDocPos) {
    return __awaiter(this, void 0, void 0, function* () {
        // Make sure we actually want parameter help
        let settings = yield getDocumentSettings(textDocPos.textDocument.uri);
        if (settings.enableParameterHelp === "off") {
            return undefined;
        }
        let text = documents.get(textDocPos.textDocument.uri);
        if (text) {
            let labSignature = labRegistrySignatureHelp(text, textDocPos.position, settings);
            if (labSignature !== undefined) {
                return labSignature;
            }
        }
        else {
            return undefined;
        }
        // Define the signature to be returned
        let signature = undefined;
        // Get the document position
        let line = textDocPos.position.line;
        let col = textDocPos.position.character;
        let line_range = {
            start: { line: line, character: 0 },
            end: { line: line, character: col }
        };
        // An AiScript command is defined as: (commandName par1 par2 <etc...>)
        // We need to get all of the text back to the nearest '(' and up to the
        // cursor position
        let line_text = text.getText(line_range);
        // Skip if we're in an ignorable situation. This is defined here as
        // any situation such as:
        //		'(' : An opening bracket with nothing beyond it
        //		')' : A closing bracket with nothing beyond it
        //		';'   : Identifies that a comment exists somewhere in the string
        // For the cases involving a bracket, we also catch the situation
        // where there is an indeterminate number of spaces after it.
        let ignore_signature_regex = /(\(|\))(\s*)$|;/g;
        if (ignore_signature_regex.test(line_text)) {
            signature = undefined;
        }
        // ... otherwise get the string
        else {
            // Loop until we have the end of the current command/parameter name.
            // This helps to identify what command or parameter we're looking at
            let signature_end = /(\s+|\(|\)|\n|;)$/g;
            while (!signature_end.test(line_text)) {
                line_range.end.character++;
                // If there are a rediculous number of characters, there's a problem
                if (line_range.end.character - col > 1000) {
                    connection.console.error("Command is unreasonably long...");
                    return undefined;
                }
                // Update the text
                line_text = text.getText(line_range);
            }
            // Trim undesired characters from end if they exist
            if (line_text.length > col) {
                line_text = line_text.slice(0, line_text.length - 1);
            }
            // Now get only the text from the closest '(' or '#' until the end
            let command_text_array = /[#\(][^\(]+$/g.exec(line_text);
            // Handle the case where an appropriate beginning wasn't found
            if (command_text_array === null) {
                return undefined;
            }
            // Extract the command name and current parameter index
            let command_text = command_text_array[0];
            if (command_text[0] == "(") {
                command_text = command_text.substr(1); // trim leading '('
            }
            let command_pars = command_text.split(/\s+/g);
            let command_str = command_pars[0]; // Command name
            let par_indx = command_pars.length - 2; // Parameter index at cursor
            // Search for command in the Fact, Action, and FactAction types
            let command = aiScriptTypes["Control"].values[command_str];
            if (command === undefined)
                command = aiScriptTypes["Fact"].values[command_str];
            if (command === undefined)
                command = aiScriptTypes["Action"].values[command_str];
            if (command === undefined)
                command = aiScriptTypes["FactAction"].values[command_str];
            // If the comand was found ...
            if (command !== undefined) {
                // Add the command type to the command definition
                command_str = "(" + command.section + ") " + command_str;
                // Load the parameters with descriptions
                let par_info = [];
                let offset = command_str.length + 1;
                command.pars.forEach(par => {
                    command_str += " " + par.type;
                    par_info.push({
                        label: [offset, offset + par.type.length],
                        documentation: {
                            value: "**" + par.type + ":** *" + par.note + "*",
                            kind: 'markdown'
                        }
                    });
                    offset += par.type.length + 1;
                });
                let descrip = { value: "", kind: 'markdown' };
                if (settings.enableParameterHelp === "full") {
                    descrip.value = "\n----\n**Command Description**  \n" + command.description;
                }
                // Initialize the signature object
                signature = {
                    signatures: [{
                            label: command_str,
                            documentation: descrip,
                            parameters: par_info
                        }],
                    activeSignature: 0,
                    activeParameter: par_indx
                };
            }
        }
        // Return the signature
        return signature;
    });
}
;
/*
connection.onDidOpenTextDocument((params) => {
    // A text document got opened in VSCode.
    // params.uri uniquely identifies the document. For documents store on disk this is a file URI.
    // params.text the initial full content of the document.
    connection.console.log(`${params.textDocument.uri} opened.`);
});
connection.onDidChangeTextDocument((params) => {
    // The content of a text document did change in VSCode.
    // params.uri uniquely identifies the document.
    // params.contentChanges describe the content changes to the document.
    connection.console.log(`${params.textDocument.uri} changed: ${JSON.stringify(params.contentChanges)}`);
});
connection.onDidCloseTextDocument((params) => {
    // A text document got closed in VSCode.
    // params.uri uniquely identifies the document.
    connection.console.log(`${params.textDocument.uri} closed.`);
});
*/
/**********************************************************************/ /**
 * Make the text document manager listen on the connection for open, change,
 * and close text document events
 **************************************************************************/
documents.listen(connection);
/**********************************************************************/ /**
 * Listen on the connection
 **************************************************************************/
connection.listen();
/*******************************************************************/ /**
 * Fill and register the completion objects
 ***********************************************************************/
function fillCompletions() {
    // Delete any stored completions
    while (aiScriptCompletionList.items.length > 0) {
        aiScriptCompletionList.items.pop();
    }
    if (aiScriptCompletionList.items.length === 0) {
        let existingLabels = new Set();
        // Loop through all Types
        Object.keys(aiScriptTypes).forEach(typeName => {
            let type = aiScriptTypes[typeName];
            // Loop through all parameters of this type
            Object.keys(type.values).forEach(parName => {
                let par = type.values[parName];
                // Construct a detailed call signature
                let detail = "(" + par.section + ") " + par.label;
                if (par.pars !== undefined) {
                    par.pars.forEach(p => {
                        detail += " " + p.type;
                    });
                }
                // Define a new completion item
                let item = {
                    label: par.label,
                    documentation: {
                        value: par.description,
                        kind: 'markdown'
                    },
                    detail: detail,
                    data: { labKind: labKindForOriginalSection(par.section) }
                };
                // Define the parameter kind (determines which icon is next to the 
                // suggestion in the popup list)
                switch (par.section) {
                    case "BuildingId":
                    case "BuildingClass":
                    case "WallId":
                    case "WallLine":
                        item.kind = vscode_languageserver_1.CompletionItemKind.Struct;
                        break;
                    case "UnitId":
                    case "UnitClass":
                    case "UnitLine":
                    case "UnitSet":
                        item.kind = vscode_languageserver_1.CompletionItemKind.Unit;
                        break;
                    case "Action":
                    case "FactAction":
                        item.kind = vscode_languageserver_1.CompletionItemKind.Method;
                        break;
                    case "Fact":
                        item.kind = vscode_languageserver_1.CompletionItemKind.Variable;
                        break;
                    case "TechId":
                        item.kind = vscode_languageserver_1.CompletionItemKind.Class;
                        break;
                    case "AgeId":
                        item.kind = vscode_languageserver_1.CompletionItemKind.Enum;
                        break;
                    case "RelOp":
                    case "UpRelOp":
                    case "TypeOp":
                    case "MathOp":
                        item.kind = vscode_languageserver_1.CompletionItemKind.Operator;
                        break;
                    case "Control":
                        item.kind = vscode_languageserver_1.CompletionItemKind.Interface;
                        break;
                    default:
                        item.kind = vscode_languageserver_1.CompletionItemKind.Module;
                        break;
                }
                // Append the new completion item
                aiScriptCompletionList.items.push(item);
                existingLabels.add(item.label);
                // Add an entry for alternative labels, i.e. for Civs
                if (par.altLabel !== undefined) {
                    let altItem = Object.assign({}, item, { label: par.altLabel });
                    aiScriptCompletionList.items.push(altItem);
                    existingLabels.add(altItem.label);
                }
            });
        });
        addLabRegistryCompletions(existingLabels);
    } // end-if
}
//# sourceMappingURL=server.js.map
