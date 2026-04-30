from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from aoe2_ai_lab.ai_package import (
    collect_reachable_per_files,
    find_package_roots,
    inspect_package_integrity,
    lint_package_root,
)
from aoe2_ai_lab.linter import lint_file


class AiPackageTests(unittest.TestCase):
    def test_collects_recursive_loads_and_load_random_entries(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "main.per").write_text(
                """
(defconst root-const 1)
(load "shared")
(load-random
    0 "disabled-variant"
    50 "variant-a"
    "variant-b"
)
""".strip(),
                encoding="utf-8",
            )
            (root / "shared.per").write_text("(defconst shared-const 2)\n", encoding="utf-8")
            (root / "variant-a.per").write_text("(defconst a-const 3)\n", encoding="utf-8")
            (root / "variant-b.per").write_text("(defconst b-const 4)\n", encoding="utf-8")

            files, missing = collect_reachable_per_files(root / "main.per")

        self.assertEqual(missing, [])
        self.assertEqual(
            [path.name for path in files],
            ["main.per", "shared.per", "variant-a.per", "variant-b.per"],
        )

    def test_collects_inline_and_plus_load_random_entries(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "main.per").write_text(
                '(load-random 20 "variant-a" +dynamic-chance "variant-b" + "variant-c" 0 "disabled")\n',
                encoding="utf-8",
            )
            (root / "variant-a.per").write_text("(defconst a-const 1)\n", encoding="utf-8")
            (root / "variant-b.per").write_text("(defconst b-const 2)\n", encoding="utf-8")
            (root / "variant-c.per").write_text("(defconst c-const 3)\n", encoding="utf-8")
            (root / "disabled.per").write_text("(defconst disabled 4)\n", encoding="utf-8")

            files, missing = collect_reachable_per_files(root / "main.per")

        self.assertEqual(missing, [])
        self.assertEqual(
            [path.name for path in files],
            ["main.per", "variant-a.per", "variant-b.per", "variant-c.per"],
        )

    def test_collects_load_random_entries_after_quoted_closing_paren(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "main.per").write_text(
                """
(load-random
    50 "variant)one"
    50 "variant-two"
)
""".strip(),
                encoding="utf-8",
            )
            (root / "variant)one.per").write_text("(defconst a-const 1)\n", encoding="utf-8")
            (root / "variant-two.per").write_text("(defconst b-const 2)\n", encoding="utf-8")

            files, missing = collect_reachable_per_files(root / "main.per")

        self.assertEqual(missing, [])
        self.assertEqual([path.name for path in files], ["main.per", "variant)one.per", "variant-two.per"])

    def test_find_package_roots_uses_ai_load_or_matching_per(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Loaded.ai").write_text('(load "scripts/main")\n', encoding="utf-8")
            scripts = root / "scripts"
            scripts.mkdir()
            (scripts / "main.per").write_text("(defrule\n    (true)\n=>\n    (do-nothing)\n)\n", encoding="utf-8")
            (root / "Named.ai").write_text("", encoding="utf-8")
            (root / "Named.per").write_text("(defrule\n    (true)\n=>\n    (do-nothing)\n)\n", encoding="utf-8")

            roots = find_package_roots(root)

        self.assertEqual([package_root.ai_path.name for package_root in roots], ["Loaded.ai", "Named.ai"])
        self.assertEqual([package_root.per_path.name for package_root in roots], ["main.per", "Named.per"])

    def test_find_package_roots_accepts_single_ai_file(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            ai_path = root / "Loaded.ai"
            ai_path.write_text('(load "scripts/main")\n', encoding="utf-8")
            scripts = root / "scripts"
            scripts.mkdir()
            (scripts / "main.per").write_text("(defrule\n    (true)\n=>\n    (do-nothing)\n)\n", encoding="utf-8")
            (root / "unused.per").write_text("(defconst unused 1)\n", encoding="utf-8")

            roots = find_package_roots(ai_path)
            integrity = inspect_package_integrity(ai_path)

        self.assertEqual(len(roots), 1)
        self.assertEqual(roots[0].ai_path.name, "Loaded.ai")
        self.assertEqual(roots[0].per_path.name, "main.per")
        self.assertEqual(integrity.package_dir, root)
        self.assertEqual([package_root.per_path.name for package_root in integrity.roots], ["main.per"])
        self.assertEqual(integrity.unreachable_per_files, [])

    def test_find_package_roots_accepts_single_per_file(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            per_path = root / "standalone.per"
            per_path.write_text(
                """
(load "shared")
(defrule
    (true)
=>
    (do-nothing)
)
""".strip(),
                encoding="utf-8",
            )
            (root / "shared.per").write_text("(defconst shared-const 1)\n", encoding="utf-8")
            (root / "unused.per").write_text("(defconst unused 1)\n", encoding="utf-8")

            roots = find_package_roots(per_path)
            integrity = inspect_package_integrity(per_path)
            result = lint_package_root(roots[0])

        self.assertEqual(len(roots), 1)
        self.assertEqual(roots[0].ai_path.name, "standalone.per")
        self.assertEqual(roots[0].per_path.name, "standalone.per")
        self.assertEqual(integrity.package_dir, root)
        self.assertEqual([package_root.per_path.name for package_root in integrity.roots], ["standalone.per"])
        self.assertEqual(integrity.unreachable_per_files, [])
        self.assertEqual([path.name for path in result.files], ["standalone.per", "shared.per"])

    def test_find_package_roots_keeps_multiple_ai_loads(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Multi.ai").write_text('(load "One")\n(load "Two")\n', encoding="utf-8")
            (root / "One.per").write_text("(defconst one 1)\n", encoding="utf-8")
            (root / "Two.per").write_text("(defconst two 2)\n", encoding="utf-8")

            roots = find_package_roots(root)
            integrity = inspect_package_integrity(root)

        self.assertEqual([package_root.ai_path.name for package_root in roots], ["Multi.ai", "Multi.ai"])
        self.assertEqual([package_root.per_path.name for package_root in roots], ["One.per", "Two.per"])
        self.assertEqual([package_root.per_path.name for package_root in integrity.roots], ["One.per", "Two.per"])
        self.assertEqual(integrity.unreachable_per_files, [])

    def test_find_package_roots_uses_ai_load_random_entries(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Random.ai").write_text(
                """
(load-random
    0 "Disabled"
    70 "One"
    30 "Two"
)
""".strip(),
                encoding="utf-8",
            )
            (root / "Disabled.per").write_text("(defconst disabled 0)\n", encoding="utf-8")
            (root / "One.per").write_text("(defconst one 1)\n", encoding="utf-8")
            (root / "Two.per").write_text("(defconst two 2)\n", encoding="utf-8")

            roots = find_package_roots(root)
            integrity = inspect_package_integrity(root)

        self.assertEqual([package_root.ai_path.name for package_root in roots], ["Random.ai", "Random.ai"])
        self.assertEqual([package_root.per_path.name for package_root in roots], ["One.per", "Two.per"])
        self.assertEqual([path.name for path in integrity.unreachable_per_files], ["Disabled.per"])

    def test_package_lint_uses_reachable_constants(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Main.ai").write_text('(load "main")\n', encoding="utf-8")
            (root / "main.per").write_text(
                """
(load "constants")
(defrule
    (true)
=>
    (up-find-local c: custom-unit c: 1)
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )
            (root / "constants.per").write_text("(defconst custom-unit 83)\n", encoding="utf-8")

            result = lint_package_root(find_package_roots(root)[0])

        self.assertEqual(result.missing_loads, [])
        self.assertEqual(result.findings, [])

    def test_package_lint_reports_malformed_load_random_entries(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Main.ai").write_text('(load "main")\n', encoding="utf-8")
            (root / "main.per").write_text(
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

            result = lint_package_root(find_package_roots(root)[0])

        self.assertEqual(result.missing_loads, [])
        self.assertEqual([finding.code for _, finding in result.findings], ["malformed-load-random-directive"])

    def test_package_lint_keeps_load_random_open_when_target_contains_closing_paren(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Main.ai").write_text('(load "main")\n', encoding="utf-8")
            (root / "main.per").write_text(
                """
(load-random
    50 "strategy)one"
    50 "strategy-two"
)
""".strip(),
                encoding="utf-8",
            )
            (root / "strategy)one.per").write_text("(defrule (true) => (do-nothing))\n", encoding="utf-8")
            (root / "strategy-two.per").write_text("(defrule (true) => (do-nothing))\n", encoding="utf-8")

            result = lint_package_root(find_package_roots(root)[0])

        self.assertEqual(result.missing_loads, [])
        self.assertEqual(result.findings, [])
        self.assertEqual([path.name for path in result.files], ["main.per", "strategy)one.per", "strategy-two.per"])

    def test_package_lint_uses_reachable_constant_values(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Main.ai").write_text('(load "main")\n', encoding="utf-8")
            (root / "main.per").write_text(
                """
(load "constants")
(defrule
    (true)
=>
    (up-get-point position-self low-point)
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )
            (root / "constants.per").write_text("(defconst low-point 5)\n", encoding="utf-8")

            result = lint_package_root(find_package_roots(root)[0])

        self.assertEqual(result.missing_loads, [])
        self.assertEqual([finding.code for _, finding in result.findings], ["unsafe-goal-block"])

    def test_package_lint_resolves_reachable_constant_alias_values(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Main.ai").write_text('(load "main")\n', encoding="utf-8")
            (root / "main.per").write_text(
                """
(load "constants")
(defrule
    (true)
=>
    (set-goal gl-invalid 1)
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )
            (root / "constants.per").write_text(
                """
(defconst gl-zero 0)
(defconst gl-invalid gl-zero)
""".strip(),
                encoding="utf-8",
            )

            result = lint_package_root(find_package_roots(root)[0])

        self.assertEqual(result.missing_loads, [])
        self.assertEqual([finding.code for _, finding in result.findings], ["command-numeric-range-mismatch"])

    def test_package_lint_reports_cross_file_defconst_alias_cycle(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Main.ai").write_text('(load "main")\n', encoding="utf-8")
            (root / "main.per").write_text(
                """
(load "constants")
(defconst gl-a gl-b)
(defrule
    (true)
=>
    (do-nothing)
)
""".strip(),
                encoding="utf-8",
            )
            (root / "constants.per").write_text("(defconst gl-b gl-a)\n", encoding="utf-8")

            result = lint_package_root(find_package_roots(root)[0])

        self.assertEqual(result.missing_loads, [])
        self.assertEqual([finding.code for _, finding in result.findings], ["defconst-alias-cycle"])

    def test_package_lint_ignores_conditional_cross_file_defconst_alias_cycle(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Main.ai").write_text('(load "main")\n', encoding="utf-8")
            (root / "main.per").write_text(
                """
(load "constants")
#load-if-defined UNKNOWN
(defconst gl-a gl-b)
#end-if
(defrule
    (true)
=>
    (do-nothing)
)
""".strip(),
                encoding="utf-8",
            )
            (root / "constants.per").write_text("(defconst gl-b gl-a)\n", encoding="utf-8")

            result = lint_package_root(find_package_roots(root)[0])

        self.assertEqual(result.missing_loads, [])
        self.assertEqual(result.findings, [])

    def test_package_lint_reports_cross_file_defconst_conflict_in_default_profile(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Main.ai").write_text('(load "main")\n', encoding="utf-8")
            (root / "main.per").write_text(
                """
(load "constants")
(defconst gl-state 1)
(defrule
    (true)
=>
    (do-nothing)
)
""".strip(),
                encoding="utf-8",
            )
            (root / "constants.per").write_text("(defconst gl-state 2)\n", encoding="utf-8")

            result = lint_package_root(find_package_roots(root)[0], profile="default")

        self.assertEqual(result.missing_loads, [])
        self.assertEqual([finding.code for _, finding in result.findings], ["duplicate-defconst-conflict"])

    def test_package_lint_exposes_package_constant_symbol_table(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Main.ai").write_text('(load "main")\n', encoding="utf-8")
            (root / "main.per").write_text(
                """
(load "constants")
(defconst gl-state gl-open)
""".strip(),
                encoding="utf-8",
            )
            (root / "constants.per").write_text("(defconst gl-open 7)\n", encoding="utf-8")

            result = lint_package_root(find_package_roots(root)[0], profile="default")

        by_name = {constant.name: constant for constant in result.constants}
        self.assertEqual(by_name["gl-open"].value, "7")
        self.assertEqual(by_name["gl-open"].resolved_value, 7)
        self.assertEqual(by_name["gl-state"].value, "gl-open")
        self.assertEqual(by_name["gl-state"].resolved_value, 7)

    def test_package_lint_does_not_duplicate_file_local_defconst_conflict(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Main.ai").write_text('(load "main")\n', encoding="utf-8")
            (root / "main.per").write_text(
                """
(defconst gl-state 1)
(defconst gl-state 2)
(defrule
    (true)
=>
    (do-nothing)
)
""".strip(),
                encoding="utf-8",
            )

            result = lint_package_root(find_package_roots(root)[0], profile="default")

        self.assertEqual(result.missing_loads, [])
        self.assertEqual([finding.code for _, finding in result.findings], ["duplicate-defconst-conflict"])

    def test_package_lint_suppresses_cross_file_defconst_conflict_in_corpus_profile(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Main.ai").write_text('(load "main")\n', encoding="utf-8")
            (root / "main.per").write_text(
                """
(load "constants")
(defconst gl-state 1)
(defrule
    (true)
=>
    (do-nothing)
)
""".strip(),
                encoding="utf-8",
            )
            (root / "constants.per").write_text("(defconst gl-state 2)\n", encoding="utf-8")

            result = lint_package_root(find_package_roots(root)[0], profile="corpus")

        self.assertEqual(result.missing_loads, [])
        self.assertEqual(result.findings, [])

    def test_package_lint_ignores_conditional_cross_file_defconst_conflict(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Main.ai").write_text('(load "main")\n', encoding="utf-8")
            (root / "main.per").write_text(
                """
(load "constants")
#load-if-defined UNKNOWN
(defconst gl-state 1)
#end-if
(defrule
    (true)
=>
    (do-nothing)
)
""".strip(),
                encoding="utf-8",
            )
            (root / "constants.per").write_text("(defconst gl-state 2)\n", encoding="utf-8")

            result = lint_package_root(find_package_roots(root)[0], profile="default")

        self.assertEqual(result.missing_loads, [])
        self.assertEqual(result.findings, [])

    def test_package_lint_reports_cross_file_quoted_defconst_conflict(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Main.ai").write_text('(load "main")\n', encoding="utf-8")
            (root / "main.per").write_text(
                """
(load "constants")
(defconst greeting "hello")
(defrule
    (true)
=>
    (do-nothing)
)
""".strip(),
                encoding="utf-8",
            )
            (root / "constants.per").write_text('(defconst greeting "bye")\n', encoding="utf-8")

            result = lint_package_root(find_package_roots(root)[0], profile="default")

        self.assertEqual(result.missing_loads, [])
        self.assertEqual([finding.code for _, finding in result.findings], ["duplicate-defconst-conflict"])

    def test_package_lint_reports_cross_file_multi_word_quoted_defconst_conflict(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Main.ai").write_text('(load "main")\n', encoding="utf-8")
            (root / "main.per").write_text(
                """
(load "constants")
(defconst greeting "hello world")
(defrule
    (true)
=>
    (do-nothing)
)
""".strip(),
                encoding="utf-8",
            )
            (root / "constants.per").write_text('(defconst greeting "bye world")\n', encoding="utf-8")

            result = lint_package_root(find_package_roots(root)[0], profile="default")

        self.assertEqual(result.missing_loads, [])
        self.assertEqual([finding.code for _, finding in result.findings], ["duplicate-defconst-conflict"])

    def test_file_lint_uses_extra_constant_values(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (true)
=>
    (up-get-point position-self low-point)
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(
                path,
                extra_constants={"low-point"},
                extra_constant_values={"low-point": 5},
            )

        self.assertEqual([finding.code for finding in findings], ["unsafe-goal-block"])

    def test_package_lint_resolves_package_root_relative_loads(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            package = root / "Example AI"
            nested = package / "Civs" / "Mayans"
            package.mkdir()
            nested.mkdir(parents=True)
            (package / "Example AI.ai").write_text('(load "Example AI/Civs/Mayans/Loads")\n', encoding="utf-8")
            (nested / "Loads.per").write_text(
                '(load "Example AI/Maps/Arabia/Strategic Numbers")\n',
                encoding="utf-8",
            )
            maps = package / "Maps" / "Arabia"
            maps.mkdir(parents=True)
            (maps / "Strategic Numbers.per").write_text("(defconst custom-unit 83)\n", encoding="utf-8")

            result = lint_package_root(find_package_roots(root)[0])

        self.assertEqual(result.missing_loads, [])
        self.assertEqual([path.name for path in result.files], ["Loads.per", "Strategic Numbers.per"])

    def test_package_lint_reports_load_cycles(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Main.ai").write_text('(load "a")\n', encoding="utf-8")
            (root / "a.per").write_text('(load "b")\n', encoding="utf-8")
            (root / "b.per").write_text('(load "a")\n', encoding="utf-8")

            result = lint_package_root(find_package_roots(root)[0])

        self.assertEqual([path.name for path in result.files], ["a.per", "b.per"])
        self.assertEqual(result.findings[0][0].name, "b.per")
        self.assertEqual(result.findings[0][1].code, "load-cycle")
        self.assertIn("a.per -> b.per -> a.per", result.findings[0][1].message)

    def test_package_lint_reports_excessive_load_depth(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Main.ai").write_text('(load "level0")\n', encoding="utf-8")
            for index in range(12):
                next_line = f'(load "level{index + 1}")\n' if index < 11 else ""
                (root / f"level{index}.per").write_text(next_line, encoding="utf-8")

            result = lint_package_root(find_package_roots(root)[0])

        self.assertEqual(result.findings[0][0].name, "level10.per")
        self.assertEqual(result.findings[0][1].code, "load-depth-exceeded")
        self.assertIn("maximum nested load depth 10", result.findings[0][1].message)

    def test_package_integrity_reports_stale_ai_and_unreachable_per_files(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Good.ai").write_text('(load "Good")\n', encoding="utf-8")
            (root / "Good.per").write_text("(defrule\n    (true)\n=>\n    (do-nothing)\n)\n", encoding="utf-8")
            (root / "Broken.ai").write_text('(load "Missing")\n', encoding="utf-8")
            (root / "Unused.per").write_text("(defconst unused 1)\n", encoding="utf-8")

            result = inspect_package_integrity(root)

        self.assertEqual([package_root.ai_path.name for package_root in result.roots], ["Good.ai"])
        self.assertEqual([stale.ai_path.name for stale in result.stale_ai_roots], ["Broken.ai"])
        self.assertIn("Missing.per", result.stale_ai_roots[0].message)
        self.assertEqual([path.name for path in result.unreachable_per_files], ["Unused.per"])

    def test_package_integrity_reports_duplicate_root_targets(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "One.ai").write_text('(load "Shared")\n', encoding="utf-8")
            (root / "Two.ai").write_text('(load "Shared")\n', encoding="utf-8")
            (root / "Shared.per").write_text("(defrule\n    (true)\n=>\n    (do-nothing)\n)\n", encoding="utf-8")

            result = inspect_package_integrity(root)

        self.assertEqual(len(result.duplicate_root_targets), 1)
        ai_names = sorted(path.name for paths in result.duplicate_root_targets.values() for path in paths)
        self.assertEqual(ai_names, ["One.ai", "Two.ai"])

    def test_package_integrity_reports_duplicate_ai_names(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            nested = root / "nested"
            nested.mkdir()
            (root / "Scout.ai").write_text('(load "Scout")\n', encoding="utf-8")
            (root / "Scout.per").write_text("(defrule\n    (true)\n=>\n    (do-nothing)\n)\n", encoding="utf-8")
            (nested / "Scout.ai").write_text('(load "Scout")\n', encoding="utf-8")
            (nested / "Scout.per").write_text("(defrule\n    (true)\n=>\n    (do-nothing)\n)\n", encoding="utf-8")

            result = inspect_package_integrity(root)

        self.assertEqual(sorted(result.duplicate_ai_names), ["scout"])
        self.assertEqual(sorted(path.name for path in result.duplicate_ai_names["scout"]), ["Scout.ai", "Scout.ai"])

    def test_collect_reachable_files_ignores_known_inactive_loads(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "main.per").write_text(
                """
(defconst ENABLED 1)
#load-if-not-defined ENABLED
(load "inactive")
#else
(load "active")
#end-if
""".strip(),
                encoding="utf-8",
            )
            (root / "active.per").write_text("(defconst active 1)\n", encoding="utf-8")
            (root / "inactive.per").write_text("(defconst inactive 1)\n", encoding="utf-8")

            files, missing = collect_reachable_per_files(root / "main.per")

        self.assertEqual(missing, [])
        self.assertEqual([path.name for path in files], ["main.per", "active.per"])

    def test_collect_reachable_files_keeps_unknown_inline_conditional_loads(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "main.per").write_text(
                '#load-if-defined UNKNOWN (load "maybe-active") #end-if\n',
                encoding="utf-8",
            )
            (root / "maybe-active.per").write_text("(defconst maybe-active 1)\n", encoding="utf-8")

            files, missing = collect_reachable_per_files(root / "main.per")

        self.assertEqual(missing, [])
        self.assertEqual([path.name for path in files], ["main.per", "maybe-active.per"])

    def test_missing_load_records_candidate_paths(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            nested = root / "nested"
            nested.mkdir()
            (nested / "main.per").write_text('(load "shared/missing")\n', encoding="utf-8")

            files, missing = collect_reachable_per_files(nested / "main.per", package_root=root)

        self.assertEqual([path.name for path in files], ["main.per"])
        self.assertEqual(len(missing), 1)
        self.assertEqual(missing[0].include, "shared/missing")
        self.assertEqual(missing[0].line, 1)
        self.assertEqual(
            [path.name for path in missing[0].candidates],
            ["missing.per", "missing.per"],
        )
        self.assertIn(str(root / "shared" / "missing.per"), [str(path) for path in missing[0].candidates])

    def test_package_lint_tracks_conditional_reachable_file_confidence(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Main.ai").write_text('(load "main")\n', encoding="utf-8")
            (root / "main.per").write_text(
                '#load-if-defined UNKNOWN (load "maybe-active") #end-if\n',
                encoding="utf-8",
            )
            (root / "maybe-active.per").write_text(
                """
(defrule
    (true)
=>
    (up-set-target-by-id g:= target-id)
)
""".strip(),
                encoding="utf-8",
            )

            result = lint_package_root(find_package_roots(root)[0])

        confidence_by_name = {path.name: result.file_confidence[path.resolve()] for path in result.files}
        self.assertEqual(confidence_by_name, {"main.per": "definite", "maybe-active.per": "conditional"})
        self.assertEqual(result.findings[0][1].confidence, "conditional")

    def test_package_lint_lints_included_xs_files(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Main.ai").write_text('(load "main")\n', encoding="utf-8")
            (root / "main.per").write_text('(include "debug.xs")\n', encoding="utf-8")
            (root / "debug.xs").write_text("void main() { xsGetUnitTargetId(1); }\n", encoding="utf-8")

            result = lint_package_root(find_package_roots(root)[0])

        self.assertEqual([path.name for path in result.xs_files], ["debug.xs"])
        self.assertEqual(result.missing_includes, [])
        self.assertEqual(result.findings[0][0].name, "debug.xs")
        self.assertEqual(result.findings[0][1].code, "unsupported-ai-xs-function")

    def test_package_lint_flags_xs_script_call_to_parameterized_function(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Main.ai").write_text('(load "main")\n', encoding="utf-8")
            (root / "main.per").write_text(
                """
(defconst max-fn "max")
(include "debug.xs")
(defrule
    (xs-script-call max-fn)
=>
    (xs-script-call "helloWorld")
)
""".strip(),
                encoding="utf-8",
            )
            (root / "debug.xs").write_text(
                """
float max(float a = 0.0, float b = 2.0) { return(a); }
bool helloWorld() { return(true); }
""".strip(),
                encoding="utf-8",
            )

            result = lint_package_root(find_package_roots(root)[0], profile="default")

        findings = [finding for _, finding in result.findings]
        self.assertEqual([finding.code for finding in findings], ["xs-script-call-parameterized-function"])
        self.assertIn("'max'", findings[0].message)
        self.assertIn("2 parameter", findings[0].message)

    def test_package_lint_reports_missing_includes(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Main.ai").write_text('(load "main")\n', encoding="utf-8")
            (root / "main.per").write_text('(include "missing.xs")\n', encoding="utf-8")

            result = lint_package_root(find_package_roots(root)[0])

        self.assertEqual(len(result.missing_includes), 1)
        self.assertEqual(result.missing_includes[0].include, "missing.xs")
        self.assertEqual(result.findings[0][1].code, "missing-include-target")


if __name__ == "__main__":
    unittest.main()
