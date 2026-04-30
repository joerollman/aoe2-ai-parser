from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re


ASCII_PRINTABLE_RE = re.compile(rb"[\x20-\x7e]{3,}")
OFFSET_LINE_RE = re.compile(r"^(?P<offset>\d+):(?P<text>.*)$")
AI_IDENTIFIER_RE = re.compile(
    r"^(?:sn|up|xs|cc|ri|ta|goal|strategic|object|action|class|cmdid|position)-[a-z0-9-]+$"
)
USERPATCH_ENTRY_RE = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)+$")
LIKELY_MESSAGE_RE = re.compile(r"^[A-Za-z][A-Za-z0-9 ,.'\"%()/_:\[\]-]{19,}$")

AI_SECTION_HEADINGS = (
    "Defining UserPatch",
)


@dataclass(frozen=True)
class StringScanResult:
    query: str
    matches: tuple[str, ...]


@dataclass(frozen=True)
class FilteredStrings:
    sections: tuple[str, ...]
    identifiers: tuple[str, ...]
    messages: tuple[str, ...]
    ai_messages: tuple[str, ...]
    rejected_sample: tuple[str, ...]


def extract_ascii_strings(data: bytes, min_length: int) -> set[str]:
    strings: set[str] = set()
    for match in ASCII_PRINTABLE_RE.finditer(data):
        value = match.group().decode("ascii", errors="ignore")
        if len(value) >= min_length:
            strings.add(value)
    return strings


def extract_utf16le_strings(data: bytes, min_length: int) -> set[str]:
    strings: set[str] = set()
    for offset in (0, 1):
        current = bytearray()
        index = offset
        while index + 1 < len(data):
            char = data[index]
            nul = data[index + 1]
            if 0x20 <= char <= 0x7E and nul == 0:
                current.append(char)
            else:
                if len(current) >= min_length:
                    strings.add(current.decode("ascii", errors="ignore"))
                current.clear()
            index += 2

        if len(current) >= min_length:
            strings.add(current.decode("ascii", errors="ignore"))

    return strings


def extract_strings(path: str | Path, min_length: int = 4) -> set[str]:
    data = Path(path).read_bytes()
    return extract_ascii_strings(data, min_length) | extract_utf16le_strings(data, min_length)


def scan_strings(
    path: str | Path,
    queries: list[str],
    *,
    min_length: int = 4,
    ignore_case: bool = True,
) -> list[StringScanResult]:
    strings = extract_strings(path, min_length=min_length)
    if ignore_case:
        haystack = [(value, value.lower()) for value in strings]
        normalized_queries = [(query, query.lower()) for query in queries]
    else:
        haystack = [(value, value) for value in strings]
        normalized_queries = [(query, query) for query in queries]

    results: list[StringScanResult] = []
    for original_query, normalized_query in normalized_queries:
        matches = sorted(
            value
            for value, normalized_value in haystack
            if normalized_query in normalized_value
        )
        results.append(StringScanResult(original_query, tuple(matches)))
    return results


def parse_offset_line(line: str) -> tuple[int | None, str]:
    match = OFFSET_LINE_RE.match(line)
    if not match:
        return None, line.strip()
    return int(match.group("offset")), match.group("text").strip()


def punctuation_ratio(value: str) -> float:
    if not value:
        return 1.0
    punctuation = sum(1 for char in value if not char.isalnum() and not char.isspace())
    return punctuation / len(value)


def letter_ratio(value: str) -> float:
    if not value:
        return 0.0
    letters = sum(1 for char in value if char.isalpha())
    return letters / len(value)


def is_likely_message(value: str) -> bool:
    if not LIKELY_MESSAGE_RE.match(value):
        return False
    if AI_IDENTIFIER_RE.match(value):
        return False
    if punctuation_ratio(value) > 0.25:
        return False
    if letter_ratio(value) < 0.45:
        return False
    return True


def is_ai_identifier(value: str) -> bool:
    return bool(AI_IDENTIFIER_RE.match(value))


def is_likely_ai_message(value: str) -> bool:
    lowered = value.lower()
    ai_terms = (
        " ai",
        "ai ",
        "strategic",
        "sn-",
        "up-",
        "boar",
        "town center",
        "villager",
        "gather",
        "build",
        "exploration",
        "dropsite",
        "attack group",
        "escrow",
        "goal",
        "taunt",
        "patrol",
        "scout",
    )
    return is_likely_message(value) and any(term in lowered for term in ai_terms)


