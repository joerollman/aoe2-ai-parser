from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from aoe2_ai_lab.parser import (
    Atom,
    Expression,
    active_source_lines,
    parse_expression,
    parse_script,
    preprocessor_issues,
)


class ParserTests(unittest.TestCase):
    def test_parses_rules_and_constants(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defconst goal-opening 1)
(defrule
    (true)
=>
    (set-goal goal-opening 2)
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )

            script = parse_script(path)

        self.assertEqual(script.constants["goal-opening"], 1)
        self.assertEqual(script.constant_tokens, {"goal-opening": "1"})
        self.assertEqual(len(script.rules), 1)
        self.assertEqual(script.rules[0].facts, ("(true)",))
        self.assertEqual(script.rules[0].fact_lines, (3,))
        self.assertEqual(script.rules[0].fact_exprs[0].head, "true")
        self.assertEqual(script.rules[0].actions[-1], "(disable-self)")
        self.assertEqual(script.rules[0].action_lines, (5, 6))
        self.assertEqual(script.rules[0].action_exprs[-1].head, "disable-self")

    def test_resolves_defconst_alias_chains(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defconst gl-base 1)
(defconst gl-alias gl-base)
(defconst gl-second gl-alias)
(defconst gl-cycle-a gl-cycle-b)
(defconst gl-cycle-b gl-cycle-a)
""".strip(),
                encoding="utf-8",
            )

            script = parse_script(path)

        self.assertEqual(script.constant_names, frozenset({
            "gl-base",
            "gl-alias",
            "gl-second",
            "gl-cycle-a",
            "gl-cycle-b",
        }))
        self.assertEqual(script.constant_tokens["gl-second"], "gl-alias")
        self.assertEqual(script.constants["gl-base"], 1)
        self.assertEqual(script.constants["gl-alias"], 1)
        self.assertEqual(script.constants["gl-second"], 1)
        self.assertNotIn("gl-cycle-a", script.constants)

    def test_tracks_multi_word_quoted_defconst_tokens(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defconst greeting "hello world")
(defconst escaped "hello \\"world\\"")
""".strip(),
                encoding="utf-8",
            )

            script = parse_script(path)

        self.assertEqual(script.constant_tokens["greeting"], '"hello world"')
        self.assertEqual(script.constant_tokens["escaped"], '"hello \\"world\\""')
        self.assertNotIn("greeting", script.constants)

    def test_parses_windows_1252_encoded_scripts(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_bytes(
                """
; caf\xe9
(defrule
    (true)
=>
    (chat-to-all "ol\xe9")
)
""".strip().encode("cp1252")
            )

            script = parse_script(path)

        self.assertEqual(len(script.rules), 1)
        self.assertEqual(script.rules[0].actions, ('(chat-to-all "ol\xe9")',))

    def test_parses_arrow_after_fact_on_same_line(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (true)
    (game-time > 5) =>
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )

            script = parse_script(path)

        self.assertEqual(script.rules[0].facts, ("(true)", "(game-time > 5)"))
        self.assertEqual(script.rules[0].fact_lines, (2, 3))
        self.assertEqual(script.rules[0].actions, ("(disable-self)",))
        self.assertEqual(script.rules[0].action_lines, (4,))

    def test_combines_multiline_nested_fact_expression(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (or (population < 2)
        (and (military-population < 4)
            (unit-type-count monk < 2)))
=>
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )

            script = parse_script(path)

        rule = script.rules[0]
        self.assertEqual(len(rule.facts), 1)
        self.assertEqual(rule.fact_lines, (2,))
        self.assertEqual(rule.fact_exprs[0].head, "or")
        self.assertEqual(rule.fact_exprs[0].args[1].head, "and")

    def test_parses_final_action_on_rule_closing_line(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (game-time >= 15)
=>
    (resign))
""".strip(),
                encoding="utf-8",
            )

            script = parse_script(path)

        self.assertEqual(script.rules[0].actions, ("(resign)",))
        self.assertEqual(script.rules[0].action_lines, (4,))

    def test_parses_same_line_action_and_rule_close_after_arrow(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (true)
=> (do-nothing))
""".strip(),
                encoding="utf-8",
            )

            script = parse_script(path)

        self.assertEqual(script.rules[0].actions, ("(do-nothing)",))
        self.assertEqual(script.rules[0].action_lines, (3,))

    def test_splits_multiple_complete_actions_on_one_line(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (true)
=> (set-goal 1 1) (disable-self))
""".strip(),
                encoding="utf-8",
            )

            script = parse_script(path)

        self.assertEqual(script.rules[0].actions, ("(set-goal 1 1)", "(disable-self)"))
        self.assertEqual(script.rules[0].action_lines, (3, 3))
        self.assertEqual([expr.head for expr in script.rules[0].action_exprs], ["set-goal", "disable-self"])

    def test_parses_single_line_defrule(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text("(defrule (true) => (set-goal 1 1) (disable-self))", encoding="utf-8")

            script = parse_script(path)

        self.assertEqual(script.rules[0].facts, ("(true)",))
        self.assertEqual(script.rules[0].actions, ("(set-goal 1 1)", "(disable-self)"))
        self.assertEqual(script.rules[0].fact_lines, (1,))
        self.assertEqual(script.rules[0].action_lines, (1, 1))

    def test_parses_inline_defrule_start(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule (true)
=>
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )

            script = parse_script(path)

        self.assertEqual(script.rules[0].facts, ("(true)",))
        self.assertEqual(script.rules[0].actions, ("(disable-self)",))

    def test_parses_tab_after_defrule_start(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text("(defrule\t(true) => (disable-self))", encoding="utf-8")

            script = parse_script(path)

        self.assertEqual(script.rules[0].facts, ("(true)",))
        self.assertEqual(script.rules[0].actions, ("(disable-self)",))

    def test_splits_multiple_complete_facts_on_one_line(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (true) (game-time > 5)
=>
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )

            script = parse_script(path)

        self.assertEqual(script.rules[0].facts, ("(true)", "(game-time > 5)"))
        self.assertEqual(script.rules[0].fact_lines, (2, 2))
        self.assertEqual([expr.head for expr in script.rules[0].fact_exprs], ["true", "game-time"])

    def test_nested_closing_parenthesis_does_not_end_rule(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (or (true)
        (false)
    )
=>
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )

            script = parse_script(path)

        self.assertEqual(len(script.rules), 1)
        self.assertEqual(script.rules[0].end_line, 7)
        self.assertEqual(script.rules[0].actions, ("(disable-self)",))

    def test_parentheses_inside_strings_do_not_affect_rule_balance(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (true)
=>
    (chat-to-all "message with ( paren")
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )

            script = parse_script(path)

        self.assertEqual(len(script.rules), 1)
        self.assertEqual(script.rules[0].end_line, 6)
        self.assertEqual(script.rules[0].actions[-1], "(disable-self)")

    def test_arrow_inside_strings_does_not_split_rule_sides(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (true)
=>
    (up-chat-data-to-player my-player-number "=> Boar1: %d" g: gl-lured-boar-id)
)
""".strip(),
                encoding="utf-8",
            )

            script = parse_script(path)

        self.assertEqual(script.rules[0].facts, ("(true)",))
        self.assertEqual(
            script.rules[0].actions,
            ('(up-chat-data-to-player my-player-number "=> Boar1: %d" g: gl-lured-boar-id)',),
        )

    def test_escaped_quotes_keep_semicolons_and_parentheses_inside_strings(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (true)
=>
    (chat-to-all "quoted \\"text ; not comment ( not paren\\"")
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )

            script = parse_script(path)

        self.assertEqual(len(script.rules), 1)
        self.assertEqual(script.rules[0].end_line, 6)
        self.assertEqual(
            script.rules[0].actions[0],
            '(chat-to-all "quoted \\"text ; not comment ( not paren\\"")',
        )
        self.assertEqual(script.rules[0].actions[1], "(disable-self)")

    def test_parses_expression_ast(self) -> None:
        expr = parse_expression(
            '(or (taunt-detected any-ally 199) (taunt-detected my-player-number 199))',
            12,
        )

        self.assertIsNotNone(expr)
        assert expr is not None
        self.assertEqual(expr.head, "or")
        self.assertEqual(expr.line, 12)
        self.assertEqual(len(expr.args), 2)
        self.assertIsInstance(expr.args[0], Expression)
        first_child = expr.args[0]
        assert isinstance(first_child, Expression)
        self.assertEqual(first_child.head, "taunt-detected")
        self.assertEqual(first_child.args[0], Atom("any-ally", 12))
        self.assertEqual(expr.start_col, 0)
        self.assertEqual(expr.head_start_col, 1)
        self.assertEqual(expr.head_end_col, 3)
        self.assertEqual(first_child.start_col, 4)
        self.assertEqual(first_child.head_start_col, 5)
        assert isinstance(first_child.args[0], Atom)
        self.assertEqual(first_child.args[0].start_col, 20)
        self.assertEqual(first_child.args[0].end_col, 28)

    def test_parses_rule_expression_columns(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (true) (game-time > 5)
=>
    (set-goal goal-opening 2) (disable-self)
)
""".strip(),
                encoding="utf-8",
            )

            script = parse_script(path)

        self.assertEqual([expr.head for expr in script.rules[0].fact_exprs], ["true", "game-time"])
        self.assertEqual([expr.start_col for expr in script.rules[0].fact_exprs], [4, 11])
        self.assertEqual([expr.head for expr in script.rules[0].action_exprs], ["set-goal", "disable-self"])
        self.assertEqual([expr.start_col for expr in script.rules[0].action_exprs], [4, 30])

    def test_preprocessor_excludes_known_inactive_branch(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defconst ENABLED 1)
#load-if-not-defined ENABLED
(defrule
    (true)
=>
    (bad-action))
#else
(defrule
    (true)
=>
    (do-nothing))
#end-if
""".strip(),
                encoding="utf-8",
            )

            script = parse_script(path)

        self.assertEqual(len(script.rules), 1)
        self.assertEqual(script.rules[0].start_line, 8)
        self.assertEqual(script.rules[0].actions, ("(do-nothing)",))

    def test_preprocessor_keeps_unknown_condition_active(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
#load-if-defined UNKNOWN
(defrule
    (true)
=>
    (do-nothing))
#end-if
""".strip(),
                encoding="utf-8",
            )

            script = parse_script(path)

        self.assertEqual(len(script.rules), 1)
        self.assertEqual(script.rules[0].start_line, 2)
        self.assertEqual(script.rules[0].confidence, "conditional")

    def test_active_source_lines_preserves_original_line_numbers(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defconst ENABLED 1)
#load-if-defined ENABLED
(defconst ACTIVE 2)
#end-if
""".strip(),
                encoding="utf-8",
            )

            active = active_source_lines(path)

        self.assertEqual(
            [(line.number, line.text.strip()) for line in active],
            [(1, "(defconst ENABLED 1)"), (3, "(defconst ACTIVE 2)")],
        )

    def test_preprocessor_keeps_unknown_inline_conditional_payload(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                '#load-if-defined UNKNOWN (defconst MAYBE 1) #end-if\n',
                encoding="utf-8",
            )

            active = active_source_lines(path)
            script = parse_script(path)

        self.assertEqual([(line.number, line.text.strip()) for line in active], [(1, "(defconst MAYBE 1)")])
        self.assertEqual(active[0].confidence, "conditional")
        self.assertEqual(script.constants, {"MAYBE": 1})

    def test_inline_preprocessor_ignores_end_if_text_inside_payload_string(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                '#load-if-defined UNKNOWN (defconst MAYBE "#end-if text") #end-if\n',
                encoding="utf-8",
            )

            active = active_source_lines(path)
            script = parse_script(path)

        self.assertEqual(
            [(line.number, line.text.strip(), line.confidence) for line in active],
            [(1, '(defconst MAYBE "#end-if text")', "conditional")],
        )
        self.assertEqual(script.constant_tokens, {"MAYBE": '"#end-if text"'})

    def test_preprocessor_reports_unmatched_and_unterminated_directives(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
#else
#load-if-defined
#load-if-defined UNKNOWN
""".strip(),
                encoding="utf-8",
            )

            issues = preprocessor_issues(path)

        self.assertEqual(
            [issue.code for issue in issues],
            [
                "unexpected-preprocessor-else",
                "malformed-preprocessor-directive",
                "unterminated-preprocessor-conditional",
            ],
        )
        self.assertEqual(issues[-1].confidence, "conditional")

    def test_preprocessor_reports_duplicate_else(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
#load-if-defined UNKNOWN
(defconst ACTIVE 1)
#else
(defconst FALLBACK 1)
#else
(defconst OTHER 1)
#end-if
""".strip(),
                encoding="utf-8",
            )

            issues = preprocessor_issues(path)

        self.assertEqual([issue.code for issue in issues], ["duplicate-preprocessor-else"])
        self.assertEqual(issues[0].confidence, "conditional")

    def test_preprocessor_flags_nesting_depth_above_50(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                "\n".join(["#load-if-defined UNKNOWN"] * 51 + ["#end-if"] * 51),
                encoding="utf-8",
            )

            issues = preprocessor_issues(path)

        self.assertEqual([issue.code for issue in issues], ["preprocessor-nesting-depth-exceeded"])
        self.assertEqual(issues[0].line, 51)
        self.assertIn("50", issues[0].message)

    def test_preprocessor_ignores_directive_text_inside_strings(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (true)
=>
    (chat-to-all "#load-if-defined UNKNOWN #else #end-if")
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )

            script = parse_script(path)
            issues = preprocessor_issues(path)

        self.assertEqual(issues, ())
        self.assertEqual(len(script.rules), 1)
        self.assertEqual(script.rules[0].actions[-1], "(disable-self)")


if __name__ == "__main__":
    unittest.main()
