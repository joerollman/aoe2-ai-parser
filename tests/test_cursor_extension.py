import json
import os
from pathlib import Path
import subprocess
import unittest


class CursorExtensionTests(unittest.TestCase):
    def test_completion_data_contains_core_ai_tokens(self) -> None:
        root = Path(__file__).resolve().parents[1]
        subprocess.run(
            ["node", "extensions/aoe2-aiscript-cursor/scripts/build-completions.mjs"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        )

        data_path = root / "extensions" / "aoe2-aiscript-cursor" / "data" / "completions.json"
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

        self.assertIn('"lint-package", packageRoot, "--json", "--fail-level", "error"', server_source)
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
        self.assertIn("aoe2-ai-lab-setup", server_source)
        self.assertIn("function bundledLabPath", server_source)
        self.assertIn('PYTHONPATH: path.join(labPath, "src")', server_source)
        self.assertIn("*.vsix", ignore_text)
        self.assertIn("languageExtension/src/**", ignore_text)
        self.assertNotIn("lab/**", ignore_text)

    def test_lab_extension_registers_command_palette_actions(self) -> None:
        root = Path(__file__).resolve().parents[1]
        extension_root = root / "extensions" / "aoe2-aiscript-cursor-local-lab"
        package_data = json.loads((extension_root / "package.json").read_text(encoding="utf-8"))
        extension_source = (extension_root / "languageExtension" / "out" / "extension.js").read_text(encoding="utf-8")
        commands = {
            command["command"]: command["title"]
            for command in package_data["contributes"]["commands"]
        }

        self.assertEqual(commands["aoe2AiScript.lintCurrentFile"], "AoE2: Lint Current File")
        self.assertEqual(commands["aoe2AiScript.lintPackage"], "AoE2: Lint Package")
        self.assertEqual(commands["aoe2AiScript.generatePackageReport"], "AoE2: Generate Package Report")
        self.assertEqual(commands["aoe2AiScript.openLatestPackageReport"], "AoE2: Open Latest Package Report")
        self.assertIn("vscode_1.commands.registerCommand(\"aoe2AiScript.lintCurrentFile\"", extension_source)
        self.assertIn("function formatPackageIssueGroups", extension_source)
        self.assertIn("payload.issue_groups || []", extension_source)
        self.assertIn("\"-m\", \"aoe2_ai_lab\", \"lint-package\", packageRoot, \"--json\"", extension_source)
        self.assertIn("exports._test", extension_source)
        self.assertIn("\"-m\", \"aoe2_ai_lab\", \"lint-package\", packageRoot, \"--report\"", extension_source)
        self.assertIn("AOE2 AI Parser", extension_source)
        self.assertIn("function bundledLabPath", extension_source)
        self.assertIn('PYTHONPATH: path.join(settings.labPath, "src")', extension_source)

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
        self.assertIn("function labRegistrySignatureHelp", server_source)
        self.assertIn("function labSignatureParameters", server_source)
        self.assertIn("codeActionProvider: true", server_source)
        self.assertIn("connection.onCodeAction", server_source)
        self.assertIn("function codeActionsForDiagnostic", server_source)
        self.assertIn("function explanationCodeAction", server_source)
        self.assertIn("labDiagnosticExplanations().get(code)", server_source)
        self.assertIn('title: "Explain " + code + ": " + explanation', server_source)
        self.assertIn("function closestRegistryLabels", server_source)
        self.assertIn("function closestRegistryLabelsByFamilies", server_source)
        self.assertIn("function diagnosticReplacementFamilies", server_source)
        self.assertIn("function typeOpReplacementLabels", server_source)
        self.assertIn("function mathOpReplacementLabels", server_source)
        self.assertIn('"load-target"', server_source)
        self.assertIn('"strategic-number"', server_source)
        self.assertIn('"duc-action"', server_source)
        self.assertIn('"math-op"', server_source)
        self.assertIn('data: { labKind: item.kind }', server_source)
        self.assertIn("textDocument/completion", smoke_source)
        self.assertIn("textDocument/signatureHelp", smoke_source)
        self.assertIn("textDocument/codeAction", smoke_source)
        self.assertIn("up-find-local object argument", smoke_source)
        self.assertIn("up-find-local signature help", smoke_source)
        self.assertIn("missing load target code action", smoke_source)
        self.assertIn("unsafe set target explanation action", smoke_source)
        self.assertIn("expectedPrefix", smoke_source)
        self.assertIn("typed prefix explanation action", smoke_source)
        self.assertIn(".ai load target completion", smoke_source)
        self.assertIn("formatPackageIssueGroups", package_output_smoke_source)
        self.assertIn("Package summary:", package_output_smoke_source)
        self.assertIn("Issue categories:", package_output_smoke_source)
        self.assertIn("[integrity] stale-ai-root (1)", package_output_smoke_source)

    def test_lab_extension_surfaces_package_integrity_ai_diagnostics(self) -> None:
        root = Path(__file__).resolve().parents[1]
        extension_root = root / "extensions" / "aoe2-aiscript-cursor-local-lab"
        server_source = (extension_root / "languageExtension" / "out" / "server.js").read_text(encoding="utf-8")

        self.assertIn("skipped-load-random", server_source)
        self.assertIn("duplicate-root-target", server_source)
        self.assertIn("duplicate_root_targets", server_source)
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
        self.assertIn("hover = labRegistryHover(hover_txt);", server_source)
        self.assertIn("return hover;", server_source)
        self.assertIn("Syntax:", by_label["up-find-local"]["documentation"])
        self.assertIn("SN", by_label["sn-maximum-town-size"]["detail"])

    def test_local_lab_extension_packages_diagnostic_registry(self) -> None:
        root = Path(__file__).resolve().parents[1]
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
