import { fork } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import {
  createMessageConnection,
  IPCMessageReader,
  IPCMessageWriter,
  NullLogger,
} from "../extensions/aoe2-aiscript-cursor-local-lab/languageExtension/node_modules/vscode-jsonrpc/lib/main.js";

const repoRoot = process.cwd();
const extensionRoot = path.join(repoRoot, "extensions", "aoe2-aiscript-cursor-local-lab");
const serverPath = path.join(extensionRoot, "languageExtension", "out", "server.js");
const fixtureRoot = path.join(repoRoot, ".tmp", "cursor-completion-smoke");

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

function fileUri(filePath) {
  return pathToFileURL(filePath).href;
}

function fixtureWithCursors(text) {
  const positions = {};
  const lines = [];
  text.split(/\n/).forEach((lineText, line) => {
    const match = /\|([A-Za-z0-9_-]+)\|/.exec(lineText);
    if (!match) {
      lines.push(lineText);
      return;
    }
    positions[match[1]] = { line, character: match.index };
    lines.push(lineText.slice(0, match.index) + lineText.slice(match.index + match[0].length));
  });
  return { text: lines.join("\n"), positions };
}

function rangeOf(text, needle) {
  const lines = text.split(/\n/);
  const line = lines.findIndex((value) => value.includes(needle));
  assert(line >= 0, `missing fixture token ${needle}`);
  const character = lines[line].indexOf(needle);
  return {
    start: { line, character },
    end: { line, character: character + needle.length },
  };
}

function completionItems(result) {
  if (!result) {
    return [];
  }
  const items = Array.isArray(result) ? result : result.items || [];
  return items.slice().sort((left, right) => {
    const leftSort = left.sortText || left.label || "";
    const rightSort = right.sortText || right.label || "";
    return leftSort.localeCompare(rightSort) || String(left.label || "").localeCompare(String(right.label || ""));
  });
}

function assertRanked(items, expected, limit, label) {
  const labels = items.slice(0, limit).map((item) => item.label);
  const expectedIndex = items.findIndex((item) => item.label === expected);
  const expectedItem = expectedIndex >= 0 ? items[expectedIndex] : undefined;
  assert(
    labels.includes(expected),
    `${label}: expected ${expected} in top ${limit}, found at ${expectedIndex}, sortText ${expectedItem && expectedItem.sortText}, saw ${labels.slice(0, 20).join(", ")}`
  );
}

function parameterText(signature, parameter) {
  if (!parameter) {
    return "";
  }
  if (Array.isArray(parameter.label)) {
    return signature.label.slice(parameter.label[0], parameter.label[1]);
  }
  return String(parameter.label || "");
}

function assertSignature(result, expectedLabel, expectedParameter, label) {
  assert(result && result.signatures && result.signatures.length > 0, `${label}: missing signature help`);
  const signature = result.signatures[result.activeSignature || 0];
  const activeParameter = signature.parameters[result.activeParameter || 0];
  assert(
    signature.label === expectedLabel,
    `${label}: expected signature ${expectedLabel}, saw ${signature.label}`
  );
  assert(
    parameterText(signature, activeParameter) === expectedParameter,
    `${label}: expected active parameter ${expectedParameter}, saw ${parameterText(signature, activeParameter)}`
  );
}

function assertCodeAction(result, expectedTitle, label) {
  const titles = (result || []).map((item) => item.title);
  assert(
    titles.includes(expectedTitle),
    `${label}: expected code action ${expectedTitle}, saw ${titles.join(", ")}`
  );
}

function assertCodeActionPrefix(result, expectedPrefix, label) {
  const titles = (result || []).map((item) => item.title);
  assert(
    titles.some((title) => title.startsWith(expectedPrefix)),
    `${label}: expected code action prefix ${expectedPrefix}, saw ${titles.join(", ")}`
  );
}

function assertNoCodeAction(result, unexpectedTitle, label) {
  const titles = (result || []).map((item) => item.title);
  assert(
    !titles.includes(unexpectedTitle),
    `${label}: did not expect code action ${unexpectedTitle}, saw ${titles.join(", ")}`
  );
}

