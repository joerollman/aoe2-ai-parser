import ast
import json
from pathlib import Path
import re
import subprocess
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_JSON_PATH = REPO_ROOT / "docs" / "workflows" / "validator-diagnostic-codes.json"
REGISTRY_MARKDOWN_PATH = REPO_ROOT / "docs" / "workflows" / "validator-diagnostic-codes.md"
EXTENSION_REGISTRY_JSON_PATH = (
    REPO_ROOT
    / "extensions"
    / "aoe2-ai-parser-extension"
    / "data"
    / "diagnostic-codes.json"
)


class DiagnosticRegistryTests(unittest.TestCase):
    def test_diagnostic_registry_covers_emitted_codes(self) -> None:
        documented_codes = self._registry_codes()
        emitted_codes = self._finding_codes_from_python_sources()
        emitted_codes.update(self._preprocessor_codes())
        emitted_codes.update({"duplicate-root-target", "stale-ai-root", "unreachable-per-file"})

        self.assertEqual(sorted(emitted_codes - documented_codes), [])

    def test_cli_uses_diagnostic_registry_instead_of_duplicated_explanation_dict(self) -> None:
        cli_source = (REPO_ROOT / "src" / "aoe2_ai_lab" / "cli.py").read_text(encoding="utf-8")

        self.assertIn("diagnostic_code_explanation", cli_source)
        self.assertNotIn("REPORT_CATEGORY_EXPLANATIONS", cli_source)

    def test_cursor_explanation_actions_use_packaged_diagnostic_registry(self) -> None:
        server_source = (
            REPO_ROOT
            / "extensions"
            / "aoe2-ai-parser-extension"
            / "languageExtension"
            / "out"
            / "server.js"
        ).read_text(encoding="utf-8")
        packaged_registry = json.loads(
            EXTENSION_REGISTRY_JSON_PATH.read_text(encoding="utf-8")
        )
        packaged_codes = {entry["code"] for entry in packaged_registry["codes"]}

        self.assertIn("labDiagnosticExplanations().get(code)", server_source)
        self.assertNotIn("let explanations = {", server_source)
        self.assertEqual(packaged_codes, self._registry_codes())

    def test_diagnostic_registry_markdown_is_generated_from_json(self) -> None:
        result = subprocess.run(
            ["node", "scripts/generate-diagnostic-registry.mjs", "--check"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_markdown_codes_match_json_codes(self) -> None:
        markdown_codes = set(re.findall(r"^\| `([^`]+)` \|", REGISTRY_MARKDOWN_PATH.read_text(encoding="utf-8"), re.MULTILINE))

        self.assertEqual(markdown_codes, self._registry_codes())

    def test_defconst_range_diagnostic_cites_limits_references(self) -> None:
        registry = json.loads(REGISTRY_JSON_PATH.read_text(encoding="utf-8"))
        entry = next(entry for entry in registry["codes"] if entry["code"] == "defconst-value-out-of-range")
        markdown = REGISTRY_MARKDOWN_PATH.read_text(encoding="utf-8")

        self.assertEqual(
            [reference["label"] for reference in entry["references"]],
            ["Internal validation notes", "AIRef Data Limits"],
        )
        self.assertIn("https://airef.github.io/resources/articles/data-limits.html", markdown)
        self.assertIn("internal-validation-notes.md#defconst-numeric-range", markdown)

    def test_extension_registry_copy_matches_source_json(self) -> None:
        self.assertEqual(
            json.loads(EXTENSION_REGISTRY_JSON_PATH.read_text(encoding="utf-8")),
            json.loads(REGISTRY_JSON_PATH.read_text(encoding="utf-8")),
        )

    def _registry_codes(self) -> set[str]:
        registry = json.loads(REGISTRY_JSON_PATH.read_text(encoding="utf-8"))
        return {entry["code"] for entry in registry["codes"]}

    def _finding_codes_from_python_sources(self) -> set[str]:
        codes: set[str] = set()
        for relative in ("src/aoe2_ai_lab/linter.py", "src/aoe2_ai_lab/ai_package.py"):
            tree = ast.parse((REPO_ROOT / relative).read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call) or getattr(node.func, "id", None) != "Finding":
                    continue
                if len(node.args) >= 2 and isinstance(node.args[1], ast.Constant) and isinstance(node.args[1].value, str):
                    codes.add(node.args[1].value)
                for keyword in node.keywords:
                    if keyword.arg == "code" and isinstance(keyword.value, ast.Constant) and isinstance(keyword.value.value, str):
                        codes.add(keyword.value.value)
        return codes

    def _preprocessor_codes(self) -> set[str]:
        parser_source = (REPO_ROOT / "src" / "aoe2_ai_lab" / "parser.py").read_text(encoding="utf-8")
        return set(re.findall(r'"((?:duplicate|malformed|unexpected|unterminated)-preprocessor-[^"]+)"', parser_source))


if __name__ == "__main__":
    unittest.main()
