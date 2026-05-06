from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import textwrap


MAX_AISCRIPT_LINE_LENGTH = 255
DEFAULT_LINE_LENGTH = 255
SCRIPT_SUFFIXES = {".ai", ".per"}
CHAT_COMMANDS = {"chat-to-all", "chat-to-player"}


@dataclass(frozen=True)
class FormatOptions:
    max_line_length: int = DEFAULT_LINE_LENGTH
    format_chat: bool = False

    def __post_init__(self) -> None:
        if self.max_line_length < 40:
            raise ValueError("max line length must be at least 40")
        if self.max_line_length > MAX_AISCRIPT_LINE_LENGTH:
            raise ValueError("max line length cannot exceed 255")


@dataclass(frozen=True)
class FormatResult:
    path: Path
    changed: bool
    original_text: str
    formatted_text: str


def discover_script_files(path: Path, *, recursive: bool = True) -> list[Path]:
    if path.is_file():
        return [path] if path.suffix.lower() in SCRIPT_SUFFIXES else []
    if path.is_dir():
        iterator = path.rglob("*") if recursive else path.iterdir()
        return sorted(file for file in iterator if file.is_file() and file.suffix.lower() in SCRIPT_SUFFIXES)
    return []


def format_file(path: Path, options: FormatOptions | None = None) -> FormatResult:
    options = options or FormatOptions()
    original = path.read_text(encoding="utf-8", errors="replace")
    formatted = format_text(original, path.suffix.lower(), options)
    return FormatResult(path=path, changed=formatted != original, original_text=original, formatted_text=formatted)


def format_text(text: str, suffix: str = ".per", options: FormatOptions | None = None) -> str:
    options = options or FormatOptions()
    if suffix.lower() == ".ai":
        return ""

    dominant_separator = dominant_load_separator(text)
    raw_lines = text.splitlines()
    formatted_lines: list[str] = []
    for line in raw_lines:
        next_lines = format_line(line.rstrip(), options, dominant_separator)
        if next_lines and next_lines[0] == "" and should_drop_promoted_comment_separator(formatted_lines, next_lines):
            next_lines = next_lines[1:]
        formatted_lines.extend(next_lines)
    formatted_lines = ensure_defrule_separators(formatted_lines)
    formatted_lines = normalize_defrule_indentation(formatted_lines)
    return "\n".join(formatted_lines) + "\n"


def should_drop_promoted_comment_separator(formatted_lines: list[str], next_lines: list[str]) -> bool:
    if formatted_lines and not formatted_lines[-1].strip():
        return True
    previous_nonempty = next((line for line in reversed(formatted_lines) if line.strip()), "")
    if not previous_nonempty:
        return True
    if previous_nonempty.strip() == "=>":
        return True
    if is_comment_line(previous_nonempty):
        return True
    code = next_lines[-1].strip() if next_lines else ""
    return code.startswith("(defrule")


def ensure_defrule_separators(lines: list[str]) -> list[str]:
    separated: list[str] = []
    for line in lines:
        stripped = line.strip()
        if is_defrule_line(stripped) and should_insert_defrule_separator(separated):
            separated.append("")
        separated.append(line)
    return separated


def should_insert_defrule_separator(lines: list[str]) -> bool:
    if not lines:
        return False
    if not lines[-1].strip():
        return False
    previous_nonempty = next((line for line in reversed(lines) if line.strip()), "")
    return bool(previous_nonempty) and not is_comment_line(previous_nonempty)


def format_line(line: str, options: FormatOptions, dominant_separator: str | None) -> list[str]:
    line = normalize_load_path_separator(line, dominant_separator)
    if is_chat_line(line) and not options.format_chat:
        return [line]
    promoted = promote_long_inline_comment(line, options)
    if promoted is not None:
        return promoted
    if is_comment_line(line):
        return wrap_comment_line(line, options.max_line_length)
    split = split_top_level_expressions(line)
    if split is not None:
        return split
    return [line]


def normalize_defrule_indentation(lines: list[str]) -> list[str]:
    normalized: list[str] = []
    in_rule = False
    rule_balance = 0
    for line in lines:
        stripped = line.strip()
        if not stripped:
            normalized.append("")
            continue

        if is_defrule_line(stripped) and not in_rule:
            normalized.append(stripped)
            rule_balance = paren_delta(stripped)
            in_rule = rule_balance > 0
            continue

        if in_rule:
            if stripped == "=>" or (stripped == ")" and rule_balance <= 1):
                normalized.append(stripped)
            else:
                normalized.append(f"    {stripped}")
            rule_balance += paren_delta(stripped)
            if rule_balance <= 0:
                in_rule = False
                rule_balance = 0
            continue

        normalized.append(line.rstrip())
    return normalized


def is_defrule_line(stripped: str) -> bool:
    code = line_without_comment(stripped).strip()
    return code == "(defrule" or code.startswith("(defrule ")


