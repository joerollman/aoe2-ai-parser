import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from aoe2_ai_lab.linter import SCHEMA_VALIDATED_COMMANDS, lint_file


class LinterTests(unittest.TestCase):
    def test_schema_validates_all_actionable_documented_commands(self) -> None:
        structural_commands = {
            "defconst",
            "defrule",
            "#else",
            "#end-if",
            "include",
            "load",
            "#load-if-defined",
            "#load-if-not-defined",
            "load-random",
            "and",
            "nand",
            "nor",
            "not",
            "or",
            "xnor",
            "xor",
        }
        inventory_path = (
            Path(__file__).resolve().parents[1]
            / "docs"
            / "extracted"
            / "inventories"
            / "airef-command-inventory.json"
        )
        commands = json.loads(inventory_path.read_text(encoding="utf-8-sig"))["commands"]

        missing = sorted(
            command["name"]
            for command in commands
            if command["name"] not in structural_commands
            and command["name"] not in SCHEMA_VALIDATED_COMMANDS
        )

        self.assertEqual(missing, [])

    def test_flags_chat_rules_that_can_repeat(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (true)
=>
    (chat-to-player my-player-number "hello")
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "repeat-chat")
        self.assertEqual(findings[0].severity, "warning")
        self.assertIn(": warning: repeat-chat:", findings[0].format(path))

    def test_corpus_profile_suppresses_repeat_chat_style_noise(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (true)
=>
    (chat-to-player my-player-number "hello")
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path, profile="corpus")

        self.assertEqual(findings, [])

    def test_flags_missing_c_typed_constant(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (up-gaia-type-count c: forage-bush > 3)
=>
    (do-nothing)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "undefined-constant")

    def test_allows_documented_object_and_sn_identifiers_without_defconst(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (true)
=>
    (set-strategic-number sn-placement-zone-size 20)
    (up-find-local c: town-center c: 1)
    (up-find-local c: town-center-foundation c: 1)
    (up-find-local c: bombard-cannon-line c: 1)
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings, [])

    def test_allows_documented_dynamic_unique_unit_ids_without_defconst(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (can-train my-unique-unit-line)
=>
    (train my-unique-unit-line)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings, [])

    def test_flags_unknown_direct_unit_identifier(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (true)
=>
    (train not-a-real-unit)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "command-argument-mismatch")
        self.assertIn("UnitId", findings[0].message)

    def test_allows_defined_direct_unit_identifier(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defconst custom-unit 12345)
(defrule
    (true)
=>
    (train custom-unit)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings, [])

    def test_allows_dynamic_and_compatibility_tech_ids_without_defconst(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (true)
    =>
    (up-research 0 c: my-unique-unit-upgrade)
    (up-research 0 c: my-unique-research)
    (up-research 0 c: my-second-unique-research)
    (up-research 0 c: ri-cartography)
    (up-research 0 c: ri-fast-fire-ship)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings, [])

    def test_allows_defined_c_typed_constant(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defconst forage-bush 59)
(defrule
    (up-gaia-type-count c: forage-bush > 3)
=>
    (do-nothing)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings, [])

    def test_flags_missing_strategic_number_constant(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (true)
=>
    (set-strategic-number sn-not-a-real-strategic-number 5)
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "undefined-strategic-number")
        self.assertNotIn("undefined-identifier", {finding.code for finding in findings})

    def test_explains_archived_non_de_strategic_number(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (true)
=>
    (set-strategic-number sn-number-defend-groups 1)
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "undefined-strategic-number")
        self.assertIn("archived as non-DE", findings[0].message)
        self.assertIn("strategic-number registry", findings[0].message)

    def test_allows_defined_strategic_number_constant(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defconst sn-target-point-adjustment 292)