function assertDefinition(result, expectedSuffix, label) {
  const locations = Array.isArray(result) ? result : (result ? [result] : []);
  assert(locations.length > 0, `${label}: expected a definition location`);
  const uri = String(locations[0].uri || "").replace(/\\/g, "/");
  assert(
    uri.endsWith(expectedSuffix.replace(/\\/g, "/")),
    `${label}: expected definition uri to end with ${expectedSuffix}, saw ${locations[0].uri}`
  );
}

async function requestWithTimeout(promise, label, timeoutMs = 10000) {
  let timeout;
  try {
    return await Promise.race([
      promise,
      new Promise((_, reject) => {
        timeout = setTimeout(() => reject(new Error(`${label} timed out`)), timeoutMs);
      }),
    ]);
  } finally {
    clearTimeout(timeout);
  }
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

fs.rmSync(fixtureRoot, { recursive: true, force: true });
fs.mkdirSync(path.join(fixtureRoot, "shared"), { recursive: true });

const perFixture = fixtureWithCursors([
  "(defconst local-probe 123)",
  '(include "shared/debug|includeTarget|.xs")',
  "(defrule",
  "    (true)",
  "    (map-type |mapType|)",
  "    (difficulty == |difficulty|)",
  "    (starting-age == |age|)",
  "    (resource-found |resource|)",
  "=>",
  "    (up-find-local c: |findLocal|)",
  "    (up-find-local g:= villager-class c: 1)",
  "    (up-target-objects 0 |targetObjects|)",
  "    (up-target-objects 0 action-gathr -1 -1)",
  "    (up-modify-sn sn-maximum-town-size |modifySn|)",
  "    (up-modify-sn sn-maximum-town-size c:: 1)",
  "    (set-strategic-number sn-maximum-town-siz 1)",
  "    (defconst villager-class 999)",
  "    (chat-to-all local-|localConst|)",
  ")",
  "",
].join("\n"));
const aiFixture = fixtureWithCursors('(load "|loadTarget|")\n(load-random 50 "shared/helper" 50 "shared/sec|loadRandomSecond|ond")\n(load "missing-target")\n');
const perText = perFixture.text;
const aiText = aiFixture.text;

const perPath = path.join(fixtureRoot, "main.per");
const aiPath = path.join(fixtureRoot, "smoke.ai");
fs.writeFileSync(perPath, perText, "utf8");
fs.writeFileSync(aiPath, aiText, "utf8");
fs.writeFileSync(path.join(fixtureRoot, "shared", "helper.per"), "(defrule (true) =>)\n", "utf8");
fs.writeFileSync(path.join(fixtureRoot, "shared", "second.per"), "(defrule (true) =>)\n", "utf8");
fs.writeFileSync(path.join(fixtureRoot, "shared", "debug.xs"), "void debug() {}\n", "utf8");

const child = fork(serverPath, ["--node-ipc"], {
  cwd: extensionRoot,
  execArgv: [],
  stdio: ["pipe", "pipe", "pipe", "ipc"],
});

const connection = createMessageConnection(
  new IPCMessageReader(child),
  new IPCMessageWriter(child),
  NullLogger
);

connection.onNotification("window/logMessage", () => {});
connection.onNotification("telemetry/event", () => {});
connection.onRequest("client/registerCapability", () => null);
connection.listen();

try {
  await requestWithTimeout(
    connection.sendRequest("initialize", {
      processId: process.pid,
      rootUri: fileUri(fixtureRoot),
      workspaceFolders: [{ uri: fileUri(fixtureRoot), name: "cursor-completion-smoke" }],
      capabilities: {},
    }),
    "initialize"
  );
  connection.sendNotification("initialized", {});
  connection.sendNotification("workspace/didChangeConfiguration", {
    settings: {
      aoe2_AiScript: {
        enableCompletionHelp: true,
        enableHoverHelp: true,
        enableParameterHelp: "parametersOnly",
        updateErrorsWhen: "never",
        maxErrorsReported: 100,
        useLabLinter: false,
        usePackageLint: false,
        labPath: repoRoot,
        pythonPath: "python",
      },
    },
  });

  connection.sendNotification("textDocument/didOpen", {
    textDocument: {
      uri: fileUri(perPath),
      languageId: "aoe2aiscript",
      version: 1,
      text: perText,
    },
  });
  connection.sendNotification("textDocument/didOpen", {
    textDocument: {
      uri: fileUri(aiPath),
      languageId: "aoe2aiscript",
      version: 1,
      text: aiText,
    },
  });

  await sleep(100);

  const cases = [
    {
      name: "map-type argument",
      uri: fileUri(perPath),
      position: perFixture.positions.mapType,
      expected: "acclivity",
      limit: 30,
    },
    {
      name: "difficulty argument",
      uri: fileUri(perPath),
      position: perFixture.positions.difficulty,
      expected: "extreme",
      limit: 20,
    },
    {
      name: "age argument",
      uri: fileUri(perPath),
      position: perFixture.positions.age,
      expected: "post-imperial-age",
      limit: 20,
    },
    {
      name: "resource argument",
      uri: fileUri(perPath),
      position: perFixture.positions.resource,
      expected: "boar-hunting",
      limit: 20,
    },
    {
      name: "up-find-local object argument",
      uri: fileUri(perPath),
      position: perFixture.positions.findLocal,
      expected: "villager-class",
      limit: 20,
    },
    {
      name: "up-target-objects DUC action argument",
      uri: fileUri(perPath),
      position: perFixture.positions.targetObjects,
      expected: "action-gather",
      limit: 40,
    },
    {
      name: "up-modify-sn math-op argument",
      uri: fileUri(perPath),
      position: perFixture.positions.modifySn,
      expected: "c:+",
      limit: 40,
    },
    {
      name: "local defconst completion",
      uri: fileUri(perPath),
      position: perFixture.positions.localConst,
      expected: "local-probe",
      limit: 20,
    },
    {
      name: ".ai load target completion",
      uri: fileUri(aiPath),
      position: aiFixture.positions.loadTarget,
      expected: "shared/helper",
      limit: 20,
    },
  ];

  for (const testCase of cases) {
    const result = await requestWithTimeout(
      connection.sendRequest("textDocument/completion", {
        textDocument: { uri: testCase.uri },
        position: testCase.position,
      }),
      testCase.name
    );
    assertRanked(completionItems(result), testCase.expected, testCase.limit, testCase.name);
  }

  const signatureCases = [
    {
      name: "up-find-local signature help",
      uri: fileUri(perPath),
      position: perFixture.positions.findLocal,
      expectedLabel: "(up-find-local <typeOp> <UnitId> <typeOp> <Value>)",
      expectedParameter: "<UnitId>",
    },
    {
      name: "up-target-objects signature help",
      uri: fileUri(perPath),
      position: perFixture.positions.targetObjects,
      expectedLabel: "(up-target-objects <Option> <DUCAction> <Formation> <AttackStance>)",
      expectedParameter: "<DUCAction>",
    },
    {
      name: "up-modify-sn signature help",
      uri: fileUri(perPath),
      position: perFixture.positions.modifySn,
      expectedLabel: "(up-modify-sn <SnId> <mathOp> <Value>)",
      expectedParameter: "<mathOp>",
    },
  ];

  for (const testCase of signatureCases) {
    const result = await requestWithTimeout(
      connection.sendRequest("textDocument/signatureHelp", {
        textDocument: { uri: testCase.uri },
        position: testCase.position,
      }),
      testCase.name
    );
    assertSignature(result, testCase.expectedLabel, testCase.expectedParameter, testCase.name);
  }

  const definitionCases = [
    {
      name: ".ai load-random target definition",
      uri: fileUri(aiPath),
      position: aiFixture.positions.loadRandomSecond,
      expectedSuffix: "shared/second.per",
    },
    {
      name: ".per include target definition",
      uri: fileUri(perPath),
      position: perFixture.positions.includeTarget,
      expectedSuffix: "shared/debug.xs",
    },
  ];

  for (const testCase of definitionCases) {
    const result = await requestWithTimeout(
      connection.sendRequest("textDocument/definition", {
        textDocument: { uri: testCase.uri },
        position: testCase.position,
      }),
      testCase.name
    );
    assertDefinition(result, testCase.expectedSuffix, testCase.name);
  }

  const codeActionCases = [
    {
      name: "missing load target code action",
      uri: fileUri(aiPath),
      range: rangeOf(aiText, "missing-target"),
      diagnostic: {
        range: rangeOf(aiText, "missing-target"),
        code: "error:missing-load-target",
        message: "'missing-target' does not resolve to a reachable .per file",
        source: "aoe2-ai-lab",
      },
      expectedTitle: "Replace load target with shared/helper",
    },
    {
      name: "undefined strategic number code action",
      uri: fileUri(perPath),
      range: rangeOf(perText, "sn-maximum-town-siz"),
      diagnostic: {
        range: rangeOf(perText, "sn-maximum-town-siz"),
        code: "error:undefined-strategic-number",
        message: "'sn-maximum-town-siz' is used as a strategic number but is not defined with defconst",
        source: "aoe2-ai-lab",
      },
      expectedTitle: "Replace with sn-maximum-town-size",
    },
    {
      name: "redundant defconst code action",
      uri: fileUri(perPath),
      range: rangeOf(perText, "villager-class"),
      diagnostic: {
        range: rangeOf(perText, "villager-class"),
        code: "warning:redundant-built-in-defconst",
        message: "'villager-class' is already a documented built-in class constant",
        source: "aoe2-ai-lab",
      },
      expectedTitle: "Remove redundant built-in defconst line",
    },
    {
      name: "unsafe set target explanation action",
      uri: fileUri(perPath),
      range: rangeOf(perText, "up-find-local"),
      diagnostic: {
        range: rangeOf(perText, "up-find-local"),
        code: "warning:unsafe-set-target-object",
        message: "up-set-target-object uses search-local before this rule has rebuilt that search list",
        source: "aoe2-ai-lab",
      },
      expectedPrefix: "Explain unsafe-set-target-object: `up-set-target-object` reads a search list before retained search evidence proves",
    },
    {
      name: "DUC action argument replacement",
      uri: fileUri(perPath),
      range: rangeOf(perText, "action-gathr"),
      diagnostic: {
        range: rangeOf(perText, "action-gathr"),
        code: "error:command-argument-mismatch",
        message: "up-target-objects argument 2 should be DUCAction",
        source: "aoe2-ai-lab",
      },
      expectedTitle: "Replace with action-gather",
      absentTitle: "Replace with town-center",
    },
    {
      name: "math operator argument replacement",
      uri: fileUri(perPath),
      range: rangeOf(perText, "c::"),
      diagnostic: {
        range: rangeOf(perText, "c::"),
        code: "error:command-argument-mismatch",
        message: "up-modify-sn argument 2 should be mathOp",
        source: "aoe2-ai-lab",
      },
      expectedTitle: "Replace with c:=",
      absentTitle: "Replace with action-gather",
    },
    {
      name: "typed prefix explanation action",
      uri: fileUri(perPath),
      range: rangeOf(perText, "g:="),
      diagnostic: {
        range: rangeOf(perText, "g:="),
        code: "error:command-typed-prefix-mismatch",
        message: "up-find-local argument 1 should be a plain typeOp like c:, g:, or s:, not a math/compare operator",
        source: "aoe2-ai-lab",
      },
      expectedTitle: "Replace with g:",
      absentTitle: "Replace with c:=",
    },
  ];

  for (const testCase of codeActionCases) {
    const result = await requestWithTimeout(
      connection.sendRequest("textDocument/codeAction", {
        textDocument: { uri: testCase.uri },
        range: testCase.range,
        context: { diagnostics: [testCase.diagnostic] },
      }),
      testCase.name
    );
    if (testCase.expectedPrefix) {
      assertCodeActionPrefix(result, testCase.expectedPrefix, testCase.name);
    } else {
      assertCodeAction(result, testCase.expectedTitle, testCase.name);
    }
    if (testCase.absentTitle) {
      assertNoCodeAction(result, testCase.absentTitle, testCase.name);
    }
  }

  console.log("Cursor completion, signature, and code action smoke tests passed.");
} finally {
  connection.dispose();
  child.kill();
}
