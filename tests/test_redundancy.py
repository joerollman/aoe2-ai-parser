from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from aoe2_ai_lab.redundancy import scan_redundancy


class RedundancyTests(unittest.TestCase):
    def test_finds_duplicate_action_blocks(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.per"
            path.write_text(
                """
(defrule
    (current-age == feudal-age)
=>
    (train archer)
)

(defrule
    (current-age == castle-age)
=>
    (train archer)
)
""".strip(),
                encoding="utf-8",
            )

            report = scan_redundancy([path])

        self.assertEqual(report.rule_count, 2)
        self.assertEqual(report.duplicate_action_blocks[0].count, 2)
        self.assertEqual(report.action_command_counts[0], ("train", 2))


if __name__ == "__main__":
    unittest.main()

