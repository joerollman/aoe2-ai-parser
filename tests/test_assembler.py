from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from aoe2_ai_lab.assembler import assemble_per


class AssemblerTests(unittest.TestCase):
    def test_expands_load_directives(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp) / "root.per"
            tasks = Path(tmp) / "tasks"
            tasks.mkdir()
            (tasks / "one.per").write_text("(defrule\n    (true)\n=>\n    (do-nothing)\n)\n", encoding="utf-8")
            root.write_text('(defconst x 1)\n#load "tasks/one"\n', encoding="utf-8")

            assembled = assemble_per(root)

        self.assertIn("(defconst x 1)", assembled)
        self.assertIn("(do-nothing)", assembled)
        self.assertNotIn("#load", assembled)


if __name__ == "__main__":
    unittest.main()
