from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
import sys
import tempfile
import unittest

from aoe2_ai_lab.cli import main
from aoe2_ai_lab.formatter import FormatOptions, format_text


class FormatterTests(unittest.TestCase):
    def test_per_gets_final_newline(self) -> None:
        self.assertEqual(format_text("(defrule\n)", ".per"), "(defrule\n)\n")

    def test_ai_files_are_enforced_empty(self) -> None:
        self.assertEqual(format_text("(load \"bot\")\n", ".ai"), "")

    def test_rejects_line_length_above_engine_limit(self) -> None:
        with self.assertRaises(ValueError):
            FormatOptions(max_line_length=256)

    def test_wraps_long_comment_lines(self) -> None:
        text = "; " + "alpha " * 20 + "\n"
        formatted = format_text(text, ".per", FormatOptions(max_line_length=60))
        lines = formatted.splitlines()

        self.assertGreater(len(lines), 1)
        self.assertTrue(all(line.startswith("; ") for line in lines))
        self.assertTrue(all(len(line) <= 60 for line in lines))

    def test_promotes_overlong_inline_comment_above_code_with_blank_line(self) -> None:
        text = "(set-goal gl-test 1) ; " + "comment " * 15 + "\n"
        formatted = format_text(text, ".per", FormatOptions(max_line_length=70))
        lines = formatted.splitlines()

        self.assertTrue(lines[0].startswith("; "))
        self.assertEqual(lines[-1], "(set-goal gl-test 1)")
        self.assertTrue(all(len(line) <= 70 for line in lines if line))

    def test_promotes_overlong_inline_comment_above_later_code_with_blank_line(self) -> None:
        text = "(true)\n(set-goal gl-test 1) ; " + "comment " * 15 + "\n"
        formatted = format_text(text, ".per", FormatOptions(max_line_length=70))
        lines = formatted.splitlines()

        self.assertEqual(lines[0], "(true)")
        self.assertEqual(lines[1], "")
        self.assertTrue(lines[2].startswith("; "))
        self.assertEqual(lines[-1], "(set-goal gl-test 1)")
        self.assertTrue(all(len(line) <= 70 for line in lines if line))

    def test_promoted_inline_comment_reuses_existing_blank_line(self) -> None:
        text = "(true)\n\n(set-goal gl-test 1) ; " + "comment " * 15 + "\n"
        formatted = format_text(text, ".per", FormatOptions(max_line_length=70))
        lines = formatted.splitlines()

        self.assertEqual(lines[0], "(true)")
        self.assertEqual(lines[1], "")
        self.assertTrue(lines[2].startswith("; "))
        self.assertNotEqual(lines[2], "")

    def test_keeps_promoted_inline_comment_attached_to_existing_comment_block(self) -> None:
        text = "; existing comment\n(set-goal gl-test 1) ; " + "comment " * 15 + "\n"
        formatted = format_text(text, ".per", FormatOptions(max_line_length=70))
        lines = formatted.splitlines()

        self.assertEqual(lines[0], "; existing comment")
        self.assertTrue(lines[1].startswith("; "))
        self.assertEqual(lines[-1], "(set-goal gl-test 1)")
        self.assertNotEqual(lines[1], "")

    def test_keeps_promoted_inline_defrule_comment_attached_to_defrule(self) -> None:
        text = "(true)\n(defrule ; " + "comment " * 15 + "\n    (true)\n=>\n    (do-nothing)\n)\n"
        formatted = format_text(text, ".per", FormatOptions(max_line_length=70))
        lines = formatted.splitlines()

        self.assertEqual(lines[0], "(true)")
        self.assertTrue(lines[1].startswith("; "))
        self.assertEqual(lines[3], "(defrule")
        self.assertNotEqual(lines[1], "")

    def test_keeps_short_inline_comment(self) -> None:
        text = "(set-goal gl-test 1) ; short\n"
        self.assertEqual(format_text(text, ".per", FormatOptions(max_line_length=70)), text)

    def test_splits_multiple_fact_and_action_expressions(self) -> None:
        text = "\n".join(
            [
                "(defrule",
                "(true) (food-amount > 100)",
                "=>",
                "(set-goal gl-test 1) (disable-self)",
                ")",
                "",
            ]
        )

        formatted = format_text(text, ".per")

        self.assertIn("    (true)\n    (food-amount > 100)", formatted)
        self.assertIn("    (set-goal gl-test 1)\n    (disable-self)", formatted)

    def test_indents_defrule_body(self) -> None:
        text = "\n".join(
            [
                "(defrule",
                "(up-compare-sn sn-focus-player-number < 9)",
                "(or",
                "(true)",
                "(players-stance focus-player ally))",
                "=>",
                "(up-full-reset-search)",
                "; action comment",
                "(up-find-remote c: town-center c: 40)",
                ")",
                "",
            ]
        )

        formatted = format_text(text, ".per")

        self.assertEqual(
            formatted,
            "\n".join(
                [
                    "(defrule",
                    "    (up-compare-sn sn-focus-player-number < 9)",
                    "    (or",
                    "    (true)",
                    "    (players-stance focus-player ally))",
                    "=>",
                    "    (up-full-reset-search)",
                    "    ; action comment",
                    "    (up-find-remote c: town-center c: 40)",
                    ")",
                    "",
                ]
            ),
        )

    def test_indents_defrule_body_when_defrule_has_inline_comment(self) -> None:
        text = "\n".join(
            [
                "(defrule; short rule comment",
                "(true)",
                "=>",
                "(do-nothing)",
                ")",
                "",
            ]
        )

        formatted = format_text(text, ".per")

        self.assertEqual(
            formatted,
            "\n".join(
                [
                    "(defrule; short rule comment",
                    "    (true)",
                    "=>",
                    "    (do-nothing)",
                    ")",
                    "",
                ]
            ),
        )

    def test_inserts_single_blank_line_before_later_defrule(self) -> None:
        text = "(defconst x 1)\n(defrule\n(true)\n=>\n(do-nothing)\n)\n"

        formatted = format_text(text, ".per")

        self.assertEqual(
            formatted,
            "(defconst x 1)\n\n(defrule\n    (true)\n=>\n    (do-nothing)\n)\n",
        )

    def test_does_not_duplicate_blank_line_before_defrule(self) -> None:
        text = "(defconst x 1)\n\n(defrule\n(true)\n=>\n(do-nothing)\n)\n"

        formatted = format_text(text, ".per")

        self.assertEqual(
            formatted,
            "(defconst x 1)\n\n(defrule\n    (true)\n=>\n    (do-nothing)\n)\n",
        )

    def test_keeps_comment_block_attached_to_defrule(self) -> None:
        text = "; rule comment\n(defrule\n(true)\n=>\n(do-nothing)\n)\n"

        formatted = format_text(text, ".per")

        self.assertEqual(
            formatted,
            "; rule comment\n(defrule\n    (true)\n=>\n    (do-nothing)\n)\n",
        )

    def test_indents_promoted_inline_comment_inside_defrule(self) -> None:
        text = "(defrule\n(true)\n=>\n(up-find-remote c: town-center c: 40) ; " + "comment " * 15 + "\n)\n"
        formatted = format_text(text, ".per", FormatOptions(max_line_length=70))
        lines = formatted.splitlines()

        self.assertEqual(lines[1], "    (true)")
        self.assertTrue(lines[3].startswith("    ; "))
        self.assertNotEqual(lines[3], "")
        self.assertEqual(lines[-2], "    (up-find-remote c: town-center c: 40)")

    def test_uses_dominant_load_path_separator(self) -> None:
        text = "\n".join(
            [
                '(load "folder\\one")',
                '(load "folder\\two")',
                '(load "folder/three")',
                "",
            ]
        )

        formatted = format_text(text, ".per")

        self.assertIn('(load "folder\\three")', formatted)

    def test_leaves_chat_lines_unchanged_by_default(self) -> None:
        text = '(chat-to-all "' + ("debug " * 80).strip() + '")\n'
        self.assertEqual(format_text(text, ".per", FormatOptions(max_line_length=70)), text)

    def test_cli_check_reports_unformatted_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "bot.per"
            path.write_text("; " + "alpha " * 20, encoding="utf-8")

            code = main(["format", str(path), "--check", "--max-line-length", "60"])

            self.assertEqual(code, 1)

    def test_cli_write_formats_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "bot.ai"
            path.write_text("(load \"bot\")\n", encoding="utf-8")

            code = main(["format", str(path), "--write"])

            self.assertEqual(code, 0)
            self.assertEqual(path.read_text(encoding="utf-8"), "")

    def test_cli_format_directory_can_stay_non_recursive(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            nested = root / "nested"
            nested.mkdir()
            direct = root / "direct.per"
            nested_file = nested / "nested.per"
            direct.write_text("(defrule\n(true)\n=>\n(do-nothing)\n)\n", encoding="utf-8")
            nested_file.write_text("(defrule\n(true)\n=>\n(do-nothing)\n)\n", encoding="utf-8")

            code = main(["format", str(root), "--write", "--no-recursive"])

            self.assertEqual(code, 0)
            self.assertIn("    (true)", direct.read_text(encoding="utf-8"))
            self.assertNotIn("    (true)", nested_file.read_text(encoding="utf-8"))

    def test_cli_format_ai_include_loads_formats_reachable_per_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            ai_path = root / "bot.ai"
            per_path = root / "bot.per"
            unused_path = root / "unused.per"
            ai_path.write_text('(load "bot")\n', encoding="utf-8")
            per_path.write_text("(defrule\n(true)\n=>\n(do-nothing)\n)\n", encoding="utf-8")
            unused_path.write_text("(defrule\n(true)\n=>\n(do-nothing)\n)\n", encoding="utf-8")

            code = main(["format", str(ai_path), "--write", "--include-loads"])

            self.assertEqual(code, 0)
            self.assertEqual(ai_path.read_text(encoding="utf-8"), "")
            self.assertIn("    (true)", per_path.read_text(encoding="utf-8"))
            self.assertNotIn("    (true)", unused_path.read_text(encoding="utf-8"))

    def test_cli_stdout_prints_single_formatted_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "bot.per"
            path.write_text("(true)\n(chat-to-all \"debug\")", encoding="utf-8")
            stdout = StringIO()

            with redirect_stdout(stdout):
                code = main(["format", str(path), "--stdout"])

            self.assertEqual(code, 0)
            self.assertEqual(stdout.getvalue(), "(true)\n(chat-to-all \"debug\")\n")
            self.assertEqual(path.read_text(encoding="utf-8"), "(true)\n(chat-to-all \"debug\")")

    def test_cli_stdin_formats_buffer_text(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "bot.per"
            stdout = StringIO()
            stdin = StringIO("(true)\n(chat-to-all \"debug\")")

            original_stdin = sys.stdin
            try:
                sys.stdin = stdin
                with redirect_stdout(stdout), redirect_stderr(StringIO()):
                    code = main(["format", str(path), "--stdin"])
            finally:
                sys.stdin = original_stdin

            self.assertEqual(code, 0)
            self.assertEqual(stdout.getvalue(), "(true)\n(chat-to-all \"debug\")\n")


if __name__ == "__main__":
    unittest.main()