(defrule
    (true)
=>
    (set-strategic-number sn-target-point-adjustment 5)
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings, [])

    def test_allows_binary_observed_target_evaluation_strategic_numbers(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (strategic-number sn-target-evaluation-range == 0)
=>
    (set-strategic-number sn-target-evaluation-ally-proximity 50)
    (up-modify-sn sn-target-evaluation-damage-capability c:= 200)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings, [])

    def test_flags_rule_with_more_than_thirty_two_elements(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (true)
=>
    (do-nothing)
    (do-nothing)
    (do-nothing)
    (do-nothing)
    (do-nothing)
    (do-nothing)
    (do-nothing)
    (do-nothing)
    (do-nothing)
    (do-nothing)
    (do-nothing)
    (do-nothing)
    (do-nothing)
    (do-nothing)
    (do-nothing)
    (do-nothing)
    (do-nothing)
    (do-nothing)
    (do-nothing)
    (do-nothing)
    (do-nothing)
    (do-nothing)
    (do-nothing)
    (do-nothing)
    (do-nothing)
    (do-nothing)
    (do-nothing)
    (do-nothing)
    (do-nothing)
    (do-nothing)
    (do-nothing)
    (do-nothing)
    (do-nothing)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "rule-too-long")

    def test_rule_length_counts_nested_logical_expressions(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            nested_facts = "\n".join("        (true)" for _ in range(32))
            path.write_text(
                f"""
(defrule
    (or
{nested_facts}
    )
=>
    (do-nothing)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "rule-too-long")

    def test_flags_low_goal_for_point_writer(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defconst point-x 5)
(defrule
    (true)
=>
    (up-get-point position-self point-x)
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "unsafe-goal-block")

    def test_flags_missing_up_get_point_position_constant(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defconst point-x 41)
(defrule
    (true)
=>
    (up-get-point position-curr-object point-x)
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "undefined-position-constant")

    def test_allows_defined_up_get_point_position_constant(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defconst position-curr-object 12)
(defconst point-x 41)
(defrule
    (true)
=>
    (up-get-point position-curr-object point-x)
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings, [])

    def test_does_not_lint_identifiers_inside_quoted_text(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (true)
=>
    (chat-to-all "sn-fake class-fake action-fake object-data-fake")
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings, [])

    def test_does_not_lint_identifiers_after_escaped_quote_inside_quoted_text(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (true)
=>
    (chat-to-all "escaped \\" sn-fake class-fake action-fake object-data-fake")
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings, [])

    def test_flags_missing_common_identifier_family_constant(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (true)
=>
    (up-get-object-data object-data-unknown g: goal-data)
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "command-arity-mismatch")

    def test_flags_alias_for_documented_builtin_constant(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defconst class-villager 904)
(defrule
    (true)
=>
    (do-nothing)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "builtin-constant-alias")

    def test_flags_redundant_builtin_defconst(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defconst villager-class 904)
(defrule
    (true)
=>
    (do-nothing)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "redundant-built-in-defconst")

    def test_flags_redundant_builtin_defconst_with_symbolic_value(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defconst villager-class class-villager)
(defrule
    (true)
=>
    (do-nothing)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "redundant-built-in-defconst")

    def test_flags_symbolic_alias_for_documented_builtin_constant(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defconst class-villager villager-class)
(defrule
    (true)
=>
    (do-nothing)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "builtin-constant-alias")
        self.assertIn("'villager-class'", findings[0].message)

    def test_corpus_profile_suppresses_builtin_alias_noise(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defconst class-villager 904)
(defconst villager-class 904)
(defrule
    (true)
=>
    (do-nothing)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path, profile="corpus")

        self.assertEqual(findings, [])

    def test_flags_duplicate_defconst_conflicting_values(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defconst goal-state 1)
(defconst goal-state 2)
(defrule
    (true)
=>
    (do-nothing)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "duplicate-defconst-conflict")
        self.assertEqual(findings[0].severity, "warning")
        self.assertIn("line 1", findings[0].message)

    def test_flags_duplicate_defconst_conflicting_alias_values(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defconst goal-state opening-goal)
(defconst goal-state closing-goal)
(defrule
    (true)
=>
    (do-nothing)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "duplicate-defconst-conflict")
        self.assertIn("'opening-goal'", findings[0].message)
        self.assertIn("'closing-goal'", findings[0].message)

    def test_allows_duplicate_defconst_same_value(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defconst goal-state 1)
(defconst goal-state 1)
(defrule
    (true)
=>
    (do-nothing)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings, [])

    def test_allows_duplicate_defconst_same_alias_value(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defconst goal-state opening-goal)
(defconst goal-state opening-goal)
(defrule
    (true)
=>
    (do-nothing)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings, [])

    def test_flags_duplicate_defconst_conflicting_quoted_values(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defconst greeting "hello")
(defconst greeting "bye")
(defrule
    (true)
=>
    (do-nothing)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "duplicate-defconst-conflict")
        self.assertIn("'\"hello\"'", findings[0].message)
        self.assertIn("'\"bye\"'", findings[0].message)

    def test_flags_duplicate_defconst_conflicting_multi_word_quoted_values(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defconst greeting "hello world")
(defconst greeting "bye world")
(defrule
    (true)
=>
    (do-nothing)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "duplicate-defconst-conflict")
        self.assertIn("'\"hello world\"'", findings[0].message)
        self.assertIn("'\"bye world\"'", findings[0].message)

    def test_allows_duplicate_defconst_same_quoted_value(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defconst greeting "hello")
(defconst greeting "hello")
(defrule
    (true)
=>
    (do-nothing)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings, [])

    def test_flags_defconst_alias_cycle(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defconst goal-a goal-b)
(defconst goal-b goal-a)
(defrule
    (true)
=>
    (do-nothing)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual([finding.code for finding in findings], ["defconst-alias-cycle"])
        self.assertIn("goal-a -> goal-b -> goal-a", findings[0].message)

    def test_allows_defconst_alias_chain_to_numeric_value(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defconst goal-a goal-b)
(defconst goal-b 1)
(defrule
    (true)
=>
    (do-nothing)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings, [])

    def test_allows_conditional_duplicate_defconst_conflict(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
#load-if-defined UNKNOWN
(defconst goal-state 1)
#else
(defconst goal-state 2)
#end-if
(defrule
    (true)
=>
    (do-nothing)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings, [])

    def test_flags_defconst_missing_value(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defconst goal-state)
(defrule
    (true)
=>
    (do-nothing)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "malformed-defconst")
        self.assertEqual(findings[0].severity, "error")
        self.assertIn("exactly", findings[0].message)

    def test_flags_defconst_missing_identifier_spacing(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defconst)
(defrule
    (true)
=>
    (do-nothing)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "malformed-defconst")

    def test_allows_broad_defconst_name_syntax(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defconst 123-goal 1)
(defconst _fcn_TrebMicro::micro_dodgeStateMicro 2)
(defrule
    (true)
=>
    (do-nothing)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings, [])

    def test_allows_defconst_alias_value(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defconst goal-state other-goal)
(defrule
    (true)
=>
    (do-nothing)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings, [])

    def test_flags_defconst_unquoted_multi_token_value(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defconst goal-state other goal)
(defrule
    (true)
=>
    (do-nothing)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "malformed-defconst")
        self.assertIn("single token", findings[0].message)

    def test_flags_defconst_unclosed_quoted_value(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defconst greeting "hello)
(defrule
    (true)
=>
    (do-nothing)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "malformed-defconst")
        self.assertIn("closing quote", findings[0].message)

    def test_flags_defconst_ending_with_escaped_quote_as_unclosed(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                "\n".join(
                    [
                        r'(defconst greeting "hello \")',
                        "(defrule",
                        "    (true)",
                        "=>",
                        "    (do-nothing)",
                        ")",
                    ]
                ),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "malformed-defconst")
        self.assertIn("closing quote", findings[0].message)

    def test_allows_defconst_with_escaped_quotes_inside_quoted_value(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defconst greeting "hello \\"world\\"")
(defrule
    (true)
=>
    (do-nothing)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings, [])

    def test_allows_multiple_defconst_forms_on_one_line(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defconst class-villager villager-class)(defconst goal-state 1)
(defrule
    (true)
=>
    (set-goal goal-state 2)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(
            [finding.code for finding in findings],
            ["builtin-constant-alias"],
        )

    def test_flags_defconst_numeric_value_outside_signed_16_bit_range(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defconst chat-buffer 7031232)
(defconst too-low -32769)
(defrule
    (true)
=>
    (do-nothing)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(
            [finding.code for finding in findings],
            ["defconst-value-out-of-range", "defconst-value-out-of-range"],
        )
        self.assertEqual([finding.line for finding in findings], [1, 2])
        self.assertEqual(findings[0].severity, "error")
        self.assertIn("signed 16-bit", findings[0].message)

    def test_allows_defconst_numeric_value_at_signed_16_bit_boundaries(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defconst minimum -32768)
(defconst maximum 32767)
(defconst alias maximum)
(defconst greeting "hello")
(defrule
    (true)
=>
    (do-nothing)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings, [])

    def test_suppress_codes_filters_specific_findings(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defconst villager-class 904)
(defrule
    (true)
=>
    (do-nothing)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path, suppress_codes={"redundant-built-in-defconst"})

        self.assertEqual(findings, [])

    def test_flags_low_goal_for_search_state_writer(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defconst search-state 9)
(defrule
    (true)
=>
    (up-get-search-state search-state)
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "unsafe-goal-block")

    def test_flags_livestock_point_default(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (true)
=>
    (up-find-local c: livestock-class c: 1)
    (up-target-point 41 action-default -1 -1)
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "livestock-default-point")

    def test_flags_up_can_build_literal_zero_escrow(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defconst house 70)
(defrule
    (up-can-build 0 c: house)
=>
    (do-nothing)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "up-can-build-zero-escrow")

    def test_corpus_profile_suppresses_documented_up_can_build_zero_idiom(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defconst house 70)
(defrule
    (up-can-build 0 c: house)
=>
    (do-nothing)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path, profile="corpus")

        self.assertEqual(findings, [])

    def test_flags_split_typed_comparison_operator(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (up-point-distance point-a point-b <= g: distance-goal)
=>
    (do-nothing)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "split-typed-comparison")

    def test_flags_source_line_longer_than_255_characters(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                "\n".join(
                    [
                        "(defrule",
                        "    (true)",
                        "=>",
                        "    " + "; " + ("x" * 254),
                        "    (disable-self)",
                        ")",
                    ]
                ),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "source-line-too-long")
        self.assertIn("255", findings[0].message)

    def test_flags_missing_closing_parenthesis(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (true)
=>
    (do-nothing)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "unbalanced-parentheses")

    def test_inactive_preprocessor_branch_does_not_emit_lint_findings(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defconst ENABLED 1)
#load-if-not-defined ENABLED
(defrule
    (true)
=>
    (up-set-target-by-id g:= target-id)
)
#else
(defrule
    (true)
=>
    (do-nothing)
)
#end-if
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings, [])

    def test_unknown_preprocessor_branch_marks_findings_conditional(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
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

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "command-typed-prefix-mismatch")
        self.assertEqual(findings[0].confidence, "conditional")

    def test_flags_malformed_preprocessor_directive(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text("#load-if-defined\n", encoding="utf-8")

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "malformed-preprocessor-directive")
        self.assertEqual(findings[0].severity, "error")

    def test_flags_unexpected_preprocessor_end_if(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text("#end-if\n", encoding="utf-8")

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "unexpected-preprocessor-end-if")

    def test_flags_unterminated_defrule(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (true)
=>
    (do-nothing)

(defrule
    (true)
=>
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "unterminated-defrule")

    def test_linter_recovers_after_unterminated_defrule(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (true)
=>
    (do-nothing)

(defrule
    (up-get-point position-self gl-point extra-token)
=>
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertIn("unterminated-defrule", [finding.code for finding in findings])
        self.assertIn("unbalanced-parentheses", [finding.code for finding in findings])
        self.assertIn("command-arity-mismatch", [finding.code for finding in findings])

    def test_reports_multiple_defrule_structure_errors(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (true)
=>
    (do-nothing)

(defrule
    (true)
)
(defrule
    (true)
=>
    (do-nothing)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(
            [finding.code for finding in findings[:2]],
            ["unterminated-defrule", "defrule-missing-arrow"],
        )

    def test_defrule_structure_ignores_arrow_inside_string(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (chat-local-to-self "literal => text")
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "defrule-missing-arrow")

    def test_flags_raw_load_directive_by_default(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text('#load "tasks/foo"\n', encoding="utf-8")

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "raw-load-in-per")

    def test_flags_raw_load_directive_with_quoted_semicolon_target(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text('#load "tasks/foo;bar"\n', encoding="utf-8")

            findings = lint_file(path)

        self.assertEqual([finding.code for finding in findings], ["raw-load-in-per"])

    def test_can_allow_raw_load_directive_for_source_roots(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text('#load "tasks/foo"\n', encoding="utf-8")

            findings = lint_file(path, allow_raw_loads=True)

        self.assertEqual(findings, [])

    def test_flags_malformed_raw_load_directive(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text("#load tasks/foo\n", encoding="utf-8")

            findings = lint_file(path, allow_raw_loads=True)

        self.assertEqual(findings[0].code, "malformed-load-directive")

    def test_nonfatal_malformed_load_does_not_hide_later_lints(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(load tasks/foo)
(defrule
    (true)
=>
    (chat-to-all "hello")
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path, allow_raw_loads=True)

        self.assertEqual(
            [finding.code for finding in findings],
            ["malformed-load-directive", "repeat-chat"],
        )

    def test_corpus_profile_keeps_low_noise_exit_for_only_suppressed_preparse_findings(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defconst villager-class 904)
(defrule
    (true)
=>
    (up-set-target-object search-local c: 0)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path, profile="corpus")

        self.assertEqual(findings, [])

    def test_flags_malformed_runtime_load_directive(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
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

            findings = lint_file(path, allow_raw_loads=True)

        self.assertEqual(findings[0].code, "malformed-load-directive")

    def test_flags_malformed_include_directive(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
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

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "malformed-include-directive")

    def test_flags_include_target_without_xs_extension(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(include "debug")
(defrule
    (true)
=>
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "include-missing-xs-extension")
        self.assertIn(".xs", findings[0].message)

    def test_allows_valid_load_and_include_directives(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(load "tasks/foo")
(include "debug.xs")
#load "tasks/source"
(load-random
    50 "strategy-a"
    50 "strategy-b"
)
(defrule
    (true)
=>
    (do-nothing)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path, allow_raw_loads=True)

        self.assertEqual(findings, [])

    def test_flags_malformed_load_random_entry(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
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

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "malformed-load-random-directive")
        self.assertEqual(findings[0].severity, "error")

    def test_nonfatal_malformed_defconst_does_not_hide_later_lints(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defconst missing-value)
(defrule
    (true)
=>
    (chat-to-all "hello")
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(
            [finding.code for finding in findings],
            ["malformed-defconst", "repeat-chat"],
        )

    def test_nonfatal_malformed_load_random_does_not_hide_later_lints(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(load-random 50 strategy-a)
(defrule
    (true)
=>
    (chat-to-all "hello")
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(
            [finding.code for finding in findings],
            ["malformed-load-random-directive", "repeat-chat"],
        )

    def test_flags_malformed_single_line_load_random_entry(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(load-random 50 strategy-a)
(defrule
    (true)
=>
    (do-nothing)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "malformed-load-random-directive")

    def test_warns_for_load_random_plus_weight_forms_in_default_profile(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(load-random
    50 "strategy-a"
    +drush-chance "strategy-b"
    + "strategy-c"
)
(load-random +load-chance "strategy-d")
(load-random 10 "strategy-e" 90 "strategy-f")
(defrule
    (true)
=>
    (do-nothing)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(
            [finding.code for finding in findings],
            [
                "load-random-plus-weight-de-behavior",
                "load-random-plus-weight-de-behavior",
                "load-random-plus-weight-de-behavior",
            ],
        )
        self.assertTrue(all(finding.severity == "warning" for finding in findings))

    def test_corpus_profile_suppresses_load_random_plus_weight_behavior_noise(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(load-random
    50 "strategy-a"
    +drush-chance "strategy-b"
    + "strategy-c"
)
(defrule
    (true)
=>
    (do-nothing)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path, profile="corpus")

        self.assertEqual(findings, [])

    def test_load_random_plus_weight_warning_does_not_hide_later_lints(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(load-random +load-chance "strategy-a")
(defrule
    (true)
=>
    (chat-to-all "hello")
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(
            [finding.code for finding in findings],
            ["load-random-plus-weight-de-behavior", "repeat-chat"],
        )

    def test_flags_unsupported_ai_xs_function(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.xs"
            path.write_text(
                """
void debug() {
    int target = xsGetUnitTargetId(123);
}
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "unsupported-ai-xs-function")

    def test_flags_unscoped_duc_target_after_search_reset(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (true)
=>
    (up-reset-search 1 1 1 1)
    (up-target-point point-x action-move -1 -1)
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "unscoped-duc-target")

    def test_allows_scoped_duc_target_after_find_local(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defconst villager 83)
(defrule
    (true)
=>
    (up-reset-search 1 1 1 1)
    (up-find-local c: villager c: 1)
    (up-target-point point-x action-move -1 -1)
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings, [])

    def test_allows_retained_duc_scope_from_previous_rule(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (true)
=>
    (up-reset-search 1 1 1 1)
    (up-find-local c: villager-class c: 10)
)

(defrule
    (true)
=>
    (up-target-point point-x action-move -1 -1)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings, [])

    def test_allows_retained_duc_scope_after_remote_only_search_reset(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (true)
=>
    (up-find-local c: villager-class c: 10)
    (up-reset-search 0 0 1 1)
    (up-target-point point-x action-move -1 -1)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings, [])

    def test_flags_up_build_place_point_coordinate_as_escrow(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (true)
=>
    (up-set-target-point point-x)
    (up-build place-point point-x c: house)
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "up-build-place-point-coordinate-as-escrow")

    def test_allows_up_build_place_point_with_escrow_goal(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (true)
=>
    (up-set-target-point point-x)
    (up-build place-point goal-build-escrow-state c: house)
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings, [])

    def test_flags_action_used_as_fact(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (disable-self)
=>
    (do-nothing)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "command-role-mismatch")

    def test_flags_action_used_as_nested_fact(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (or
        (true)
        (disable-self)
    )
=>
    (do-nothing)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "command-role-mismatch")

    def test_flags_fact_used_as_action(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (true)
=>
    (game-time > 10)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "command-role-mismatch")

    def test_fact_used_as_action_suggests_likely_action(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (can-research-with-escrow ri-two-man-saw)
=>
    (can-research-with-escrow ri-two-man-saw)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "command-role-mismatch")
        self.assertIn("likely intended action", findings[0].message)
        self.assertIn("up-research", findings[0].message)

    def test_allows_fact_action_command_in_fact_context(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (up-set-target-object search-local c: 0)
=>
    (do-nothing)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings, [])

    def test_allows_action_set_target_object_after_fact_guard(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (up-set-target-object search-remote c: 0)
=>
    (up-set-target-object search-remote c: 0)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings, [])

    def test_flags_action_set_target_object_without_local_search(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (true)
=>
    (up-set-target-object search-local c: 0)
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "unsafe-set-target-object")

    def test_allows_action_set_target_object_after_local_search(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (true)
=>
    (up-find-local c: villager-class c: 1)
    (up-set-target-object search-local c: 0)
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings, [])

    def test_allows_action_set_target_object_after_retained_local_search(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (true)
=>
    (up-find-local c: villager-class c: 1)
)

(defrule
    (true)
=>
    (up-set-target-object search-local c: 0)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings, [])

    def test_allows_action_set_target_object_after_set_group(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (true)
=>
    (up-set-group search-local g: attack-group)
    (up-set-target-object search-local c: 0)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings, [])

    def test_allows_action_set_target_object_after_remote_only_search_reset(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (true)
=>
    (up-find-local c: villager-class c: 1)
    (up-reset-search 0 0 1 1)
    (up-set-target-object search-local c: 0)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings, [])

    def test_flags_action_set_target_object_after_local_list_search_reset(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (true)
=>
    (up-find-local c: villager-class c: 1)
    (up-reset-search 1 1 0 0)
    (up-set-target-object search-local c: 0)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "unsafe-set-target-object")

    def test_flags_target_object_arity_mismatch(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (true)
=>
    (up-find-local c: villager-class c: 1)
    (up-set-target-object search-local c: 0 extra-arg)
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "command-arity-mismatch")

    def test_flags_find_local_missing_type_prefix(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (true)
=>
    (up-find-local villager-class town-center c: 1)
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "command-typed-prefix-mismatch")
        self.assertIn("plain typeOp", findings[0].message)

    def test_allows_legacy_redirect_type_operator(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (true)
=>
    (up-find-local c:< villager-class c:< 1)
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings, [])

    def test_flags_math_operator_in_type_operator_slot(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
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

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "command-typed-prefix-mismatch")

    def test_flags_goal_prefix_with_strategic_number_operand(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
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

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "command-typed-operand-mismatch")
        self.assertEqual(findings[0].severity, "warning")
        self.assertIn("use s:", findings[0].message)

    def test_flags_strategic_number_prefix_with_goal_operand(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (true)
=>
    (up-set-target-by-id s: goal-town-size)
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "command-typed-operand-mismatch")
        self.assertIn("use g:", findings[0].message)

    def test_flags_math_operator_with_wrong_operand_family(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (true)
=>
    (up-modify-goal gl-target g:= sn-maximum-town-size)
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "command-typed-operand-mismatch")
        self.assertIn("use s:", findings[0].message)

    def test_flags_compare_operator_with_wrong_operand_family(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (up-compare-goal gl-target s:< goal-limit)
=>
    (do-nothing)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "command-typed-operand-mismatch")
        self.assertIn("use g:", findings[0].message)

    def test_allows_matching_typed_operand_prefixes(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (true)
=>
    (up-set-target-by-id g: goal-source)
    (up-find-local c: villager-class s: sn-cap-civilian-builders)
    (up-modify-goal gl-target g:= goal-source)
    (disable-self)
)
(defrule
    (up-compare-goal gl-target s:< sn-maximum-town-size)
=>
    (do-nothing)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings, [])

    def test_flags_strategic_number_symbol_in_goal_id_slot(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
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

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "command-family-mismatch")
        self.assertEqual(findings[0].severity, "warning")
        self.assertIn("GoalId", findings[0].message)

    def test_flags_goal_symbol_in_sn_id_slot(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (true)
=>
    (set-strategic-number goal-town-size 1)
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "command-family-mismatch")
        self.assertIn("SnId", findings[0].message)

    def test_allows_strategic_number_symbol_for_up_compare_sn(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (up-compare-sn sn-focus-player-number > 0)
=>
    (do-nothing)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings, [])

    def test_flags_goal_symbol_for_up_compare_sn(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (up-compare-sn gl-target > 0)
=>
    (do-nothing)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "command-family-mismatch")
        self.assertIn("SnId", findings[0].message)

    def test_flags_goal_symbol_in_object_id_slot(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (true)
=>
    (up-set-placement-data my-player-number gl-target-unit c: 1)
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "command-family-mismatch")
        self.assertIn("ObjectId", findings[0].message)

    def test_flags_any_player_wildcard_for_up_set_placement_data(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (true)
=>
    (up-set-placement-data any-ally town-center c: 1)
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "command-argument-mismatch")
        self.assertIn("cannot use any/every wildcard players", findings[0].message)

    def test_allows_this_any_rule_variable_for_up_set_placement_data(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (true)
=>
    (up-set-placement-data this-any-enemy town-center c: 1)
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings, [])

    def test_flags_any_player_wildcard_for_single_player_actions(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defconst out-goal 41)
(defrule
    (true)
=>
    (up-get-player-color any-ally out-goal)
    (up-get-player-fact any-ally player-number 0 out-goal)
    (up-get-upgrade-id every-enemy 0 out-goal out-goal)
    (up-store-player-chat any-enemy)
    (up-store-player-name every-ally)
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(
            [finding.code for finding in findings],
            [
                "command-argument-mismatch",
                "command-argument-mismatch",
                "command-argument-mismatch",
                "command-argument-mismatch",
                "command-argument-mismatch",
            ],
        )
        self.assertTrue(all("cannot use any/every wildcard players" in finding.message for finding in findings))

    def test_allows_this_any_rule_variable_for_single_player_actions(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defconst out-goal 41)
(defrule
    (true)
=>
    (up-get-player-color this-any-ally out-goal)
    (up-get-player-fact this-any-ally player-number 0 out-goal)
    (up-get-upgrade-id this-any-enemy 0 out-goal out-goal)
    (up-store-player-chat this-any-enemy)
    (up-store-player-name this-any-ally)
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings, [])

    def test_allows_any_player_wildcard_for_up_get_player_fact_fact_context(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defconst out-goal 41)
(defrule
    (up-get-player-fact any-ally player-number 0 out-goal)
=>
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings, [])

    def test_flags_unsupported_player_wildcards_for_up_find_player_flare(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defconst flare-point 41)
(defrule
    (true)
=>
    (up-find-player-flare this-any-ally flare-point)
    (up-find-player-flare every-enemy flare-point)
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(
            [finding.code for finding in findings],
            ["command-argument-mismatch", "command-argument-mismatch"],
        )
        self.assertTrue(all("not designed for flare lookup" in finding.message for finding in findings))

    def test_allows_supported_player_values_for_up_find_player_flare(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defconst flare-point 41)
(defrule
    (true)
=>
    (up-find-player-flare any-ally flare-point)
    (up-find-player-flare focus-player flare-point)
    (up-find-player-flare target-player flare-point)
    (up-find-player-flare 1 flare-point)
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings, [])

    def test_flags_binary_logical_operator_with_too_many_child_facts(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (or
        (true)
        (false)
        (game-time > 5)
    )
=>
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "logical-operator-arity-mismatch")
        self.assertEqual(findings[0].severity, "error")
        self.assertIn("or expects 2 child facts, got 3", findings[0].message)

    def test_allows_valid_multiline_nested_logical_operator(self) -> None:
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

            findings = lint_file(path)

        self.assertEqual(findings, [])

    def test_flags_not_with_too_many_child_facts(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (not
        (true)
        (false)
    )
=>
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "logical-operator-arity-mismatch")
        self.assertIn("not expects 1 child fact, got 2", findings[0].message)

    def test_allows_nested_logical_operator_for_three_alternatives(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (or
        (true)
        (or
            (false)
            (game-time > 5)
        )
    )
=>
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings, [])

    def test_allows_matching_symbol_family_in_direct_slots(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (true)
=>
    (set-goal goal-town-size 1)
    (set-strategic-number sn-maximum-town-size 1)
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings, [])

    def test_flags_literal_goal_id_outside_documented_range(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
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

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "command-numeric-range-mismatch")
        self.assertEqual(findings[0].severity, "warning")
        self.assertIn("GoalId", findings[0].message)
        self.assertIn("1 to 16000", findings[0].message)

    def test_lints_second_action_when_multiple_actions_share_one_line(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (true)
=> (disable-self) (set-goal 0 1))
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual([finding.code for finding in findings], ["command-numeric-range-mismatch"])

    def test_lints_single_line_defrule(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text("(defrule (true) => (disable-self) (set-goal 0 1))", encoding="utf-8")

            findings = lint_file(path)

        self.assertEqual([finding.code for finding in findings], ["command-numeric-range-mismatch"])

    def test_flags_single_line_defrule_missing_arrow(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text("(defrule (true) (disable-self))", encoding="utf-8")

            findings = lint_file(path)

        self.assertEqual([finding.code for finding in findings], ["defrule-missing-arrow"])

    def test_flags_empty_inline_defrule_missing_arrow(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text("(defrule)", encoding="utf-8")

            findings = lint_file(path)

        self.assertEqual([finding.code for finding in findings], ["defrule-missing-arrow"])

    def test_flags_rule_with_no_facts(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
=>
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual([finding.code for finding in findings], ["empty-fact"])
        self.assertEqual(findings[0].severity, "error")

    def test_flags_single_line_rule_with_no_facts(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text("(defrule => (disable-self))", encoding="utf-8")

            findings = lint_file(path)

        self.assertEqual([finding.code for finding in findings], ["empty-fact"])

    def test_flags_literal_typed_signal_id_outside_documented_range(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (true)
=>
    (up-set-signal c: 256 c: 1)
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "command-numeric-range-mismatch")
        self.assertIn("SignalId", findings[0].message)
        self.assertIn("0 to 255", findings[0].message)

    def test_flags_defconst_goal_id_outside_documented_range(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defconst gl-invalid 0)
(defrule
    (true)
=>
    (set-goal gl-invalid 1)
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "command-numeric-range-mismatch")
        self.assertIn("'gl-invalid'", findings[0].message)
        self.assertIn("defined as 0", findings[0].message)

    def test_flags_defconst_alias_goal_id_outside_documented_range(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defconst gl-zero 0)
(defconst gl-invalid gl-zero)
(defrule
    (true)
=>
    (set-goal gl-invalid 1)
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "command-numeric-range-mismatch")
        self.assertIn("'gl-invalid'", findings[0].message)
        self.assertIn("defined as 0", findings[0].message)

    def test_flags_package_wide_defconst_signal_id_outside_documented_range(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (true)
=>
    (up-set-signal c: gl-invalid-signal c: 1)
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(
                path,
                extra_constants={"gl-invalid-signal"},
                extra_constant_values={"gl-invalid-signal": 256},
            )

        self.assertEqual(findings[0].code, "command-numeric-range-mismatch")
        self.assertIn("'gl-invalid-signal'", findings[0].message)
        self.assertIn("defined as 256", findings[0].message)

    def test_allows_dynamic_typed_signal_id_range_operand(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defconst gl-signal-id 1)
(defrule
    (true)
=>
    (up-set-signal g: gl-signal-id c: 1)
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings, [])

    def test_allows_literal_ids_inside_documented_ranges(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defconst gl-valid 1)
(defrule
    (true)
=>
    (set-goal 1 1)
    (set-goal gl-valid 1)
    (set-shared-goal 256 1)
    (up-set-signal c: 255 c: 1)
    (acknowledge-taunt any-ally 255)
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings, [])

    def test_allows_unknown_constant_range_operand_without_guessing_value(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (true)
=>
    (set-goal gl-external 1)
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path, extra_constants={"gl-external"})

        self.assertEqual(findings, [])

    def test_allows_typed_goal_source_for_unit_id_slot(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (true)
=>
    (up-find-remote g: gl-drush-target-object c: 1)
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings, [])

    def test_flags_invalid_search_source(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
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

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "command-argument-mismatch")

    def test_allows_defined_search_source_alias(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defconst my-search-source search-local)
(defrule
    (true)
=>
    (up-set-target-object my-search-source c: 0)
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings, [])

    def test_flags_invalid_duc_action(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (true)
=>
    (up-find-local c: villager-class c: 1)
    (up-target-point 0 action-fly -1 -1)
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "command-argument-mismatch")

    def test_flags_goal_arity_mismatch(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (goal 1)
=>
    (do-nothing)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "command-arity-mismatch")

    def test_allows_bare_compare_operator_for_strategic_number(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defconst sn-maximum-town-size 126)
(defrule
    (strategic-number sn-maximum-town-size < 24)
=>
    (set-strategic-number sn-maximum-town-size 24)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings, [])

    def test_flags_invalid_compare_operator_for_goal_command(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (up-compare-goal 1 approx 2)
=>
    (do-nothing)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "command-argument-mismatch")

    def test_flags_invalid_math_operator_for_goal_command(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (true)
=>
    (up-modify-goal 1 plus 2)
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "command-argument-mismatch")

    def test_flags_classic_build_arity_mismatch(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (can-build house extra)
=>
    (build house)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "command-arity-mismatch")

    def test_flags_invalid_up_build_placement_type(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (true)
=>
    (up-build place-sky 0 c: house)
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "command-argument-mismatch")

    def test_flags_up_train_missing_type_prefix(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (true)
=>
    (up-train 0 villager villager)
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "command-typed-prefix-mismatch")

    def test_allows_build_train_research_schema_family(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defconst villager 83)
(defconst ri-loom 22)
(defconst goal-build-escrow-state 73)
(defrule
    (can-build house)
    (can-train villager)
    (can-research ri-loom)
=>
    (build house)
    (train villager)
    (research ri-loom)
)
(defrule
    (up-can-build goal-build-escrow-state c: house)
    (up-can-train goal-build-escrow-state c: villager)
    (up-can-research goal-build-escrow-state c: ri-loom)
=>
    (up-build place-normal goal-build-escrow-state c: house)
    (up-train goal-build-escrow-state c: villager)
    (up-research goal-build-escrow-state c: ri-loom)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings, [])

    def test_allows_availability_and_research_status_schema_family(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defconst villager 83)
(defconst ri-loom 22)
(defrule
    (building-available house)
    (unit-available villager)
    (research-available ri-loom)
    (research-completed ri-loom)
    (can-build-with-escrow house)
    (can-train-with-escrow villager)
    (can-research-with-escrow ri-loom)
    (up-research-status c: ri-loom >= research-pending)
=>
    (do-nothing)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings, [])

    def test_flags_invalid_research_status_state(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defconst ri-loom 22)
(defrule
    (up-research-status c: ri-loom >= research-maybe)
=>
    (do-nothing)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "command-argument-mismatch")

    def test_allows_resource_and_escrow_schema_family(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defconst town-center 109)
(defrule
    (food-amount < 100)
    (wood-amount >= 50)
    (gold-amount == 0)
    (stone-amount != 10)
    (resource-found food)
=>
    (set-escrow-percentage food 25)
    (release-escrow food)
    (up-release-escrow)
    (up-modify-escrow wood c:+ 10)
    (up-drop-resources gold c: 1)
    (up-gather-inside c: town-center c: 1)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings, [])

    def test_flags_invalid_escrow_resource(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (true)
=>
    (release-escrow berries)
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "command-argument-mismatch")

    def test_allows_count_schema_family(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defconst villager 83)
(defrule
    (unit-type-count villager > 0)
    (unit-type-count-total villager >= 1)
    (building-type-count house < 2)
    (building-type-count-total house <= 4)
    (population == 3)
    (population-cap != 5)
    (civilian-population > 0)
    (military-population == 0)
    (soldier-count == 0)
    (building-count > 0)
    (unit-count > 0)
    (idle-farm-count == 0)
=>
    (do-nothing)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings, [])

    def test_allows_object_count_aliases_from_inventory_notes(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (unit-type-count villager-wood < 10)
    (unit-type-count villager-food < 10)
    (unit-type-count-total trebuchet-set < 3)
=>
    (up-find-local c: villager-wood c: 1)
    (up-find-local c: villager-food c: 1)
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings, [])

    def test_explains_archived_non_de_direct_id_symbols(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (unit-type-count stable-tarkan < 1)
    (can-research ri-tracking)
=>
    (do-nothing)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        messages = [finding.message for finding in findings]
        self.assertEqual([finding.code for finding in findings], ["command-argument-mismatch", "command-argument-mismatch"])
        self.assertTrue(any("archived as non-DE" in message and "object registry" in message for message in messages))
        self.assertTrue(any("archived as non-DE" in message and "tech registry" in message for message in messages))

    def test_flags_invalid_count_compare_operator(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (population around 3)
=>
    (do-nothing)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "command-argument-mismatch")

    def test_allows_time_player_point_and_object_data_schema_family(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defconst timer-open 1)
(defconst point-x 41)
(defconst point-y 43)
(defconst out-goal 45)
(defrule
    (current-age == dark-age)
    (difficulty >= hard)
    (game-time < 60)
    (timer-triggered timer-open)
    (up-timer-status timer-open == timer-triggered)
    (player-in-game any-ally)
    (players-stance any-ally ally)
    (cc-players-unit-type-count any-ally villager > 0)
    (up-object-data object-data-id >= 0)
    (up-pending-objects c: house == 0)
    (up-pending-placement c: house)
=>
    (disable-timer timer-open)
    (enable-timer timer-open 1)
    (up-get-object-data object-data-id out-goal)
    (up-get-search-state out-goal)
    (up-get-point position-self point-x)
    (up-set-target-point point-x)
    (up-get-point-distance point-x point-y out-goal)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings, [])

    def test_flags_invalid_age_schema_argument(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (current-age == future-age)
=>
    (do-nothing)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "command-argument-mismatch")

    def test_flags_invalid_timer_state_schema_argument(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (up-timer-status 1 == timer-lost)
=>
    (do-nothing)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "command-argument-mismatch")

    def test_allows_chat_taunt_and_misc_schema_family(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (taunt-detected any-ally 199)
=>
    (acknowledge-taunt any-ally 199)
    (chat-to-all "hello")
    (chat-to-allies "allies")
    (chat-to-player my-player-number "player")
    (chat-local-to-self "local")
    (up-jump-rule 1)
    (do-nothing)
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings, [])

    def test_flags_unquoted_chat_text(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (true)
=>
    (chat-to-all hello)
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "command-argument-mismatch")

    def test_allows_string_defconst_for_text_argument(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defconst greeting "hello")
(defrule
    (true)
=>
    (chat-to-all greeting)
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings, [])

    def test_allows_search_filter_schema_family(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defconst point-a 41)
(defconst point-b 43)
(defrule
    (up-point-distance point-a point-b <= 10)
    (up-compare-const 1 == 1)
    (up-set-target-by-id c: 1)
    (up-add-object-by-id search-local c: 1)
    (up-find-resource c: food c: 1)
=>
    (up-full-reset-search)
    (up-reset-search 1 1 1 1)
    (up-remove-objects search-local object-data-id == 1)
    (up-clean-search search-local object-data-distance search-order-asc)
    (up-copy-point point-a point-b)
    (up-filter-distance c: -1 c: 10)
    (up-filter-status c: status-ready c: list-active)
    (up-filter-include -1 -1 -1 -1)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings, [])

    def test_flags_invalid_search_order_schema_argument(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (true)
=>
    (up-clean-search search-local object-data-distance search-order-sideways)
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "command-argument-mismatch")

    def test_allows_player_market_and_extended_up_schema_family(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defconst out-goal 45)
(defconst point-a 47)
(defconst point-b 49)
(defconst villager 83)
(defconst stance-no-attack 3)
(defrule
    (players-building-type-count any-ally house > 0)
    (players-unit-type-count any-ally villager > 0)
    (players-current-age any-ally >= dark-age)
    (players-military-population any-ally == 0)
    (players-population any-ally > 0)
    (players-building-count any-ally > 0)
    (players-stance any-ally ally)
    (stance-toward any-ally ally)
    (player-valid any-ally)
    (civ-selected briton)
    (map-type arabia)
    (map-type custom)
    (current-age-time >= 0)
    (enemy-buildings-in-town)
    (town-under-attack)
=>
    (do-nothing)
)
(defrule
    (dropsite-min-distance wood >= 0)
    (commodity-selling-price food > 0)
    (commodity-buying-price wood > 0)
    (can-afford-building house)
    (escrow-amount food >= 0)
    (up-projectile-detected projectile-any >= 0)
    (up-object-target-data object-data-id >= 0)
=>
    (buy-commodity food)
    (sell-commodity wood)
    (up-chat-data-to-all "value %d" c: 1)
    (up-chat-data-to-player my-player-number "value %d" c: 1)
    (up-modify-group-flag 1 c: 1)
    (up-reset-group c: 1)
    (up-create-group 0 0 c: 1)
    (up-assign-builders c: house c: 1)
    (up-set-placement-data my-player-number house c: 1)
    (up-set-offense-priority c: villager c: 1)
    (up-set-defense-priority c: house c: 1)
    (up-set-attack-stance villager c: stance-no-attack)
)
(defrule
    (up-point-contains point-a c: villager)
    (up-allied-goal any-ally out-goal >= 0)
    (up-can-build-line out-goal point-a c: house)
=>
    (up-get-fact game-time 0 out-goal)
    (up-get-focus-fact game-time 0 out-goal)
    (up-get-target-fact game-time 0 out-goal)
    (up-get-object-target-data object-data-id out-goal)
    (up-get-precise-time 0 out-goal)
    (up-jump-direct c: 1)
    (up-lerp-tiles point-a point-b c: 1)
    (up-cross-tiles point-a point-b c: 1)
    (up-filter-exclude -1 -1 -1 villager-class)
    (up-reset-filters)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings, [])

    def test_flags_invalid_commodity_schema_argument(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (true)
=>
    (buy-commodity gold)
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "command-argument-mismatch")

    def test_allows_remaining_common_corpus_schema_family(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defconst out-goal 45)
(defconst flag-goal 46)
(defconst villager 83)
(defrule
    (true)
    (death-match-game)
    (housing-headroom > 0)
    (up-players-in-game ally >= 1)
    (up-gaia-type-count c: food >= 0)
    (can-sell-commodity food)
    (can-buy-commodity wood)
    (up-enemy-units-in-town == 0)
    (up-allied-resource-amount any-ally amount-food >= 0)
    (up-resource-amount food >= 0)
    (up-compare-flag flag-goal == 1)
    (up-find-status-local c: villager c: 1)
    (up-find-status-remote c: villager c: 1)
=>
    (up-get-player-fact my-player-number game-time 0 out-goal)
    (up-modify-flag flag-goal c:= 1)
    (do-nothing)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings, [])

    def test_flags_invalid_resource_type_schema_argument(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (up-allied-resource-amount any-ally amount-snacks >= 0)
=>
    (do-nothing)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "command-argument-mismatch")

    def test_allows_extended_value_family_schema_arguments(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defconst point-a 41)
(defconst out-goal 45)
(defrule
    (event-detected trigger 1)
    (up-point-explored point-a == explored-active)
    (game-type == empire-wars)
    (map-size ludicrous)
    (starting-resources == medium-resources)
    (victory-condition conquest)
    (fe-sub-game-type == sub-game-type-empire-wars)
    (up-idle-unit-count idle-type-villager == 0)
=>
    (up-find-player ally find-closest out-goal)
    (up-send-scout group-type-land-explore scout-enemy)
    (up-reset-target-priorities priority-offense 0)
    (do-nothing)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings, [])

    def test_flags_invalid_extended_value_family_schema_argument(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (game-type == treaty-random-map)
=>
    (do-nothing)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "command-argument-mismatch")

    def test_allows_more_closed_value_family_schema_arguments(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defconst point-a 41)
(defconst terrain-out 43)
(defrule
    (can-build-wall 0 stone-wall)
    (can-build-wall 1 stone-wall-line)
    (up-point-terrain point-a == terrain-grass)
=>
    (build-wall 0 stone-wall)
    (build-wall 1 stone-wall-line)
    (set-difficulty-parameter ability-to-dodge-missiles 1)
    (up-filter-include -1 actionid-gather orderid-gather -1)
    (up-filter-exclude -1 actionid-attack orderid-attack -1)
    (up-get-point-terrain point-a terrain-out)
    (fe-cc-effect-amount effect-set-attribute 83 attribute-hp 5)
    (fe-cc-effect-percent effect-mul-attribute 83 attribute-speed 10)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings, [])

    def test_flags_invalid_wall_id_schema_argument(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (can-build-wall 0 crystal-wall)
=>
    (do-nothing)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings[0].code, "command-argument-mismatch")

    def test_allows_duc_action_specific_target_argument_slots(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (true)
=>
    (up-find-local c: barracks c: 1)
    (up-target-point 0 action-train c: villager)
    (disable-self)
)
""".strip(),
                encoding="utf-8",
            )

            findings = lint_file(path)

        self.assertEqual(findings, [])


if __name__ == "__main__":
    unittest.main()