def paren_delta(line: str) -> int:
    code = line_without_comment(line)
    delta = 0
    in_string = False
    escaped = False
    for char in code:
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if char == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if char == "(":
            delta += 1
        elif char == ")":
            delta -= 1
    return delta


def line_without_comment(line: str) -> str:
    comment_index = inline_comment_index(line)
    if comment_index is None:
        return line
    return line[:comment_index]


def is_comment_line(line: str) -> bool:
    return line.lstrip().startswith(";")


def is_chat_line(line: str) -> bool:
    return any(re.search(rf"\(\s*{re.escape(command)}\b", line) for command in CHAT_COMMANDS)


def dominant_load_separator(text: str) -> str | None:
    slash_count = 0
    backslash_count = 0
    for target in load_targets(text):
        slash_count += target.count("/")
        backslash_count += target.count("\\")
    if slash_count > backslash_count:
        return "/"
    if backslash_count > slash_count:
        return "\\"
    return None


def load_targets(text: str) -> list[str]:
    targets: list[str] = []
    patterns = [
        re.compile(r"(\(\s*(?:load|include)\s+\")([^\"]+)(\")"),
        re.compile(r"(^\s*#load\s+\")([^\"]+)(\")", re.MULTILINE),
        re.compile(r"(\(\s*load-random\s+\")([^\"]+)(\")"),
    ]
    for pattern in patterns:
        targets.extend(match.group(2) for match in pattern.finditer(text))
    return targets


def normalize_load_path_separator(line: str, separator: str | None) -> str:
    if separator is None:
        return line
    patterns = [
        re.compile(r"(\(\s*(?:load|include)\s+\")([^\"]+)(\")"),
        re.compile(r"(^\s*#load\s+\")([^\"]+)(\")"),
        re.compile(r"(\(\s*load-random\s+\")([^\"]+)(\")"),
    ]

    def replace(match: re.Match[str]) -> str:
        target = match.group(2)
        normalized = target.replace("/", separator).replace("\\", separator)
        return f"{match.group(1)}{normalized}{match.group(3)}"

    for pattern in patterns:
        line = pattern.sub(replace, line)
    return line


def promote_long_inline_comment(line: str, options: FormatOptions) -> list[str] | None:
    comment_index = inline_comment_index(line)
    if comment_index is None or len(line) <= options.max_line_length:
        return None
    code = line[:comment_index].rstrip()
    comment = line[comment_index:].strip()
    if not code or not comment:
        return None
    indent = re.match(r"\s*", line).group(0)
    wrapped = wrap_comment_text(comment[1:].strip(), indent, options.max_line_length)
    return ["", *wrapped, code]


def inline_comment_index(line: str) -> int | None:
    in_string = False
    escaped = False
    for index, char in enumerate(line):
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if char == '"':
            in_string = not in_string
            continue
        if char == ";" and not in_string:
            return index
    return None


def wrap_comment_line(line: str, max_line_length: int) -> list[str]:
    if len(line) <= max_line_length:
        return [line]
    stripped = line.lstrip()
    indent = line[: len(line) - len(stripped)]
    return wrap_comment_text(stripped[1:].strip(), indent, max_line_length)


def wrap_comment_text(text: str, indent: str, max_line_length: int) -> list[str]:
    prefix = f"{indent}; "
    width = max(1, max_line_length - len(prefix))
    wrapped = textwrap.wrap(
        text,
        width=width,
        break_long_words=True,
        break_on_hyphens=False,
    )
    if not wrapped:
        return [prefix.rstrip()]
    return [f"{prefix}{part}" for part in wrapped]


def split_top_level_expressions(line: str) -> list[str] | None:
    indent = re.match(r"\s*", line).group(0)
    stripped = line.strip()
    if not stripped or stripped.startswith(";") or stripped.startswith("#"):
        return None
    expressions = top_level_expressions(stripped)
    if len(expressions) < 2:
        return None
    if not only_whitespace_between_expressions(stripped, expressions):
        return None
    if any(expression.startswith("(defrule") for expression in expressions):
        return None
    return [f"{indent}{expression}" for expression in expressions]


def only_whitespace_between_expressions(text: str, expressions: list[str]) -> bool:
    index = 0
    for expression in expressions:
        next_index = text.find(expression, index)
        if next_index < 0:
            return False
        if text[index:next_index].strip():
            return False
        index = next_index + len(expression)
    return not text[index:].strip()


def top_level_expressions(text: str) -> list[str]:
    expressions: list[str] = []
    start: int | None = None
    depth = 0
    in_string = False
    escaped = False
    for index, char in enumerate(text):
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if char == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if char == "(":
            if depth == 0:
                start = index
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0 and start is not None:
                expressions.append(text[start : index + 1])
                start = None
            if depth < 0:
                return []
    if depth != 0:
        return []
    return expressions
