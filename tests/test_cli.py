import os
from contextlib import redirect_stdout
from contextlib import redirect_stderr
import io
import json
from pathlib import Path
import unittest
from uuid import uuid4

from aoe2_ai_lab.cli import (
    diagnostic_code_explanation,
    find_log_cleanup_candidates,
    find_de_profile_dirs,
    install_rms_files,
    main,
)


class WorkspaceTempDir:
    def __enter__(self) -> Path:
        self.path = Path("tests") / ".tmp" / uuid4().hex
        self.path.mkdir(parents=True, exist_ok=False)
        return self.path

    def __exit__(self, exc_type, exc, tb) -> None:
        for child in sorted(self.path.rglob("*"), reverse=True):
            if child.is_file():
                child.unlink()
            elif child.is_dir():
                child.rmdir()
        self.path.rmdir()


class CliTests(unittest.TestCase):
    def test_diagnostic_code_explanation_comes_from_json_registry(self) -> None:
        root = Path(__file__).resolve().parents[1]
        registry = json.loads(
            (root / "docs" / "workflows" / "validator-diagnostic-codes.json").read_text(encoding="utf-8")
        )
        expected = {
            entry["code"]: entry["meaning"]
            for entry in registry["codes"]
        }["up-build-place-point-coordinate-as-escrow"]

        self.assertEqual(diagnostic_code_explanation("up-build-place-point-coordinate-as-escrow"), expected)

    def test_diagnostics_cli_lists_registry_entries(self) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = main(["diagnostics"])

        self.assertEqual(code, 0)
        self.assertIn("command-role-mismatch", buffer.getvalue())
        self.assertIn("cursor action:", buffer.getvalue())

    def test_diagnostics_cli_resolves_single_code(self) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = main(["diagnostics", "command-role-mismatch"])

        output = buffer.getvalue()
        self.assertEqual(code, 0)
        self.assertIn("command-role-mismatch", output)
        self.assertIn("severity: error", output)
        self.assertIn("wrong rule side", output)
        self.assertNotIn("unsafe-set-target-object", output)

    def test_diagnostics_cli_emits_json(self) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = main(["diagnostics", "command-role-mismatch", "--json"])

        self.assertEqual(code, 0)
        payload = json.loads(buffer.getvalue())
        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["diagnostics"][0]["code"], "command-role-mismatch")

    def test_diagnostics_cli_unknown_code_fails(self) -> None:
        stdout_buffer = io.StringIO()
        stderr_buffer = io.StringIO()
        with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
            code = main(["diagnostics", "not-a-real-code"])

        self.assertEqual(code, 2)
        self.assertEqual(stdout_buffer.getvalue(), "")
        self.assertIn("unknown diagnostic code", stderr_buffer.getvalue())

    def test_find_de_profile_dirs_returns_numeric_profiles(self) -> None:
        with WorkspaceTempDir() as root:
            (root / "0").mkdir()
            (root / "76561198084679681").mkdir()
            (root / "logs").mkdir()

            profiles = find_de_profile_dirs(root)

        self.assertEqual([path.name for path in profiles], ["0", "76561198084679681"])

    def test_install_rms_files_copies_rms_to_profiles(self) -> None:
        with WorkspaceTempDir() as root:
            rms_dir = root / "rms"
            rms_dir.mkdir()
            (rms_dir / "fixture.rms").write_text("<PLAYER_SETUP>\nrandom_placement\n", encoding="utf-8")
            (rms_dir / "ignore.txt").write_text("ignore", encoding="utf-8")
            profiles_root = root / "profiles"
            profile = profiles_root / "123"
            profile.mkdir(parents=True)

            targets = install_rms_files(rms_dir, profiles_root)

            installed = profile / "resources" / "_common" / "random-map-scripts" / "fixture.rms"
            self.assertEqual(targets, [installed.parent])
            self.assertTrue(installed.exists())

    def test_lint_json_includes_source_span(self) -> None:
        with WorkspaceTempDir() as root:
            path = root / "Sample.per"
            path.write_text(
                """
(defrule
    (true)
=>
    (set-strategic-number sn-not-real 5)
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                code = main(["lint", str(path), "--json"])
            source_lines = path.read_text(encoding="utf-8").splitlines()

        self.assertEqual(code, 1)
        payload = json.loads(buffer.getvalue())
        finding = next(
            item for item in payload["findings"]
            if item["code"] == "undefined-strategic-number"
        )
        self.assertEqual(finding["span"]["start_line"], 4)
        self.assertEqual(finding["span"]["end_line"], 4)
        self.assertEqual(
            source_lines[3][
                finding["span"]["start_col"]:finding["span"]["end_col"]
            ],
            "sn-not-real",
        )

    def test_lint_json_spans_typed_prefix_token(self) -> None:
        with WorkspaceTempDir() as root:
            path = root / "Sample.per"
            path.write_text(
                """
(defrule
    (true)
=>
    (up-set-target-by-id g:= target-id)
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                code = main(["lint", str(path), "--json"])
            source_lines = path.read_text(encoding="utf-8").splitlines()

        self.assertEqual(code, 1)
        payload = json.loads(buffer.getvalue())
        finding = next(
            item for item in payload["findings"]
            if item["code"] == "command-typed-prefix-mismatch"
        )
        self.assertEqual(
            source_lines[3][
                finding["span"]["start_col"]:finding["span"]["end_col"]
            ],
            "g:=",
        )

    def test_lint_json_spans_typed_operand_token(self) -> None:
        with WorkspaceTempDir() as root:
            path = root / "Sample.per"
            path.write_text(
                """
(defrule
    (true)
=>
    (up-set-target-by-id g: sn-maximum-town-size)
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                code = main(["lint", str(path), "--json"])
            source_lines = path.read_text(encoding="utf-8").splitlines()

        self.assertEqual(code, 1)
        payload = json.loads(buffer.getvalue())
        finding = next(
            item for item in payload["findings"]
            if item["code"] == "command-typed-operand-mismatch"
        )
        self.assertEqual(
            source_lines[3][
                finding["span"]["start_col"]:finding["span"]["end_col"]
            ],
            "sn-maximum-town-size",
        )

    def test_lint_json_spans_command_argument_token(self) -> None:
        with WorkspaceTempDir() as root:
            path = root / "Sample.per"
            path.write_text(
                """
(defrule
    (true)
=>
    (up-set-target-object search-none c: 0)
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                code = main(["lint", str(path), "--json"])
            source_lines = path.read_text(encoding="utf-8").splitlines()

        self.assertEqual(code, 1)
        payload = json.loads(buffer.getvalue())
        finding = next(
            item for item in payload["findings"]
            if item["code"] == "command-argument-mismatch"
        )
        self.assertEqual(
            source_lines[3][
                finding["span"]["start_col"]:finding["span"]["end_col"]
            ],
            "search-none",
        )

    def test_lint_json_spans_command_family_mismatch_token(self) -> None:
        with WorkspaceTempDir() as root:
            path = root / "Sample.per"
            path.write_text(
                """
(defrule
    (true)
=>
    (set-goal sn-maximum-town-size 1)
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                code = main(["lint", str(path), "--json"])
            source_lines = path.read_text(encoding="utf-8").splitlines()

        self.assertEqual(code, 1)
        payload = json.loads(buffer.getvalue())
        finding = next(
            item for item in payload["findings"]
            if item["code"] == "command-family-mismatch"
        )
        self.assertEqual(
            source_lines[3][
                finding["span"]["start_col"]:finding["span"]["end_col"]
            ],
            "sn-maximum-town-size",
        )

    def test_lint_json_spans_command_numeric_range_mismatch_token(self) -> None:
        with WorkspaceTempDir() as root:
            path = root / "Sample.per"
            path.write_text(
                """
(defrule
    (true)
=>
    (set-goal 0 1)
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                code = main(["lint", str(path), "--json"])
            source_lines = path.read_text(encoding="utf-8").splitlines()

        self.assertEqual(code, 1)
        payload = json.loads(buffer.getvalue())
        finding = next(
            item for item in payload["findings"]
            if item["code"] == "command-numeric-range-mismatch"
        )
        self.assertEqual(
            source_lines[3][
                finding["span"]["start_col"]:finding["span"]["end_col"]
            ],
            "0",
        )

    def test_lint_json_span_prefers_unquoted_token(self) -> None:
        with WorkspaceTempDir() as root:
            path = root / "Sample.per"
            path.write_text(
                """
(defrule
    (true)
=>
    (chat-to-all "set-goal 0")
    (set-goal 0 1)
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                code = main(["lint", str(path), "--json"])
            source_lines = path.read_text(encoding="utf-8").splitlines()

        self.assertEqual(code, 1)
        payload = json.loads(buffer.getvalue())
        finding = next(
            item for item in payload["findings"]
            if item["code"] == "command-numeric-range-mismatch"
        )
        self.assertEqual(
            source_lines[4][
                finding["span"]["start_col"]:finding["span"]["end_col"]
            ],
            "0",
        )

    def test_lint_json_span_uses_whole_token_match(self) -> None:
        with WorkspaceTempDir() as root:
            path = root / "Sample.per"
            path.write_text(
                """
(defrule
    (true)
=>
    (set-goal 10 1) (set-goal 0 1)
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                code = main(["lint", str(path), "--json"])
            source_lines = path.read_text(encoding="utf-8").splitlines()

        self.assertEqual(code, 1)
        payload = json.loads(buffer.getvalue())
        finding = next(
            item for item in payload["findings"]
            if item["code"] == "command-numeric-range-mismatch"
        )
        self.assertEqual(
            source_lines[3][
                finding["span"]["start_col"]:finding["span"]["end_col"]
            ],
            "0",
        )
        self.assertGreater(finding["span"]["start_col"], source_lines[3].index("10"))

    def test_lint_json_span_prefers_unquoted_token_after_escaped_quote(self) -> None:
        with WorkspaceTempDir() as root:
            path = root / "Sample.per"
            path.write_text(
                """
(defrule
    (true)
=> (chat-to-all "escaped \\" 0") (set-goal 0 1) (disable-self))
""".strip(),
                encoding="utf-8",
            )
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                code = main(["lint", str(path), "--json"])
            source_lines = path.read_text(encoding="utf-8").splitlines()

        self.assertEqual(code, 1)
        payload = json.loads(buffer.getvalue())
        finding = next(
            item for item in payload["findings"]
            if item["code"] == "command-numeric-range-mismatch"
        )
        span = finding["span"]
        self.assertEqual(source_lines[2][span["start_col"]:span["end_col"]], "0")
        self.assertGreater(span["start_col"], source_lines[2].index("set-goal"))

    def test_lint_json_spans_malformed_load_target(self) -> None:
        with WorkspaceTempDir() as root:
            path = root / "Sample.per"
            path.write_text(
                """
(load tasks/foo)
(defrule
    (true)
=>
    (do-nothing)
)
""".strip(),
                encoding="utf-8",
            )
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                code = main(["lint", str(path), "--json"])
            source_lines = path.read_text(encoding="utf-8").splitlines()

        self.assertEqual(code, 1)
        payload = json.loads(buffer.getvalue())
        finding = next(
            item for item in payload["findings"]
            if item["code"] == "malformed-load-directive"
        )
        self.assertEqual(
            source_lines[0][
                finding["span"]["start_col"]:finding["span"]["end_col"]
            ],
            "tasks/foo",
        )

    def test_lint_json_spans_malformed_load_random_target(self) -> None:
        with WorkspaceTempDir() as root:
            path = root / "Sample.per"
            path.write_text(
                """
(load-random
    50 strategy-a
)
(defrule
    (true)
=>
    (do-nothing)
)
""".strip(),
                encoding="utf-8",
            )
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                code = main(["lint", str(path), "--json"])
            source_lines = path.read_text(encoding="utf-8").splitlines()

        self.assertEqual(code, 1)
        payload = json.loads(buffer.getvalue())
        finding = next(
            item for item in payload["findings"]
            if item["code"] == "malformed-load-random-directive"
        )
        self.assertEqual(
            source_lines[1][
                finding["span"]["start_col"]:finding["span"]["end_col"]
            ],
            "strategy-a",
        )

    def test_lint_json_spans_malformed_include_target(self) -> None:
        with WorkspaceTempDir() as root:
            path = root / "Sample.per"
            path.write_text(
                """
(include debug.xs)
(defrule
    (true)
=>
    (do-nothing)
)
""".strip(),
                encoding="utf-8",
            )
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                code = main(["lint", str(path), "--json"])
            source_lines = path.read_text(encoding="utf-8").splitlines()

        self.assertEqual(code, 1)
        payload = json.loads(buffer.getvalue())
        finding = next(
            item for item in payload["findings"]
            if item["code"] == "malformed-include-directive"
        )
        self.assertEqual(
            source_lines[0][
                finding["span"]["start_col"]:finding["span"]["end_col"]
            ],
            "debug.xs",
        )

    def test_find_log_cleanup_candidates_preserves_newest_runs(self) -> None:
        with WorkspaceTempDir() as root:
            newest = root / "2026.04.27-0002.00"
            middle = root / "2026.04.27-0001.00"
            oldest = root / "2026.04.27-0000.00"
            for index, path in enumerate([oldest, middle, newest], start=1):
                path.mkdir()
                (path / "MainLog.txt").write_text(str(index), encoding="utf-8")
                os.utime(path, (index, index))

            slow_log = root / "SlowLog"
            slow_log.mkdir()
            old_slow = slow_log / "old.txt"
            new_slow = slow_log / "new.txt"
            old_slow.write_text("old", encoding="utf-8")
            new_slow.write_text("new", encoding="utf-8")
            os.utime(old_slow, (1, 1))
            os.utime(new_slow, (3, 3))

            candidates = find_log_cleanup_candidates(root, keep_latest=2)

        self.assertEqual({candidate.path.name for candidate in candidates}, {"2026.04.27-0000.00", "old.txt"})

    def test_search_registry_cli_prints_matches(self) -> None:
        registry = {
            "concepts": [
                {
                    "id": "duc",
                    "name": "Direct Unit Control",
                    "definition": "Unit control system.",
                    "source_urls": ["https://example.test/duc"],
                    "lookup_terms": ["up-target-point"],
                    "aliases": ["direct control"],
                    "tags": ["duc", "control"],
                    "validation_status": "documented",
                }
            ],
            "articles": [],
            "taxonomies": {},
        }

        with WorkspaceTempDir() as root:
            path = root / "registry.json"
            path.write_text(json.dumps(registry), encoding="utf-8")
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                code = main(["search-registry", "duc", "--path", str(path)])

        self.assertEqual(code, 0)
        output = buffer.getvalue()
        self.assertIn("matches: 1", output)
        self.assertIn("concept\tduc\tDirect Unit Control", output)
        self.assertIn("status: documented", output)
        self.assertIn("aliases: direct control", output)

    def test_resolve_reference_cli_prints_primary_and_related(self) -> None:
        registry = {
            "concepts": [],
            "articles": [],
            "validated_commands": [
                {
                    "id": "cmd-up-target-point",
                    "command_name": "up-target-point",
                    "validated_patterns": ["Observed point targeting path."],
                    "lookup_terms": ["up-target-point"],
                    "validation_status": "observed",
                }
            ],
            "command_inventory": [
                {
                    "name": "up-target-point",
                    "url": "https://airef.github.io/commands/commands-details.html#up-target-point",
                    "description": "Direct local search results to a specific point on the map.",
                    "syntax": "(up-target-point <Point> <DUCAction>)",
                    "command_type": "Action",
                    "complexity": "Very High",
                    "command_category": ["DUC", "Points"],
                    "command_parameters": [{"name": "Point"}, {"name": "DUCAction"}],
                    "related_commands": ["up-target-objects"],
                    "related_strategic_numbers": ["sn-target-point-adjustment"],
                }
            ],
            "taxonomies": {},
        }

        with WorkspaceTempDir() as root:
            path = root / "registry.json"
            path.write_text(json.dumps(registry), encoding="utf-8")
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                code = main(["resolve-reference", "up-target-point", "--path", str(path)])

        self.assertEqual(code, 0)
        output = buffer.getvalue()
        self.assertIn("resolved: 1", output)
        self.assertIn("primary: validated-command\tcmd-up-target-point\tup-target-point", output)
        self.assertIn("related: 1", output)

    def test_lint_cli_corpus_profile_suppresses_alias_noise(self) -> None:
        with WorkspaceTempDir() as root:
            path = root / "sample.per"
            path.write_text(
                """
(defconst class-villager 904)
(defrule
    (true)
=>
    (do-nothing)
)
""".strip(),
                encoding="utf-8",
            )

            default_buffer = io.StringIO()
            with redirect_stdout(default_buffer):
                default_code = main(["lint", str(path)])

            corpus_buffer = io.StringIO()
            with redirect_stdout(corpus_buffer):
                corpus_code = main(["lint", str(path), "--profile", "corpus"])

        self.assertEqual(default_code, 1)
        self.assertIn("builtin-constant-alias", default_buffer.getvalue())
        self.assertEqual(corpus_code, 0)
        self.assertEqual(corpus_buffer.getvalue(), "")

    def test_lint_package_summary_does_not_fail_on_warnings_by_default(self) -> None:
        with WorkspaceTempDir() as root:
            (root / "Warn.ai").write_text('(load "Warn")\n', encoding="utf-8")
            (root / "Warn.per").write_text(
                """
(defconst point-x 100)
(defconst house 70)
(defrule
    (true)
=>
    (up-set-target-point point-x)
    (up-build place-point point-x c: house)
)
""".strip(),
                encoding="utf-8",
            )
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                code = main(["lint-package", str(root), "--summary"])

        self.assertEqual(code, 0)
        output = buffer.getvalue()
        self.assertIn("severity: warning: 1", output)
        self.assertIn("confidence: definite: 1", output)
        self.assertIn("up-build-place-point-coordinate-as-escrow: 1", output)

    def test_lint_package_can_fail_on_warnings(self) -> None:
        with WorkspaceTempDir() as root:
            (root / "Warn.ai").write_text('(load "Warn")\n', encoding="utf-8")
            (root / "Warn.per").write_text(
                """
(defconst point-x 100)
(defconst house 70)
(defrule
    (true)
=>
    (up-set-target-point point-x)
    (up-build place-point point-x c: house)
)
""".strip(),
                encoding="utf-8",
            )
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                code = main(["lint-package", str(root), "--summary", "--fail-level", "warning"])

        self.assertEqual(code, 1)

    def test_lint_package_can_suppress_known_finding_codes(self) -> None:
        with WorkspaceTempDir() as root:
            (root / "Warn.ai").write_text('(load "Warn")\n', encoding="utf-8")
            (root / "Warn.per").write_text(
                """
(defconst point-x 100)
(defconst house 70)
(defrule
    (true)
=>
    (up-set-target-point point-x)
    (up-build place-point point-x c: house)
)
""".strip(),
                encoding="utf-8",
            )
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                code = main(
                    [
                        "lint-package",
                        str(root),
                        "--json",
                        "--fail-level",
                        "warning",
                        "--suppress-code",
                        "up-build-place-point-coordinate-as-escrow",
                    ]
                )

        self.assertEqual(code, 0)
        payload = json.loads(buffer.getvalue())
        self.assertFalse(payload["failed"])
        self.assertEqual(payload["suppressed_codes"], ["up-build-place-point-coordinate-as-escrow"])
        self.assertEqual(payload["roots"][0]["finding_count"], 0)
        self.assertEqual(payload["roots"][0]["findings"], [])
        self.assertEqual(payload["totals"]["finding_count"], 0)

    def test_lint_package_json_reports_structured_results(self) -> None:
        with WorkspaceTempDir() as root:
            (root / "Warn.ai").write_text('(load "Warn")\n', encoding="utf-8")
            (root / "Warn.per").write_text(
                """
(defconst point-x 100)
(defconst house 70)
(defrule
    (true)
=>
    (up-set-target-point point-x)
    (up-build place-point point-x c: house)
)
""".strip(),
                encoding="utf-8",
            )
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                code = main(["lint-package", str(root), "--json"])

        self.assertEqual(code, 0)
        payload = json.loads(buffer.getvalue())
        self.assertFalse(payload["failed"])
        self.assertEqual(payload["root_count"], 1)
        root_payload = payload["roots"][0]
        self.assertEqual(root_payload["finding_count"], 1)
        self.assertEqual(root_payload["finding_groups"][0]["code"], "up-build-place-point-coordinate-as-escrow")
        self.assertEqual(root_payload["finding_groups"][0]["count"], 1)
        self.assertEqual(root_payload["finding_groups"][0]["severity_counts"], {"warning": 1})
        self.assertIn("third argument is still escrow state", root_payload["finding_groups"][0]["explanation"])
        self.assertEqual(root_payload["finding_groups"][0]["examples"][0]["line"], 7)
        self.assertEqual(root_payload["xs_file_count"], 0)
        self.assertEqual(root_payload["xs_files"], [])
        self.assertEqual(root_payload["missing_includes"], [])
        self.assertEqual(root_payload["constant_count"], 2)
        self.assertEqual(
            {constant["name"]: constant["resolved_value"] for constant in root_payload["constants"]},
            {"house": 70, "point-x": 100},
        )
        self.assertEqual(root_payload["severity_counts"], {"warning": 1})
        self.assertEqual(root_payload["code_counts"], {"up-build-place-point-coordinate-as-escrow": 1})
        self.assertEqual(root_payload["confidence_counts"], {"definite": 1})
        self.assertEqual(root_payload["file_confidence_counts"], {"definite": 1})
        self.assertEqual(
            root_payload["file_summaries"],
            [
                {
                    "path": str((root / "Warn.per").resolve()),
                    "confidence": "definite",
                    "finding_count": 1,
                    "severity_counts": {"warning": 1},
                    "code_counts": {"up-build-place-point-coordinate-as-escrow": 1},
                }
            ],
        )
        self.assertFalse(root_payload["failed"])
        self.assertEqual(root_payload["findings"][0]["code"], "up-build-place-point-coordinate-as-escrow")
        self.assertEqual(root_payload["findings"][0]["confidence"], "definite")
        self.assertIsNone(root_payload["findings"][0]["suggestion"])
        self.assertEqual(payload["totals"]["finding_count"], 1)
        self.assertEqual(payload["totals"]["xs_file_count"], 0)
        self.assertEqual(payload["totals"]["severity_counts"], {"warning": 1})
        self.assertEqual(payload["totals"]["code_counts"], {"up-build-place-point-coordinate-as-escrow": 1})
        self.assertEqual(payload["totals"]["confidence_counts"], {"definite": 1})
        self.assertEqual(payload["totals"]["failed_root_count"], 0)
        self.assertEqual(payload["finding_groups"][0]["code"], "up-build-place-point-coordinate-as-escrow")
        self.assertEqual(payload["finding_groups"][0]["examples"][0]["path"], str((root / "Warn.per").resolve()))
        self.assertEqual(payload["issue_groups"][0]["source"], "lint")
        self.assertEqual(payload["issue_groups"][0]["code"], "up-build-place-point-coordinate-as-escrow")

    def test_lint_package_json_marks_error_failures(self) -> None:
        with WorkspaceTempDir() as root:
            (root / "Bad.ai").write_text('(load "Bad")\n', encoding="utf-8")
            (root / "Bad.per").write_text(
                """
(defrule
    (true)
=>
    (up-set-target-by-id g:= target-id)
)
""".strip(),
                encoding="utf-8",
            )
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                code = main(["lint-package", str(root), "--json"])

        self.assertEqual(code, 1)
        payload = json.loads(buffer.getvalue())
        self.assertTrue(payload["failed"])
        self.assertTrue(payload["roots"][0]["failed"])
        self.assertEqual(payload["roots"][0]["severity_counts"], {"error": 1})
        self.assertIn("plain typeOp", payload["roots"][0]["findings"][0]["suggestion"])
        self.assertEqual(payload["roots"][0]["findings"][0]["confidence"], "definite")
        self.assertEqual(payload["totals"]["failed_root_count"], 1)
        self.assertEqual(payload["totals"]["severity_counts"], {"error": 1})

    def test_lint_package_json_reports_conditional_confidence(self) -> None:
        with WorkspaceTempDir() as root:
            (root / "Maybe.ai").write_text('(load "Maybe")\n', encoding="utf-8")
            (root / "Maybe.per").write_text(
                """
#load-if-defined UNKNOWN
(defrule
    (true)
=>
    (up-set-target-by-id g:= target-id)
)
#end-if
""".strip(),
                encoding="utf-8",
            )
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                code = main(["lint-package", str(root), "--json"])

        self.assertEqual(code, 0)
        payload = json.loads(buffer.getvalue())
        self.assertFalse(payload["failed"])
        self.assertFalse(payload["roots"][0]["failed"])
        self.assertEqual(payload["roots"][0]["confidence_counts"], {"conditional": 1})
        self.assertEqual(payload["roots"][0]["findings"][0]["confidence"], "conditional")
        self.assertEqual(payload["totals"]["conditional_error_count"], 1)
        self.assertEqual(payload["totals"]["definite_error_count"], 0)

    def test_lint_package_json_can_fail_on_conditional_errors(self) -> None:
        with WorkspaceTempDir() as root:
            (root / "Maybe.ai").write_text('(load "Maybe")\n', encoding="utf-8")
            (root / "Maybe.per").write_text(
                """
#load-if-defined UNKNOWN
(defrule
    (true)
=>
    (up-set-target-by-id g:= target-id)
)
#end-if
""".strip(),
                encoding="utf-8",
            )
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                code = main(["lint-package", str(root), "--json", "--fail-confidence", "conditional"])

        self.assertEqual(code, 1)
        payload = json.loads(buffer.getvalue())
        self.assertTrue(payload["failed"])
        self.assertTrue(payload["roots"][0]["failed"])

    def test_lint_package_json_reports_integrity(self) -> None:
        with WorkspaceTempDir() as root:
            (root / "Good.ai").write_text('(load "Good")\n', encoding="utf-8")
            (root / "Good.per").write_text("(defrule\n    (true)\n=>\n    (do-nothing)\n)\n", encoding="utf-8")
            (root / "Broken.ai").write_text('(load "Missing")\n', encoding="utf-8")
            (root / "Unused.per").write_text("(defconst unused 1)\n", encoding="utf-8")
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                code = main(["lint-package", str(root), "--json"])

        self.assertEqual(code, 1)
        payload = json.loads(buffer.getvalue())
        self.assertTrue(payload["failed"])
        self.assertEqual(payload["integrity"]["stale_ai_root_count"], 1)
        self.assertEqual(payload["integrity"]["unreachable_per_file_count"], 1)
        self.assertEqual(payload["integrity"]["severity_counts"], {"error": 1, "info": 1})
        self.assertEqual(payload["integrity"]["code_counts"], {"stale-ai-root": 1, "unreachable-per-file": 1})
        manifest_by_name = {
            Path(entry["ai_path"]).name: entry
            for entry in payload["integrity"]["root_manifest"]
        }
        self.assertEqual(manifest_by_name["Good.ai"]["status"], "resolved")
        self.assertEqual(manifest_by_name["Good.ai"]["entries"][0]["source"], "load")
        self.assertEqual(manifest_by_name["Broken.ai"]["status"], "stale")
        self.assertEqual(manifest_by_name["Broken.ai"]["entries"][0]["status"], "unresolved")
        self.assertEqual(payload["integrity"]["stale_ai_roots"][0]["ai_path"], str(root / "Broken.ai"))
        self.assertEqual(payload["integrity"]["unreachable_per_files"], [str((root / "Unused.per").resolve())])
        self.assertEqual(
            [(group["source"], group["code"], group["count"]) for group in payload["issue_groups"]],
            [
                ("integrity", "stale-ai-root", 1),
                ("integrity", "unreachable-per-file", 1),
            ],
        )
        self.assertEqual(payload["issue_groups"][0]["examples"][0]["path"], str(root / "Broken.ai"))
        self.assertEqual(payload["totals"]["stale_ai_root_count"], 1)
        self.assertEqual(payload["totals"]["unreachable_per_file_count"], 1)
        self.assertEqual(payload["totals"]["integrity_severity_counts"], {"error": 1, "info": 1})

    def test_lint_package_can_fail_on_integrity_warnings(self) -> None:
        with WorkspaceTempDir() as root:
            (root / "One.ai").write_text('(load "Shared")\n', encoding="utf-8")
            (root / "Two.ai").write_text('(load "Shared")\n', encoding="utf-8")
            (root / "Shared.per").write_text("(defrule\n    (true)\n=>\n    (do-nothing)\n)\n", encoding="utf-8")
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                code = main(["lint-package", str(root), "--json", "--fail-level", "warning"])

        self.assertEqual(code, 1)
        payload = json.loads(buffer.getvalue())
        self.assertTrue(payload["failed"])
        self.assertEqual(payload["integrity"]["severity_counts"], {"warning": 1})

    def test_lint_package_can_fail_on_integrity_info(self) -> None:
        with WorkspaceTempDir() as root:
            (root / "Good.ai").write_text('(load "Good")\n', encoding="utf-8")
            (root / "Good.per").write_text("(defrule\n    (true)\n=>\n    (do-nothing)\n)\n", encoding="utf-8")
            (root / "Unused.per").write_text("(defconst unused 1)\n", encoding="utf-8")
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                code = main(["lint-package", str(root), "--json", "--fail-level", "info"])

        self.assertEqual(code, 1)
        payload = json.loads(buffer.getvalue())
        self.assertTrue(payload["failed"])
        self.assertEqual(payload["integrity"]["severity_counts"], {"info": 1})

    def test_lint_package_json_reports_missing_load_candidates(self) -> None:
        with WorkspaceTempDir() as root:
            (root / "Main.ai").write_text('(load "Main")\n', encoding="utf-8")
            (root / "Main.per").write_text('(load "missing/path")\n', encoding="utf-8")
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                code = main(["lint-package", str(root), "--json"])

        self.assertEqual(code, 1)
        payload = json.loads(buffer.getvalue())
        missing = payload["roots"][0]["missing_loads"][0]
        self.assertEqual(missing["include"], "missing/path")
        self.assertEqual(missing["confidence"], "definite")
        self.assertTrue(missing["candidates"])
        self.assertIn("tried", payload["roots"][0]["findings"][0]["message"])

    def test_lint_package_output_writes_json_file(self) -> None:
        with WorkspaceTempDir() as root:
            output_path = root / "reports" / "package.json"
            (root / "Good.ai").write_text('(load "Good")\n', encoding="utf-8")
            (root / "Good.per").write_text("(defrule\n    (true)\n=>\n    (do-nothing)\n)\n", encoding="utf-8")
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                code = main(["lint-package", str(root), "--output", str(output_path)])
            payload = json.loads(output_path.read_text(encoding="utf-8"))

        self.assertEqual(code, 0)
        self.assertEqual(buffer.getvalue().strip(), str(output_path))
        self.assertFalse(payload["failed"])
        self.assertEqual(payload["root_count"], 1)
        self.assertEqual(Path(payload["integrity"]["root_manifest"][0]["ai_path"]).name, "Good.ai")

    def test_lint_package_report_writes_verbose_markdown(self) -> None:
        with WorkspaceTempDir() as root:
            report_path = root / "reports" / "package.md"
            (root / "Warn.ai").write_text('(load "Warn")\n', encoding="utf-8")
            (root / "Warn.per").write_text(
                """
(defconst point-x 100)
(defconst house 70)
(defrule
    (true)
=>
    (up-set-target-point point-x)
    (up-build place-point point-x c: house)
)
""".strip(),
                encoding="utf-8",
            )
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                code = main(["lint-package", str(root), "--report", str(report_path)])
            report = report_path.read_text(encoding="utf-8")

        self.assertEqual(code, 0)
        self.assertEqual(buffer.getvalue().strip(), str(report_path))
        self.assertIn("# AI Package Validation Report", report)
        self.assertIn("## Summary", report)
        self.assertIn("## Issue Categories", report)
        self.assertLess(report.index("## Issue Categories"), report.index("## Root Manifest"))
        self.assertIn("### `up-build-place-point-coordinate-as-escrow`", report)
        self.assertIn("third argument is escrow state", report)
        self.assertIn("Warn.per:7", report)

    def test_lint_package_root_manifest_reports_skipped_load_random_entries(self) -> None:
        with WorkspaceTempDir() as root:
            (root / "Random.ai").write_text(
                """
(load-random
    0 "Disabled"
    100 "Enabled"
)
""".strip(),
                encoding="utf-8",
            )
            (root / "Disabled.per").write_text("(defconst disabled 0)\n", encoding="utf-8")
            (root / "Enabled.per").write_text("(defconst enabled 1)\n", encoding="utf-8")
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                code = main(["lint-package", str(root), "--json"])

        self.assertEqual(code, 0)
        payload = json.loads(buffer.getvalue())
        entries = payload["integrity"]["root_manifest"][0]["entries"]
        self.assertEqual([entry["source"] for entry in entries], ["load-random", "load-random"])
        self.assertEqual(entries[0]["status"], "skipped")
        self.assertEqual(entries[0]["skipped_reason"], "zero-or-negative-weight")
        self.assertEqual(entries[1]["status"], "resolved")

    def test_lint_package_json_reports_included_xs_files(self) -> None:
        with WorkspaceTempDir() as root:
            (root / "Main.ai").write_text('(load "Main")\n', encoding="utf-8")
            (root / "Main.per").write_text('(include "debug.xs")\n', encoding="utf-8")
            (root / "debug.xs").write_text("void main() { xsGetUnitTargetId(1); }\n", encoding="utf-8")
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                code = main(["lint-package", str(root), "--json"])

        self.assertEqual(code, 1)
        payload = json.loads(buffer.getvalue())
        root_payload = payload["roots"][0]
        self.assertEqual(root_payload["xs_file_count"], 1)
        self.assertEqual(root_payload["xs_files"], [str((root / "debug.xs").resolve())])
        self.assertEqual(root_payload["findings"][0]["path"], str((root / "debug.xs").resolve()))
        self.assertEqual(root_payload["findings"][0]["code"], "unsupported-ai-xs-function")
        self.assertEqual(payload["totals"]["xs_file_count"], 1)

    def test_lint_package_json_groups_xs_script_call_target_findings(self) -> None:
        with WorkspaceTempDir() as root:
            (root / "Main.ai").write_text('(load "Main")\n', encoding="utf-8")
            (root / "Main.per").write_text(
                """
(include "debug.xs")
(defrule
    (true)
=>
    (xs-script-call "needsArg")
)
""".strip(),
                encoding="utf-8",
            )
            (root / "debug.xs").write_text("void needsArg(int value = 0) {}\n", encoding="utf-8")
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                code = main(["lint-package", str(root), "--json"])

        self.assertEqual(code, 0)
        payload = json.loads(buffer.getvalue())
        root_payload = payload["roots"][0]
        self.assertEqual(root_payload["severity_counts"], {"warning": 1})
        self.assertEqual(root_payload["finding_groups"][0]["code"], "xs-script-call-parameterized-function")
        self.assertEqual(payload["issue_groups"][0]["code"], "xs-script-call-parameterized-function")
        self.assertEqual(payload["issue_groups"][0]["severity_counts"], {"warning": 1})


if __name__ == "__main__":
    unittest.main()