def filter_strings_dump(lines: list[str], *, rejected_limit: int = 500) -> FilteredStrings:
    sections: list[str] = []
    identifiers: set[str] = set()
    messages: set[str] = set()
    ai_messages: set[str] = set()
    rejected: list[str] = []

    section_active = False
    for raw_line in lines:
        line = raw_line.rstrip("\r\n")
        offset, text = parse_offset_line(line)
        if not text:
            continue

        if any(text.startswith(heading) for heading in AI_SECTION_HEADINGS):
            section_active = True
            sections.append(line)
            continue

        if section_active:
            if text.startswith("Defining ") and text not in AI_SECTION_HEADINGS:
                section_active = False
            elif is_ai_identifier(text):
                sections.append(line)
            elif text.startswith("Defining "):
                sections.append(line)
            else:
                section_active = False

        if is_ai_identifier(text):
            identifiers.add(text)
        elif is_likely_message(text):
            messages.add(text)
            if is_likely_ai_message(text):
                ai_messages.add(text)
        elif len(rejected) < rejected_limit:
            rejected.append(line)

    return FilteredStrings(
        sections=tuple(sections),
        identifiers=tuple(sorted(identifiers)),
        messages=tuple(sorted(messages)),
        ai_messages=tuple(sorted(ai_messages)),
        rejected_sample=tuple(rejected),
    )


def write_filtered_strings(
    dump_path: str | Path,
    output_dir: str | Path,
    *,
    rejected_limit: int = 500,
) -> FilteredStrings:
    lines = Path(dump_path).read_text(encoding="utf-8", errors="replace").splitlines()
    filtered = filter_strings_dump(lines, rejected_limit=rejected_limit)
    target_dir = Path(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    (target_dir / "aoe2de-ai-sections.txt").write_text(
        "\n".join(filtered.sections) + "\n",
        encoding="utf-8",
    )
    (target_dir / "aoe2de-ai-identifiers.txt").write_text(
        "\n".join(filtered.identifiers) + "\n",
        encoding="utf-8",
    )
    (target_dir / "aoe2de-ai-debug-messages.txt").write_text(
        "\n".join(filtered.messages) + "\n",
        encoding="utf-8",
    )
    (target_dir / "aoe2de-ai-diagnostic-messages.txt").write_text(
        "\n".join(filtered.ai_messages) + "\n",
        encoding="utf-8",
    )
    (target_dir / "aoe2de-rejected-strings-sample.txt").write_text(
        "\n".join(filtered.rejected_sample) + "\n",
        encoding="utf-8",
    )
    return filtered


def section_slug(heading: str) -> str:
    value = heading.lower()
    value = value.replace("defining userpatch", "").strip()
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value or "userpatch"


def extract_userpatch_sections(lines: list[str]) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {}
    current_heading: str | None = None
    current_lines: list[str] = []

    for raw_line in lines:
        line = raw_line.rstrip("\r\n")
        _, text = parse_offset_line(line)
        if text.lower().startswith("defining userpatch"):
            if current_heading is not None:
                sections[current_heading] = current_lines
            current_heading = text
            current_lines = [line]
            continue

        if current_heading is None:
            continue

        if USERPATCH_ENTRY_RE.match(text):
            current_lines.append(line)
            continue

        sections[current_heading] = current_lines
        current_heading = None
        current_lines = []

    if current_heading is not None:
        sections[current_heading] = current_lines

    return sections


def write_userpatch_sections(dump_path: str | Path, output_dir: str | Path) -> dict[str, list[str]]:
    lines = Path(dump_path).read_text(encoding="utf-8", errors="replace").splitlines()
    sections = extract_userpatch_sections(lines)
    target_dir = Path(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    index_lines = [
        "# UserPatch Registration Sections",
        "",
        "Extracted from the local AoE2 DE executable string dump.",
        "",
        "These sections validate names and categories present in the binary.",
        "They do not provide full command syntax, defaults, or behavior semantics.",
        "",
    ]

    for heading, section_lines in sorted(sections.items()):
        slug = section_slug(heading)
        file_name = f"userpatch-{slug}.txt"
        (target_dir / file_name).write_text(
            "\n".join(section_lines) + "\n",
            encoding="utf-8",
        )
        item_count = max(len(section_lines) - 1, 0)
        index_lines.append(f"- [{heading}]({file_name}) - {item_count} entries")

    (target_dir / "userpatch-sections.md").write_text(
        "\n".join(index_lines) + "\n",
        encoding="utf-8",
    )
    return sections
