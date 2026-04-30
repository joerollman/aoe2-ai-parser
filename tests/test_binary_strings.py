from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from aoe2_ai_lab.binary_strings import (
    extract_strings,
    extract_userpatch_sections,
    filter_strings_dump,
    scan_strings,
    section_slug,
)


class BinaryStringsTests(unittest.TestCase):
    def test_extracts_ascii_and_utf16le_strings(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.bin"
            path.write_bytes(
                b"\x00DEBUGSPEEDS\x00"
                + b"\x00"
                + "up-get-point".encode("utf-16le")
                + b"\x00\x00"
            )

            strings = extract_strings(path, min_length=4)

        self.assertIn("DEBUGSPEEDS", strings)
        self.assertIn("up-get-point", strings)

    def test_scans_queries_case_insensitively_by_default(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.bin"
            path.write_bytes(b"\x00LOGSYSTEMS=AIScript\x00")

            results = scan_strings(path, ["logsystems"])

        self.assertEqual(results[0].query, "logsystems")
        self.assertEqual(results[0].matches, ("LOGSYSTEMS=AIScript",))

    def test_filters_ai_sections_identifiers_and_messages(self) -> None:
        lines = [
            "100:abc]$%___",
            "200:Defining UserPatch Extended Strategic Numbers",
            "208:sn-enable-boar-hunting",
            "240:sn-livestock-to-town-center",
            "300:Defining UserPatch Facts (operations)",
            "320:up-get-point",
            "400:This is a live boar, but boar hunting is not enabled",
        ]

        filtered = filter_strings_dump(lines, rejected_limit=10)

        self.assertIn("200:Defining UserPatch Extended Strategic Numbers", filtered.sections)
        self.assertIn("208:sn-enable-boar-hunting", filtered.sections)
        self.assertIn("up-get-point", filtered.identifiers)
        self.assertIn(
            "This is a live boar, but boar hunting is not enabled",
            filtered.messages,
        )
        self.assertIn(
            "This is a live boar, but boar hunting is not enabled",
            filtered.ai_messages,
        )
        self.assertIn("100:abc]$%___", filtered.rejected_sample)

    def test_extracts_userpatch_sections(self) -> None:
        lines = [
            "100:Defining UserPatch ActionIds",
            "120:action-move",
            "140:action-gather",
            "180:not an identifier",
            "200:Defining USerPatch Player Wildcards",
            "220:focus-player",
            "240:target-player",
            "280:Defining UserPatch ObjectData Constants",
            "300:object-data-id",
        ]

        sections = extract_userpatch_sections(lines)

        self.assertEqual(
            sections["Defining UserPatch ActionIds"],
            ["100:Defining UserPatch ActionIds", "120:action-move", "140:action-gather"],
        )
        self.assertEqual(
            sections["Defining USerPatch Player Wildcards"],
            [
                "200:Defining USerPatch Player Wildcards",
                "220:focus-player",
                "240:target-player",
            ],
        )
        self.assertEqual(
            sections["Defining UserPatch ObjectData Constants"],
            [
                "280:Defining UserPatch ObjectData Constants",
                "300:object-data-id",
            ],
        )

    def test_userpatch_section_slug(self) -> None:
        self.assertEqual(
            section_slug("Defining UserPatch ObjectData Constants"),
            "objectdata-constants",
        )


if __name__ == "__main__":
    unittest.main()
