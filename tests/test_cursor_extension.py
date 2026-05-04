import json
import os
from pathlib import Path
import subprocess
import unittest


class CursorExtensionTests(unittest.TestCase):
    def test_completion_data_contains_core_ai_tokens(self) -> None:
        root = Path(__file__).resolve().parents[1]
        data_path = (
            root
            / "extensions"
            / "aoe2-aiscript-cursor-local-lab"
            / "data"
            / "completions.json"
        )
        data = json.loads(data_path.read_text(encoding="utf-8"))
        labels = {item["label"] for item in data["items"]}

        self.assertIn("defrule", labels)
        self.assertIn("up-find-local", labels)
        self.assertIn("sn-maximum-town-size", labels)
        self.assertIn("villager", labels)
        self.assertIn("ri-loom", labels)
        self.assertGreater(data["itemCount"], 1000)

    def test_lab_diagnostics_sample_exercises_cli_output(self) -> None:
        root = Path(__file__).resolve().parents[1]
        sample_path = (
            root
            / "extensions"
            / "aoe2-aiscript-cursor-local-lab"
            / "samples"
            / "lab_diagnostics_sample.per"
        )
        env = os.environ.copy()
        env["PYTHONPATH"] = "src"

        result = subprocess.run(
            ["python", "-m", "aoe2_ai_lab", "lint", str(sample_path)],
            cwd=root,
            env=env,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("repeat-chat", result.stdout)
        self.assertIn("undefined-strategic-number", result.stdout)
        self.assertIn("undefined-constant", result.stdout)

    def test_lab_extension_diagnostics_include_visible_severity(self) -> None:
        root = Path(__file__).resolve().parents[1]
        server_path = (
            root
            / "extensions"
            / "aoe2-aiscript-cursor-local-lab"
            / "languageExtension"
            / "out"
            / "server.js"
        )

        server_source = server_path.read_text(encoding="utf-8")

        self.assertIn('code: severity + ":" + code', server_source)
        self.assertIn('message: "[" + severity + "] " + code + ": " + message', server_source)

    def test_lab_extension_prefers_reachable_package_lint(self) -> None:
        root = Path(__file__).resolve().parents[1]
        server_path = (
            root
            / "extensions"
            / "aoe2-aiscript-cursor-local-lab"
            / "languageExtension"
            / "out"
            / "server.js"
        )

        server_source = server_path.read_text(encoding="utf-8")

        self.assertIn('"lint-package", packageRoot, "--json", "--fail-level", packageFailLevel', server_source)
        self.assertIn("function execFileText", server_source)
        self.assertIn("stdout = yield execFileText(pythonPath", server_source)
        self.assertIn("diagnostics = yield runLabLinter", server_source)
        self.assertIn('packageFailLevel: "info"', server_source)
        self.assertIn("usePackageLint: false", server_source)
        self.assertIn("findNearestPackageRoot(filePath, workspacePath)", server_source)
        self.assertIn("currentFileIsReachable", server_source)
        self.assertIn("return null;", server_source)

    def test_lab_extension_uses_token_level_ranges(self) -> None:
        root = Path(__file__).resolve().parents[1]
        server_path = (
            root
            / "extensions"
            / "aoe2-aiscript-cursor-local-lab"
            / "languageExtension"
            / "out"
            / "server.js"
        )

        server_source = server_path.read_text(encoding="utf-8")

        self.assertIn("function diagnosticRangeForLine(textDocument, lineNumber, code, message, span)", server_source)
        self.assertIn("let quotedToken = /'([^']+)'/.exec(message);", server_source)
        self.assertIn('code === "repeat-chat"', server_source)
        self.assertIn("range: diagnosticRangeForLine(textDocument, line, code, message, span)", server_source)
        self.assertIn("function suppressionCodeAction", server_source)
        self.assertIn("aoe2-ai-parser-disable-line", server_source)
        self.assertIn("Suppress \" + code + \" on this line", server_source)

    def test_lab_extension_supports_ai_roots(self) -> None:
        root = Path(__file__).resolve().parents[1]
        package_path = root / "extensions" / "aoe2-aiscript-cursor-local-lab" / "package.json"
        server_path = (
            root
            / "extensions"
            / "aoe2-aiscript-cursor-local-lab"
            / "languageExtension"
            / "out"
            / "server.js"
        )

        package_data = json.loads(package_path.read_text(encoding="utf-8"))
        extensions = package_data["contributes"]["languages"][0]["extensions"]
        server_source = server_path.read_text(encoding="utf-8")

        self.assertIn(".ai", extensions)
        self.assertIn("function collectAiRootDiagnostics", server_source)
        self.assertIn("missing-load-target", server_source)
        self.assertIn('path.extname(filePath).toLowerCase() === ".ai"', server_source)
        self.assertIn('path.extname(filePath).toLowerCase() === ".per"', server_source)
        self.assertIn("return isPerFile ? filePath : null;", server_source)

    def test_lab_extension_has_setup_diagnostics_and_packaging_ignore(self) -> None:
        root = Path(__file__).resolve().parents[1]
        extension_root = root / "extensions" / "aoe2-aiscript-cursor-local-lab"
        server_path = extension_root / "languageExtension" / "out" / "server.js"

        server_source = server_path.read_text(encoding="utf-8")
        ignore_text = (extension_root / ".vscodeignore").read_text(encoding="utf-8")

        self.assertIn("function labSetupDiagnostic", server_source)
        self.assertIn("pythonPath:", server_source)
        self.assertIn("labPath:", server_source)
        self.assertIn("aoe2-ai-parser-setup", server_source)
        self.assertIn("function bundledLabPath", server_source)
        self.assertIn('PYTHONPATH: path.join(labPath, "src")', server_source)
        self.assertIn("*.vsix", ignore_text)
        self.assertIn("**/__pycache__/**", ignore_text)
        self.assertIn("**/*.pyc", ignore_text)
        self.assertIn("languageExtension/src/**", ignore_text)
        self.assertNotIn("lab/**", ignore_text)

    def test_lab_extension_registers_command_palette_actions(self) -> None:
        root = Path(__file__).resolve().parents[1]
        extension_root = root / "extensions" / "aoe2-aiscript-cursor-local-lab"
        package_data = json.loads((extension_root / "package.json").read_text(encoding="utf-8"))
        extension_source = (extension_root / "languageExtension" / "out" / "extension.js").read_text(encoding="utf-8")
        server_source = (extension_root / "languageExtension" / "out" / "server.js").read_text(encoding="utf-8")
        commands = {
            command["command"]: command["title"]
            for command in package_data["contributes"]["commands"]
        }

        self.assertEqual(commands["aoe2AiScript.lintCurrentFile"], "AoE2: Lint Current File")
        self.assertEqual(commands["aoe2AiScript.lintCurrentAi"], "AoE2: Lint Current AI")
        self.assertNotIn("aoe2AiScript.lintPackage", commands)
        self.assertEqual(commands["aoe2AiScript.lintFolder"], "AoE2: Lint Current Folder")
        self.assertEqual(commands["aoe2AiScript.lintRecursiveFolder"], "AoE2: Lint Recursive Folder")
        self.assertEqual(commands["aoe2AiScript.generatePackageReport"], "AoE2: Generate Package Report")
        self.assertEqual(commands["aoe2AiScript.openLatestPackageReport"], "AoE2: Open Latest Package Report")
        self.assertEqual(commands["aoe2AiScript.autoFormat"], "AoE2: AutoFormat Current File")
        self.assertNotIn("aoe2AiScript.autoFormatPackage", commands)
        self.assertEqual(commands["aoe2AiScript.autoFormatCurrentAi"], "AoE2: AutoFormat Current AI")
        self.assertEqual(commands["aoe2AiScript.autoFormatCurrentFolder"], "AoE2: AutoFormat Current Folder")
        self.assertEqual(commands["aoe2AiScript.autoFormatRecursiveFolder"], "AoE2: AutoFormat Recursive Folder")
        self.assertEqual(commands["aoe2AiScript.formatThenLintCurrentFile"], "AoE2: Format Then Lint Current File")
        self.assertEqual(commands["aoe2AiScript.formatThenLintCurrentAi"], "AoE2: Format Then Lint Current AI")
        self.assertEqual(commands["aoe2AiScript.formatThenLintCurrentFolder"], "AoE2: Format Then Lint Current Folder")
        self.assertEqual(commands["aoe2AiScript.formatThenLintRecursiveFolder"], "AoE2: Format Then Lint Recursive Folder")
        self.assertEqual(commands["aoe2AiScript.scaffoldSemanticColorSettings"], "AoE2: Write Semantic Color Settings")
        self.assertIn("vscode_1.commands.registerCommand(\"aoe2AiScript.lintCurrentFile\"", extension_source)
        self.assertIn("vscode_1.commands.registerCommand(\"aoe2AiScript.lintCurrentAi\"", extension_source)
        self.assertIn("vscode_1.commands.registerCommand(\"aoe2AiScript.lintFolder\"", extension_source)
        self.assertIn("vscode_1.commands.registerCommand(\"aoe2AiScript.lintRecursiveFolder\"", extension_source)
        self.assertIn("vscode_1.commands.registerCommand(\"aoe2AiScript.scaffoldSemanticColorSettings\"", extension_source)
        self.assertIn("function lintFolder", extension_source)
        self.assertIn("function lintFolderScope", extension_source)
        self.assertIn("folderPath, \"--json\"", extension_source)
        self.assertIn('"--no-recursive"', extension_source)
        self.assertIn("function formatPackageIssueGroups", extension_source)
        self.assertIn("function formatPackageLoadGraph", extension_source)
        self.assertIn("function formatPackageLintTrace", extension_source)
        self.assertIn('lines.push("Lint trace:")', extension_source)
        self.assertIn('lines.push("  roots:")', extension_source)
        self.assertIn('lines.push(rootChildPrefix + "|-- reachable .per files ("', extension_source)
        self.assertIn('lines.push(rootChildPrefix + "|-- included .xs files ("', extension_source)
        self.assertIn('lines.push(rootChildPrefix + "`-- load/include graph")', extension_source)
        self.assertIn("payload.issue_groups || []", extension_source)
        self.assertIn("root.load_graph || []", extension_source)
        self.assertIn("channel.show(false)", extension_source)
        self.assertIn("AoE2 package command did not run.", extension_source)
        self.assertIn("See AOE2 AI Parser output.", extension_source)
        self.assertIn("documentation_markdown", extension_source)
        self.assertNotIn("\"-m\", \"aoe2_ai_lab\", \"lint-package\", packageRoot, \"--json\"", extension_source)
        self.assertIn('"--trace-progress"', extension_source)
        self.assertIn("function execFileTextStreaming", extension_source)
        self.assertIn("child.stderr.on(\"data\"", extension_source)
        self.assertIn("exports._test", extension_source)
        self.assertIn("\"-m\", \"aoe2_ai_lab\", \"lint-package\", packageRoot, \"--report\"", extension_source)
        self.assertIn("AOE2 AI Parser", extension_source)
        self.assertIn("function bundledLabPath", extension_source)
        self.assertIn('PYTHONPATH: path.join(settings.labPath, "src")', extension_source)
        self.assertIn('config.get("packageFailLevel") || "info"', extension_source)
        self.assertIn('"--fail-level", settings.packageFailLevel', extension_source)
        self.assertIn('config.get("enableSemanticColors")', extension_source)
        self.assertIn("semanticColorsEnabled() &&", extension_source)
        self.assertIn("aoe2AiScript.autoFormat", extension_source)
        self.assertNotIn("aoe2AiScript.autoFormatPackage", extension_source)
        self.assertIn("aoe2AiScript.autoFormatCurrentAi", extension_source)
        self.assertIn("aoe2AiScript.formatThenLintCurrentAi", extension_source)
        self.assertIn('"resolve-current-ai", filePath, "--json"', extension_source)
        self.assertIn("Multiple .ai roots reach this .per file", extension_source)
        self.assertIn("No candidate AI found: no nearby .ai load graph reaches the active file.", extension_source)
        self.assertNotIn("active .per was not found in its load graph", extension_source)
        self.assertNotIn("No .ai load graph reaches this file. Select a nearby AI root.", extension_source)
        self.assertIn("formatCommandArgs(aiRoot, false, { includeLoads: true })", extension_source)
        self.assertIn("formatThenLintFolder", extension_source)
        self.assertIn("if (formatResult && formatResult.ok)", extension_source)
        self.assertNotIn("function autoFormatPackage", extension_source)
        self.assertIn("documents.onDidOpen(change =>", server_source)
        self.assertIn("connection.sendDiagnostics({ uri: change.document.uri, diagnostics: [] })", server_source)
        self.assertNotIn("validateTextDocument(change.document);", server_source)

    def test_lab_extension_contributes_color_themes_for_custom_tokens(self) -> None:
        root = Path(__file__).resolve().parents[1]
        extension_root = root / "extensions" / "aoe2-aiscript-cursor-local-lab"
        package_data = json.loads((extension_root / "package.json").read_text(encoding="utf-8"))
        settings = package_data["contributes"]["configuration"]["properties"]
        themes = {
            theme["label"]: theme
            for theme in package_data["contributes"]["themes"]
        }
        semantic_tokens = {
            "aoe2Action",
            "aoe2Fact",
            "aoe2FactAction",
            "aoe2Command",
            "aoe2StrategicNumber",
            "aoe2Object",
            "aoe2Tech",
            "aoe2Value",
            "aoe2LocalConstant",
        }

        self.assertEqual(
            themes["AOE2 AI Parser Dark"]["path"],
            "./themes/aoe2-ai-parser-dark-color-theme.json",
        )
        self.assertEqual(
            themes["AOE2 AI Parser Light"]["path"],
            "./themes/aoe2-ai-parser-light-color-theme.json",
        )
        self.assertEqual(
            themes["AOE2 AiScript Classic"]["path"],
            "./themes/aoe2-aiscript-classic-color-theme.json",
        )
        self.assertEqual(themes["AOE2 AI Parser Dark"]["uiTheme"], "vs-dark")
        self.assertEqual(themes["AOE2 AI Parser Light"]["uiTheme"], "vs")
        self.assertEqual(themes["AOE2 AiScript Classic"]["uiTheme"], "vs-dark")
        self.assertNotIn("configurationDefaults", package_data["contributes"])
        self.assertFalse(settings["aoe2_AiScript.enableSemanticColors"]["default"])
        self.assertEqual(settings["aoe2_AiScript.semanticColors.theme"]["default"], "auto")
        self.assertEqual(
            settings["aoe2_AiScript.semanticColors.theme"]["enum"],
            ["auto", "dark", "light", "custom"],
        )
        for legacy_setting_name in [
            "aoe2_AiScript.semanticColors.action",
            "aoe2_AiScript.semanticColors.fact",
            "aoe2_AiScript.semanticColors.factAction",
            "aoe2_AiScript.semanticColors.command",
            "aoe2_AiScript.semanticColors.strategicNumber",
            "aoe2_AiScript.semanticColors.object",
            "aoe2_AiScript.semanticColors.tech",
            "aoe2_AiScript.semanticColors.value",
            "aoe2_AiScript.semanticColors.localConstant",
        ]:
            self.assertNotIn(legacy_setting_name, settings)
        by_theme = settings["aoe2_AiScript.semanticColors.byTheme"]["default"]
        self.assertEqual(set(by_theme), {"Dark", "Light", "Custom"})
        self.assertEqual(by_theme["Dark"]["action"], "#5DADEC")
        self.assertEqual(by_theme["Light"]["action"], "#0550AE")
        self.assertEqual(by_theme["Custom"]["action"], "#569CD6")

        for label, expected_type in [
            ("AOE2 AI Parser Dark", "dark"),
            ("AOE2 AI Parser Light", "light"),
        ]:
            theme_path = extension_root / themes[label]["path"].replace("./", "")
            theme_data = json.loads(theme_path.read_text(encoding="utf-8"))
            semantic_colors = theme_data["semanticTokenColors"]

            self.assertEqual(theme_data["type"], expected_type)
            self.assertTrue(theme_data["semanticHighlighting"])
            self.assertIn("tokenColors", theme_data)
            for token in semantic_tokens:
                self.assertIn(token, semantic_colors)
                self.assertIn(f"{token}:aoe2aiscript", semantic_colors)

        dark_data = json.loads(
            (extension_root / "themes" / "aoe2-ai-parser-dark-color-theme.json").read_text(
                encoding="utf-8"
            )
        )
        light_data = json.loads(
            (extension_root / "themes" / "aoe2-ai-parser-light-color-theme.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertNotEqual(
            dark_data["semanticTokenColors"]["aoe2StrategicNumber"],
            dark_data["semanticTokenColors"]["aoe2LocalConstant"],
        )
        self.assertNotEqual(
            light_data["semanticTokenColors"]["aoe2StrategicNumber"],
            light_data["semanticTokenColors"]["aoe2LocalConstant"],
        )
        classic_data = json.loads(
            (extension_root / "themes" / "aoe2-aiscript-classic-color-theme.json").read_text(
                encoding="utf-8"
            )
        )
        classic_scopes = {
            scope
            for rule in classic_data["tokenColors"]
            for scope in (
                rule["scope"] if isinstance(rule["scope"], list) else [rule["scope"]]
            )
        }
        self.assertFalse(classic_data["semanticHighlighting"])
        self.assertIn("entity.name.function.aoe2aiscript.fact", classic_scopes)
        self.assertIn("entity.name.function.aoe2aiscript.action", classic_scopes)
        self.assertIn("storage.type.aoe2aiscript.def.rule", classic_scopes)

    def test_lab_extension_supports_setting_driven_semantic_colors(self) -> None:
        root = Path(__file__).resolve().parents[1]
        extension_root = root / "extensions" / "aoe2-aiscript-cursor-local-lab"
        extension_source = (extension_root / "languageExtension" / "out" / "extension.js").read_text(
            encoding="utf-8"
        )

        self.assertIn("semanticColorSettings", extension_source)
        self.assertIn("semanticColorDefaults", extension_source)
        self.assertIn("semanticColorByThemeDefaults", extension_source)
        self.assertIn("semanticColorSettingKeys", extension_source)
        self.assertIn('aoe2Action: "semanticColors.action"', extension_source)
        self.assertIn('config.get("semanticColors.byTheme")', extension_source)
        self.assertIn('config.get("semanticColors.theme")', extension_source)
        self.assertIn('get("colorTheme")', extension_source)
        self.assertIn("function refreshSemanticDecorationTypes", extension_source)
        self.assertIn("async function scaffoldSemanticColorSettings", extension_source)
        self.assertIn('config.update("semanticColors.byTheme"', extension_source)
        self.assertIn('config.update("semanticColors.theme"', extension_source)
        self.assertIn('editorConfig.update("semanticTokenColorCustomizations", undefined', extension_source)
        self.assertIn('editorConfig.update("tokenColorCustomizations", undefined', extension_source)
        self.assertIn("ConfigurationTarget.Workspace", extension_source)
        self.assertIn("createTextEditorDecorationType({ color })", extension_source)
        self.assertIn("function semanticDecorationRanges", extension_source)
        self.assertIn("function updateSemanticDecorationsForVisibleEditors", extension_source)
        self.assertIn("function scheduleSemanticDecorationUpdate", extension_source)
        self.assertIn("setTimeout(() =>", extension_source)
        self.assertIn('event.affectsConfiguration("aoe2_AiScript.semanticColors")', extension_source)
        self.assertIn('event.affectsConfiguration("workbench.colorTheme")', extension_source)

    def test_lab_extension_exposes_package_fail_level_setting(self) -> None:
        root = Path(__file__).resolve().parents[1]
        package_data = json.loads(
            (
                root
                / "extensions"
                / "aoe2-aiscript-cursor-local-lab"
                / "package.json"
            ).read_text(encoding="utf-8")
        )
        setting = package_data["contributes"]["configuration"]["properties"]["aoe2_AiScript.packageFailLevel"]

        self.assertEqual(setting["default"], "info")
        self.assertEqual(setting["enum"], ["error", "warning", "info"])

        max_errors_setting = package_data["contributes"]["configuration"]["properties"]["aoe2_AiScript.maxErrorsReported"]
        self.assertEqual(max_errors_setting["default"], -1)
        self.assertIn("Default -1 means no limit", max_errors_setting["description"])

        package_lint_setting = package_data["contributes"]["configuration"]["properties"]["aoe2_AiScript.usePackageLint"]
        self.assertFalse(package_lint_setting["default"])
        self.assertIn("CPU-heavy", package_lint_setting["description"])
        self.assertIn("nearest folder containing an .ai file", package_lint_setting["description"])

        format_on_save_setting = package_data["contributes"]["configuration"]["properties"]["aoe2_AiScript.formatOnSave"]
        self.assertFalse(format_on_save_setting["default"])
        self.assertIn("active .per or .ai file", format_on_save_setting["description"])

        self.assertNotIn("aoe2_AiScript.aiDirectory", package_data["contributes"]["configuration"]["properties"])
        self.assertNotIn("aoe2_AiScript.aiName", package_data["contributes"]["configuration"]["properties"])

    def test_lab_extension_does_not_print_generic_command_failed_when_stdout_exists(self) -> None:
        root = Path(__file__).resolve().parents[1]
        extension_source = (
            root
            / "extensions"
            / "aoe2-aiscript-cursor-local-lab"
            / "languageExtension"
            / "out"
            / "extension.js"
        ).read_text(encoding="utf-8")

        self.assertIn('let stderr = error.stderr ? String(error.stderr) : "";', extension_source)
        self.assertIn("if (!stdout && !stderr)", extension_source)
        self.assertIn("AoE2 package report generated with findings.", extension_source)
        self.assertIn("function execFileText", extension_source)
        self.assertIn("async function runLabCommand", extension_source)
        self.assertIn("await execFileTextStreaming(settings.pythonPath", extension_source)
        self.assertIn('channel.appendLine(title + " complete")', extension_source)
        self.assertIn('channel.appendLine("status: " + (ok ? "completed" : "failed"))', extension_source)
        self.assertIn('channel.appendLine("duration: " + elapsedSeconds + "s")', extension_source)
        self.assertIn("vscode_1.window.withProgress", extension_source)
        self.assertIn("vscode_1.ProgressLocation.Notification", extension_source)
        self.assertIn('progress.report({ message: "running... " + elapsedSeconds + "s" })', extension_source)
        self.assertNotIn("async function lintPackage", extension_source)
        self.assertIn("await runLabCommand", extension_source)
        self.assertNotIn("__awaiter", extension_source)
        self.assertNotIn("execFileSync(settings.pythonPath", extension_source)
        self.assertIn('"vscode.markdown.preview.editor"', extension_source)
        self.assertIn("showTextDocument(document, vscode_1.ViewColumn.Beside)", extension_source)

    def test_local_lab_extension_merges_registry_completions(self) -> None:
        root = Path(__file__).resolve().parents[1]
        extension_root = root / "extensions" / "aoe2-aiscript-cursor-local-lab"
        server_source = (extension_root / "languageExtension" / "out" / "server.js").read_text(encoding="utf-8")
        completion_data = json.loads((extension_root / "data" / "completions.json").read_text(encoding="utf-8"))
        labels = {item["label"] for item in completion_data["items"]}

        self.assertGreater(completion_data["itemCount"], 2000)
        self.assertIn("addLabRegistryCompletions(existingLabels)", server_source)
        self.assertIn("function labCompletionKind", server_source)
        self.assertIn("sn-maximum-town-size", labels)
        self.assertIn("up-find-local", labels)
        self.assertIn("villager", labels)

    def test_lab_extension_uses_contextual_completions(self) -> None:
        root = Path(__file__).resolve().parents[1]
        extension_root = root / "extensions" / "aoe2-aiscript-cursor-local-lab"
        server_source = (extension_root / "languageExtension" / "out" / "server.js").read_text(encoding="utf-8")
        smoke_source = (root / "scripts" / "smoke-cursor-completions.mjs").read_text(encoding="utf-8")
        package_output_smoke_source = (
            root / "scripts" / "smoke-cursor-package-output.mjs"
        ).read_text(encoding="utf-8")

        self.assertIn("function contextualCompletionList", server_source)
        self.assertIn("function completionContextKind", server_source)
        self.assertIn("function currentCommandArgument", server_source)
        self.assertIn("function preferredKindsForParameter", server_source)
        self.assertIn("function completionItemFamily", server_source)
        self.assertIn("function localDefconstCompletions", server_source)
        self.assertIn("function loadTargetCompletions", server_source)
        self.assertIn("function labDiagnosticExplanations", server_source)
        self.assertIn("diagnostic-codes.json", server_source)
        self.assertIn("aoe2AiScript.openDiagnosticDocsPreview", server_source)
        self.assertIn("function labRegistrySignatureHelp", server_source)
        self.assertIn("function labSignatureParameters", server_source)
        self.assertIn("function markdownHeadingFragment", server_source)
        self.assertIn("return markdownAnchor(token);", server_source)
        self.assertIn('with({ fragment: anchor }).toString()', server_source)
        self.assertIn("codeActionProvider: true", server_source)
        self.assertIn("connection.onCodeAction", server_source)
        self.assertIn("function codeActionsForDiagnostic", server_source)
        self.assertIn("function explanationCodeAction", server_source)
        self.assertIn("labDiagnosticExplanations().get(code)", server_source)
        self.assertIn('title: "Open diagnostic docs for " + code + ": " + explanation', server_source)
        self.assertIn("function closestRegistryLabels", server_source)
        self.assertIn("function closestRegistryLabelsByFamilies", server_source)
        self.assertIn("function diagnosticReplacementFamilies", server_source)
        self.assertIn("function typeOpReplacementLabels", server_source)
        self.assertIn("function mathOpReplacementLabels", server_source)
        self.assertIn('"load-target"', server_source)
        self.assertIn('"strategic-number"', server_source)
        self.assertIn('"duc-action"', server_source)
        self.assertIn('"math-op"', server_source)
        self.assertIn('"map-type"', server_source)
        self.assertIn('data: { labKind: item.kind }', server_source)
        self.assertIn("textDocument/completion", smoke_source)
        self.assertIn("textDocument/signatureHelp", smoke_source)
        self.assertIn("textDocument/definition", smoke_source)
        self.assertIn("textDocument/codeAction", smoke_source)
        self.assertIn("up-find-local object argument", smoke_source)
        self.assertIn("map-type argument", smoke_source)
        self.assertIn("difficulty argument", smoke_source)
        self.assertIn("resource argument", smoke_source)
        self.assertIn(".ai load-random target definition", smoke_source)
        self.assertIn(".per include target definition", smoke_source)
        self.assertIn("up-find-local signature help", smoke_source)
        self.assertIn("missing load target code action", smoke_source)
        self.assertIn("unsafe set target explanation action", smoke_source)
        self.assertIn("expectedPrefix", smoke_source)
        self.assertIn("typed prefix explanation action", smoke_source)
        self.assertIn(".ai load target completion", smoke_source)
        self.assertIn("formatPackageIssueGroups", package_output_smoke_source)
        self.assertIn("Package summary:", package_output_smoke_source)
        self.assertIn("Issue categories:", package_output_smoke_source)
        self.assertIn("Load graph:", package_output_smoke_source)
        self.assertIn("[integrity] stale-ai-root (1)", package_output_smoke_source)

    def test_lab_extension_surfaces_package_integrity_ai_diagnostics(self) -> None:
        root = Path(__file__).resolve().parents[1]
        extension_root = root / "extensions" / "aoe2-aiscript-cursor-local-lab"
        server_source = (extension_root / "languageExtension" / "out" / "server.js").read_text(encoding="utf-8")

        self.assertIn("skipped-load-random", server_source)
        self.assertIn("duplicate-root-target", server_source)
        self.assertIn("duplicate-ai-name", server_source)
        self.assertIn("duplicate-load-target", server_source)
        self.assertIn("duplicate-per-name", server_source)
        self.assertIn("duplicate_root_targets", server_source)
        self.assertIn("duplicate_ai_names", server_source)
        self.assertIn("duplicate_load_targets", server_source)
        self.assertIn("duplicate_per_names", server_source)
        self.assertTrue((extension_root / "samples" / "lab_load_random_sample.ai").exists())
        self.assertTrue((extension_root / "samples" / "lab_duplicate_one.ai").exists())

    def test_lab_extension_prefers_python_json_spans(self) -> None:
        root = Path(__file__).resolve().parents[1]
        extension_root = root / "extensions" / "aoe2-aiscript-cursor-local-lab"
        server_source = (extension_root / "languageExtension" / "out" / "server.js").read_text(encoding="utf-8")

        self.assertIn('"lint", filePath, "--json"', server_source)
        self.assertIn("finding.span", server_source)
        self.assertIn("function diagnosticRangeForLine(textDocument, lineNumber, code, message, span)", server_source)

    def test_lab_extension_uses_registry_hovers(self) -> None:
        root = Path(__file__).resolve().parents[1]
        extension_root = root / "extensions" / "aoe2-aiscript-cursor-local-lab"
        server_source = (extension_root / "languageExtension" / "out" / "server.js").read_text(encoding="utf-8")
        completion_data = json.loads((extension_root / "data" / "completions.json").read_text(encoding="utf-8"))
        by_label = {item["label"]: item for item in completion_data["items"]}

        self.assertIn("function labRegistryHover", server_source)
        self.assertIn("AOE2 AI Parser hover request failed", server_source)
        self.assertIn("return labRegistryHover(token);", server_source)
        self.assertIn("maxHoverDocumentationLength", server_source)
        self.assertIn("documentation.slice(0, maxHoverDocumentationLength)", server_source)
        self.assertIn("Syntax:", by_label["up-find-local"]["documentation"])
        self.assertIn("SN", by_label["sn-maximum-town-size"]["detail"])

    def test_local_lab_extension_packages_diagnostic_registry(self) -> None:
        root = Path(__file__).resolve().parents[1]
        extension_root = root / "extensions" / "aoe2-aiscript-cursor-local-lab"
        extension_source = (extension_root / "languageExtension" / "out" / "extension.js").read_text(encoding="utf-8")
        diagnostic_data = json.loads(
            (
                root
                / "extensions"
                / "aoe2-aiscript-cursor-local-lab"
                / "data"
                / "diagnostic-codes.json"
            ).read_text(encoding="utf-8")
        )
        codes = {entry["code"] for entry in diagnostic_data["codes"]}

        self.assertIn("unsafe-set-target-object", codes)
        self.assertIn("command-typed-prefix-mismatch", codes)
        self.assertIn("missing-load-target", codes)
        self.assertIn("duplicate-ai-name", codes)
        self.assertIn("duplicate-load-target", codes)
        self.assertIn("duplicate-per-name", codes)
        self.assertIn("function openDiagnosticDocsPreview", extension_source)
        self.assertIn("validator-diagnostic-codes.md", extension_source)
        self.assertIn("aoe2AiScript.openDiagnosticDocsPreview", extension_source)
        self.assertIn(
            '<a id="diagnostic-command-argument-mismatch"></a>',
            (root / "docs" / "workflows" / "validator-diagnostic-codes.md").read_text(encoding="utf-8"),
        )

    def test_extension_packaging_syncs_bundled_lab_runtime(self) -> None:
        root = Path(__file__).resolve().parents[1]
        package_data = json.loads((root / "package.json").read_text(encoding="utf-8"))
        install_source = (root / "scripts" / "install-cursor-extension.mjs").read_text(encoding="utf-8")
        sync_source = (root / "scripts" / "sync-extension-lab.mjs").read_text(encoding="utf-8")

        self.assertEqual(package_data["scripts"]["sync:extension-lab"], "node scripts/sync-extension-lab.mjs")
        self.assertIn("node\", [\"scripts/sync-extension-lab.mjs\"]", install_source)
        self.assertIn("docs\", \"extracted\", \"inventories", sync_source)
        self.assertIn("docs\", \"reference\", \"generated", sync_source)
        self.assertIn("[\"src\", \"src\"]", sync_source)


if __name__ == "__main__":
    unittest.main()
