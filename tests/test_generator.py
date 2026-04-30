from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from aoe2_ai_lab.generator import (
    generate_goal_batch,
    generate_state_transition,
    insert_block,
    insert_block_into_file,
)


class GeneratorTests(unittest.TestCase):
    def test_inserts_and_replaces_block_in_section(self) -> None:
        source = """
; <aoe2-ai-lab:section state>
; </aoe2-ai-lab:section state>
""".lstrip()
        first = generate_goal_batch("state.opening", ["(true)"], [("goal-opening", "1")])
        second = generate_goal_batch("state.opening", ["(true)"], [("goal-opening", "2")])

        updated = insert_block(source, "state", first)
        replaced = insert_block(updated, "state", second)

        self.assertIn("(set-goal goal-opening 2)", replaced)
        self.assertNotIn("(set-goal goal-opening 1)", replaced)
        self.assertEqual(replaced.count("; <aoe2-ai-lab:block state.opening>"), 1)

    def test_appends_missing_section(self) -> None:
        block = generate_state_transition(
            "opening.feudal",
            "goal-opening",
            "dark",
            "feudal",
            ["(current-age == feudal-age)"],
        )

        updated = insert_block("; script\n", "state", block)

        self.assertIn("; <aoe2-ai-lab:section state>", updated)
        self.assertIn("(goal goal-opening dark)", updated)

    def test_inserts_into_file(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text("; script\n", encoding="utf-8")
            block = generate_goal_batch("state.setup", [], [("goal-a", "1")])

            insert_block_into_file(path, "state", block)

            text = path.read_text(encoding="utf-8")

        self.assertIn("(set-goal goal-a 1)", text)


if __name__ == "__main__":
    unittest.main()
