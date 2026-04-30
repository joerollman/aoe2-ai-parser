from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re


@dataclass(frozen=True)
class SourceSpan:
    start_line: int
    start_col: int
    end_line: int
    end_col: int


@dataclass(frozen=True)
class Atom:
    value: str
    line: int
    start_col: int = field(default=0, compare=False)
    end_col: int = field(default=0, compare=False)


@dataclass(frozen=True)
class Expression:
    head: str
    args: tuple[Atom | "Expression", ...]
    line: int
    source: str
    start_col: int = 0
    end_col: int = 0
    head_start_col: int = 0
    head_end_col: int = 0

    @property
    def span(self) -> SourceSpan:
        return SourceSpan(self.line, self.start_col, self.line, self.end_col)

    @property
    def head_span(self) -> SourceSpan:
        return SourceSpan(self.line, self.head_start_col, self.line, self.head_end_col)


@dataclass(frozen=True)
class Rule:
    start_line: int
    end_line: int
    facts: tuple[str, ...]
    actions: tuple[str, ...]
    fact_lines: tuple[int, ...] = ()
    action_lines: tuple[int, ...] = ()
    fact_exprs: tuple[Expression, ...] = ()
    action_exprs: tuple[Expression, ...] = ()
    confidence: str = "definite"


@dataclass(frozen=True)
class Script:
    path: Path
    rules: tuple[Rule, ...]
    constants: dict[str, int]
    constant_names: frozenset[str] = frozenset()
    constant_tokens: dict[str, str] | None = None


@dataclass(frozen=True)
class SourceLine:
    number: int
    text: str
    active: bool = True
    confidence: str = "definite"


@dataclass(frozen=True)
class PreprocessorIssue:
    line: int
    code: str
    message: str
    confidence: str = "definite"


@dataclass(frozen=True)
class PreprocessorFrame:
    parent_active: bool
    condition_known: bool
    condition_value: bool
    in_else: bool = False

    @property
    def active(self) -> bool:
        if not self.parent_active:
            return False
        if not self.condition_known:
            return True
        return not self.condition_value if self.in_else else self.condition_value

    @property
    def conditional(self) -> bool:
        return self.parent_active and not self.condition_known


LOAD_IF_DEFINED_RE = re.compile(r"^#load-if-defined\s+([A-Za-z_][A-Za-z0-9_-]*)\b")
LOAD_IF_NOT_DEFINED_RE = re.compile(r"^#load-if-not-defined\s+([A-Za-z_][A-Za-z0-9_-]*)\b")
PREPROCESSOR_CONTROL_RE = re.compile(r"^#(?:load-if-defined|load-if-not-defined|else|end-if)\b")
MAX_PREPROCESSOR_NESTING_DEPTH = 50


def is_escaped_quote(text: str, index: int) -> bool:
    """Return true when text[index] is escaped by an odd number of backslashes."""
    backslashes = 0
    cursor = index - 1
    while cursor >= 0 and text[cursor] == "\\":
        backslashes += 1
        cursor -= 1
    return backslashes % 2 == 1


def read_script_text(path: str | Path) -> str:
    script_path = Path(path)
    try:
        return script_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return script_path.read_text(encoding="cp1252")


def strip_comment(line: str) -> str:
    """Remove AoE2 AI comments while preserving code before the semicolon."""
    in_string = False
    for index, char in enumerate(line):
        if char == '"' and not is_escaped_quote(line, index):
            in_string = not in_string
        elif char == ";" and not in_string:
            return line[:index].strip()
    return line.strip()


def directive_spans(code: str) -> tuple[tuple[int, str], ...]:
    directive_starts: list[int] = []
    in_string = False
    for index, char in enumerate(code):
        if char == '"' and not is_escaped_quote(code, index):
            in_string = not in_string
            continue
        if char == "#" and not in_string:
            directive_starts.append(index)

    spans: list[tuple[int, str]] = []
    for position, start in enumerate(directive_starts):
        end = directive_starts[position + 1] if position + 1 < len(directive_starts) else -1
        segment = code[start:] if end == -1 else code[start:end]
        segment = segment.strip()
        if segment:
            spans.append((start, segment))
    return tuple(spans)


def directive_tokens(code: str) -> tuple[str, ...]:
    tokens: list[str] = []
    for _start, segment in directive_spans(code):
        tokens.append(segment)
    return tuple(tokens)


def preprocess_source_lines(lines: list[str]) -> tuple[SourceLine, ...]:
    defined: set[str] = set()
    stack: list[PreprocessorFrame] = []
    source_lines: list[SourceLine] = []

    def current_active() -> bool:
        return all(frame.active for frame in stack)

    def current_confidence() -> str:
        return "conditional" if any(frame.conditional for frame in stack) else "definite"

    for number, raw_line in enumerate(lines, start=1):
        code = strip_comment(raw_line)
        line_active = current_active()
        line_confidence = current_confidence()
        if line_active:
            const_name = parse_defconst_name(raw_line)
            if const_name is not None:
                defined.add(const_name)

        inline_match = LOAD_IF_DEFINED_RE.match(code) or LOAD_IF_NOT_DEFINED_RE.match(code)
        inline_directives = directive_spans(code) if inline_match else ()
        inline_end = next(
            (
                start
                for start, directive in inline_directives[1:]
                if directive.startswith("#else") or directive.startswith("#end-if")
            ),
            None,
        )
        has_inline_end_if = any(directive.startswith("#end-if") for _start, directive in inline_directives[1:])
        if inline_match and inline_end is not None and has_inline_end_if:
            name = inline_match.group(1)
            condition_known = name in defined
            if LOAD_IF_NOT_DEFINED_RE.match(code):
                condition_value = not condition_known
            else:
                condition_value = condition_known
            payload = code[inline_match.end() : inline_end].strip()
            payload_active = line_active and (not condition_known or condition_value)
            if payload_active and payload:
                const_name = parse_defconst_name(payload)
                if const_name is not None:
                    defined.add(const_name)
            confidence = "conditional" if (line_confidence == "conditional" or not condition_known) else "definite"
            source_lines.append(
                SourceLine(
                    number=number,
                    text=payload,
                    active=payload_active and bool(payload),
                    confidence=confidence,
                )
            )
            continue

        directives = directive_tokens(code)
        is_directive_only = (
            bool(directives)
            and code.startswith("#")
            and all(PREPROCESSOR_CONTROL_RE.match(directive) for directive in directives)
        )
        for directive in directives:
            if match := LOAD_IF_DEFINED_RE.match(directive):
                name = match.group(1)
                parent_active = current_active()
                condition_known = name in defined
                stack.append(
                    PreprocessorFrame(
                        parent_active=parent_active,
                        condition_known=condition_known,
                        condition_value=condition_known,
                    )
                )
                continue
            if match := LOAD_IF_NOT_DEFINED_RE.match(directive):
                name = match.group(1)
                parent_active = current_active()
                condition_known = name in defined
                stack.append(
                    PreprocessorFrame(
                        parent_active=parent_active,
                        condition_known=condition_known,
                        condition_value=not condition_known,
                    )
                )
                continue
            if directive.startswith("#else"):
                if stack:
                    frame = stack.pop()
                    stack.append(
                        PreprocessorFrame(
                            parent_active=frame.parent_active,
                            condition_known=frame.condition_known,
                            condition_value=frame.condition_value,
                            in_else=not frame.in_else,
                        )
                    )
                continue
            if directive.startswith("#end-if"):
                if stack:
                    stack.pop()
                continue

        source_lines.append(
            SourceLine(
                number=number,
                text=raw_line,
                active=line_active and not is_directive_only,
                confidence=line_confidence,
            )
        )

    return tuple(source_lines)


def collect_preprocessor_issues(lines: list[str]) -> tuple[PreprocessorIssue, ...]:
    defined: set[str] = set()
    stack: list[PreprocessorFrame] = []
    issues: list[PreprocessorIssue] = []

    def current_active() -> bool:
        return all(frame.active for frame in stack)

    def current_confidence() -> str:
        return "conditional" if any(frame.conditional for frame in stack) else "definite"

    for number, raw_line in enumerate(lines, start=1):
        code = strip_comment(raw_line)
        line_active = current_active()
        line_confidence = current_confidence()
        if line_active:
            const_name = parse_defconst_name(raw_line)
            if const_name is not None:
                defined.add(const_name)

        for directive in directive_tokens(code):
            if directive.startswith("#load-if-defined"):
                match = LOAD_IF_DEFINED_RE.match(directive)
                if not match:
                    issues.append(
                        PreprocessorIssue(
                            number,
                            "malformed-preprocessor-directive",
                            "#load-if-defined requires a symbol name",
                            line_confidence,
                        )
                    )
                    continue
                name = match.group(1)
                condition_known = name in defined
                stack.append(
                    PreprocessorFrame(
                        parent_active=current_active(),
                        condition_known=condition_known,
                        condition_value=condition_known,
                    )
                )
                if len(stack) > MAX_PREPROCESSOR_NESTING_DEPTH:
                    issues.append(
                        PreprocessorIssue(
                            number,
                            "preprocessor-nesting-depth-exceeded",
                            f"conditional loading commands can nest at most {MAX_PREPROCESSOR_NESTING_DEPTH} levels deep",
                            line_confidence,
                        )
                    )
                continue

            if directive.startswith("#load-if-not-defined"):
                match = LOAD_IF_NOT_DEFINED_RE.match(directive)
                if not match:
                    issues.append(
                        PreprocessorIssue(
                            number,
                            "malformed-preprocessor-directive",
                            "#load-if-not-defined requires a symbol name",
                            line_confidence,
                        )
                    )
                    continue
                name = match.group(1)
                condition_known = name in defined
                stack.append(
                    PreprocessorFrame(
                        parent_active=current_active(),
                        condition_known=condition_known,
                        condition_value=not condition_known,
                    )
                )
                if len(stack) > MAX_PREPROCESSOR_NESTING_DEPTH:
                    issues.append(
                        PreprocessorIssue(
                            number,
                            "preprocessor-nesting-depth-exceeded",
                            f"conditional loading commands can nest at most {MAX_PREPROCESSOR_NESTING_DEPTH} levels deep",
                            line_confidence,
                        )
                    )
                continue

            if directive.startswith("#else"):
                if not stack:
                    issues.append(
                        PreprocessorIssue(
                            number,
                            "unexpected-preprocessor-else",
                            "#else has no matching #load-if-defined or #load-if-not-defined",
                            line_confidence,
                        )
                    )
                    continue
                frame = stack.pop()
                if frame.in_else:
                    issues.append(
                        PreprocessorIssue(
                            number,
                            "duplicate-preprocessor-else",
                            "#else appears more than once for the same conditional block",
                            line_confidence,
                        )
                    )
                stack.append(
                    PreprocessorFrame(
                        parent_active=frame.parent_active,
                        condition_known=frame.condition_known,
                        condition_value=frame.condition_value,
                        in_else=True,
                    )
                )
                continue

            if directive.startswith("#end-if"):
                if not stack:
                    issues.append(
                        PreprocessorIssue(
                            number,
                            "unexpected-preprocessor-end-if",
                            "#end-if has no matching #load-if-defined or #load-if-not-defined",
                            line_confidence,
                        )
                    )
                    continue
                stack.pop()
                continue

    for frame in stack:
        issues.append(
            PreprocessorIssue(
                len(lines) if lines else 1,
                "unterminated-preprocessor-conditional",
                "#load-if-defined or #load-if-not-defined is missing #end-if",
                "conditional" if frame.conditional else "definite",
            )
        )

    return tuple(issues)


def active_source_lines(path: str | Path) -> tuple[SourceLine, ...]:
    return tuple(line for line in preprocess_source_lines(read_script_text(path).splitlines()) if line.active)


def preprocessor_issues(path: str | Path) -> tuple[PreprocessorIssue, ...]:
    return collect_preprocessor_issues(read_script_text(path).splitlines())


def count_code_parens(line: str) -> int:
    """Count parentheses outside quoted strings."""
    balance = 0
    in_string = False
    for index, char in enumerate(line):
        if char == '"' and not is_escaped_quote(line, index):
            in_string = not in_string
        elif not in_string and char == "(":
            balance += 1
        elif not in_string and char == ")":
            balance -= 1
    return balance


def remove_last_code_closing_paren(line: str) -> str:
    in_string = False
    last_closing = -1
    for index, char in enumerate(line):
        if char == '"' and not is_escaped_quote(line, index):
            in_string = not in_string
        elif char == ")" and not in_string:
            last_closing = index
    if last_closing != -1:
        return f"{line[:last_closing]}{line[last_closing + 1:]}"
    return line


def first_symbol(expr: str) -> str:
    expr = expr.strip()
    if not expr.startswith("("):
        return ""
    body = expr[1:].strip()
    if not body:
        return ""
    return body.split(None, 1)[0].rstrip(")")


def iter_expression_heads(expr: str) -> tuple[str, ...]:
    heads: list[str] = []
    index = 0
    while index < len(expr):
        if expr[index] != "(":
            index += 1
            continue
        index += 1
        while index < len(expr) and expr[index].isspace():
            index += 1
        start = index
        while index < len(expr) and not expr[index].isspace() and expr[index] not in "()":
            index += 1
        if index > start:
            heads.append(expr[start:index])
    return tuple(heads)


def tokenize_expression(expr: str, line: int, column_offset: int = 0) -> tuple[Atom, ...]:
    tokens: list[Atom] = []
    index = 0
    while index < len(expr):
        char = expr[index]
        if char.isspace():
            index += 1
            continue
        if char in "()":
            tokens.append(Atom(char, line, column_offset + index, column_offset + index + 1))
            index += 1
            continue
        if char == '"':
            start = index
            index += 1
            while index < len(expr) and (expr[index] != '"' or is_escaped_quote(expr, index)):
                index += 1
            if index < len(expr):
                index += 1
            tokens.append(Atom(expr[start:index], line, column_offset + start, column_offset + index))
            continue
        start = index
        while index < len(expr) and not expr[index].isspace() and expr[index] not in "()":
            index += 1
        tokens.append(Atom(expr[start:index], line, column_offset + start, column_offset + index))
    return tuple(tokens)


def parse_expression(expr: str, line: int, column_offset: int = 0) -> Expression | None:
    tokens = tokenize_expression(expr, line, column_offset)

    def parse_at(index: int) -> tuple[Expression | Atom | None, int]:
        if index >= len(tokens):
            return None, index
        token = tokens[index]
        if token.value != "(":
            return token, index + 1
        start_line = token.line
        start_col = token.start_col
        index += 1
        if index >= len(tokens):
            return None, index
        head_token = tokens[index]
        index += 1
        args: list[Atom | Expression] = []
        while index < len(tokens):
            current = tokens[index]
            if current.value == ")":
                return (
                    Expression(
                        head=head_token.value,
                        args=tuple(args),
                        line=start_line,
                        source=expr,
                        start_col=start_col,
                        end_col=current.end_col,
                        head_start_col=head_token.start_col,
                        head_end_col=head_token.end_col,
                    ),
                    index + 1,
                )
            parsed, index = parse_at(index)
            if parsed is not None:
                args.append(parsed)
        return (
            Expression(
                head=head_token.value,
                args=tuple(args),
                line=start_line,
                source=expr,
                start_col=start_col,
                end_col=tokens[index - 1].end_col if index > 0 else start_col,
                head_start_col=head_token.start_col,
                head_end_col=head_token.end_col,
            ),
            index,
        )

    parsed, _ = parse_at(0)
    if isinstance(parsed, Expression):
        return parsed
    return None


def parse_expressions(
    exprs: list[str],
    lines: list[int],
    columns: list[int] | None = None,
) -> tuple[Expression, ...]:
    parsed: list[Expression] = []
    column_values = columns if columns is not None else [0] * len(exprs)
    for expr, line, column in zip(exprs, lines, column_values):
        expression = parse_expression(expr, line, column)
        if expression is not None:
            parsed.append(expression)
    return tuple(parsed)


def split_top_level_expression_spans(code: str) -> tuple[tuple[str, int], ...]:
    segments: list[tuple[str, int]] = []
    start = 0
    last_end = 0
    balance = 0
    in_string = False
    for index, char in enumerate(code):
        if char == '"' and not is_escaped_quote(code, index):
            in_string = not in_string
        elif not in_string and char == "(":
            if balance == 0 and code[last_end:index].strip():
                return ((code, 0),)
            if balance == 0:
                start = index
            balance += 1
        elif not in_string and char == ")":
            balance -= 1
            if balance == 0:
                raw_segment = code[start:index + 1]
                segment = raw_segment.strip()
                if segment:
                    leading = len(raw_segment) - len(raw_segment.lstrip())
                    segments.append((segment, start + leading))
                last_end = index + 1
            if balance < 0:
                return ((code, 0),)
    if balance != 0:
        return ((code, 0),)
    if code[last_end:].strip():
        return ((code, 0),)
    return tuple(segments) if segments else ((code, 0),)


def split_top_level_expressions(code: str) -> tuple[str, ...]:
    return tuple(segment for segment, _column in split_top_level_expression_spans(code))


def split_rule_arrow(code: str) -> tuple[str, str] | None:
    in_quote = False
    escaped = False
    for index, char in enumerate(code):
        if escaped:
            escaped = False
            continue
        if char == "\\" and in_quote:
            escaped = True
            continue
        if char == '"':
            in_quote = not in_quote
            continue
        if not in_quote and code.startswith("=>", index):
            return code[:index], code[index + 2 :]
    return None


def is_defrule_start(code: str) -> bool:
    if not code.startswith("(defrule"):
        return False
    if len(code) == len("(defrule"):
        return True
    return code[len("(defrule")] in {")"} or code[len("(defrule")].isspace()


def parse_defconst(line: str) -> tuple[str, int] | None:
    parsed = parse_defconst_token(line)
    if parsed is None:
        return None
    name, value = parsed
    try:
        return name, int(value)
    except ValueError:
        return None


def parse_defconst_token(line: str) -> tuple[str, str] | None:
    code = strip_comment(line)
    if not code.startswith("(defconst "):
        return None
    body = code.removeprefix("(defconst ").strip()
    if body.endswith(")"):
        body = body[:-1].strip()
    parts = body.split(None, 1)
    if len(parts) != 2:
        return None
    name, value = parts
    if value.startswith('"'):
        closing_index = -1
        for index in range(1, len(value)):
            if value[index] == '"' and not is_escaped_quote(value, index):
                closing_index = index
                break
        if closing_index == -1:
            return None
        if value[closing_index + 1 :].strip():
            return None
        return name, value[: closing_index + 1]
    if len(value.split()) != 1:
        return None
    return name, value


def parse_defconst_name(line: str) -> str | None:
    code = strip_comment(line)
    if not code.startswith("(defconst "):
        return None
    parts = code.removeprefix("(defconst ").rstrip(")").split(None, 1)
    if len(parts) != 2:
        return None
    return parts[0]


def resolve_constant_tokens(tokens: dict[str, str]) -> dict[str, int]:
    resolved: dict[str, int] = {}

    def resolve(name: str, stack: set[str]) -> int | None:
        if name in resolved:
            return resolved[name]
        if name in stack:
            return None
        token = tokens.get(name)
        if token is None:
            return None
        try:
            value = int(token)
        except ValueError:
            value = resolve(token, {*stack, name})
            if value is None:
                return None
        resolved[name] = value
        return value

    for name in tokens:
        resolve(name, set())
    return resolved


def parse_script(path: str | Path) -> Script:
    script_path = Path(path)
    lines = active_source_lines(script_path)
    rules: list[Rule] = []
    constant_tokens: dict[str, str] = {}
    constant_names: set[str] = set()

    in_rule = False
    start_line = 0
    facts: list[str] = []
    actions: list[str] = []
    fact_lines: list[int] = []
    action_lines: list[int] = []
    fact_columns: list[int] = []
    action_columns: list[int] = []
    target = facts
    target_lines = fact_lines
    target_columns = fact_columns
    rule_balance = 0
    rule_confidence = "definite"

    def append_segments(
        destination: list[str],
        destination_lines: list[int],
        destination_columns: list[int],
        code: str,
        line_number: int,
        column_offset: int,
    ) -> None:
        for segment, segment_column in split_top_level_expression_spans(code):
            destination.append(segment)
            destination_lines.append(line_number)
            destination_columns.append(column_offset + segment_column)

    def record_rule_code(code: str, line_number: int, column_offset: int = 0) -> None:
        nonlocal target, target_lines, target_columns
        arrow_split = split_rule_arrow(code)
        if arrow_split is not None:
            before_arrow, after_arrow = arrow_split
            before_raw = before_arrow
            after_raw = after_arrow
            before_arrow = before_raw.strip()
            after_arrow = after_raw.strip()
            if before_arrow:
                before_offset = column_offset + len(before_raw) - len(before_raw.lstrip())
                append_segments(target, target_lines, target_columns, before_arrow, line_number, before_offset)
            target = actions
            target_lines = action_lines
            target_columns = action_columns
            if after_arrow:
                after_offset = column_offset + len(before_raw) + 2 + len(after_raw) - len(after_raw.lstrip())
                append_segments(target, target_lines, target_columns, after_arrow, line_number, after_offset)
        elif code:
            append_segments(target, target_lines, target_columns, code, line_number, column_offset)

    def finish_rule(end_line: int) -> None:
        nonlocal in_rule, rule_balance
        rules.append(
            Rule(
                start_line=start_line,
                end_line=end_line,
                facts=tuple(facts),
                actions=tuple(actions),
                fact_lines=tuple(fact_lines),
                action_lines=tuple(action_lines),
                fact_exprs=parse_expressions(facts, fact_lines, fact_columns),
                action_exprs=parse_expressions(actions, action_lines, action_columns),
                confidence=rule_confidence,
            )
        )
        in_rule = False
        rule_balance = 0

    last_line_number = 1
    for source_line in lines:
        index = source_line.number
        raw_line = source_line.text
        last_line_number = index
        const_name = parse_defconst_name(raw_line)
        if const_name is not None:
            constant_names.add(const_name)

        const_token = parse_defconst_token(raw_line)
        if const_token is not None:
            constant_tokens[const_token[0]] = const_token[1]

        code = strip_comment(raw_line)
        if not code:
            continue

        if is_defrule_start(code):
            in_rule = True
            start_line = index
            rule_balance = count_code_parens(code)
            facts = []
            actions = []
            fact_lines = []
            action_lines = []
            fact_columns = []
            action_columns = []
            target = facts
            target_lines = fact_lines
            target_columns = fact_columns
            rule_confidence = source_line.confidence
            if code == "(defrule":
                continue
            inline_payload = code.removeprefix("(defrule").strip()
            inline_payload_offset = raw_line.find(inline_payload) if inline_payload else 0
            closes_rule = rule_balance == 0
            line_to_record = remove_last_code_closing_paren(inline_payload).strip() if closes_rule else inline_payload
            line_to_record_offset = raw_line.find(line_to_record, inline_payload_offset) if line_to_record else inline_payload_offset
            record_rule_code(line_to_record, index, max(line_to_record_offset, 0))
            if closes_rule:
                finish_rule(index)
            continue

        if not in_rule:
            continue

        next_rule_balance = rule_balance + count_code_parens(code)
        closes_rule = next_rule_balance == 0

        line_to_record = remove_last_code_closing_paren(code).strip() if closes_rule else code
        line_to_record_offset = raw_line.find(line_to_record) if line_to_record else 0

        record_rule_code(line_to_record, index, max(line_to_record_offset, 0))

        rule_balance = next_rule_balance
        if closes_rule:
            finish_rule(index)
            continue

    if in_rule:
        rules.append(
            Rule(
                start_line=start_line,
                end_line=last_line_number,
                facts=tuple(facts),
                actions=tuple(actions),
                fact_lines=tuple(fact_lines),
                action_lines=tuple(action_lines),
                fact_exprs=parse_expressions(facts, fact_lines, fact_columns),
                action_exprs=parse_expressions(actions, action_lines, action_columns),
                confidence=rule_confidence,
            )
        )

    return Script(
        path=script_path,
        rules=tuple(rules),
        constants=resolve_constant_tokens(constant_tokens),
        constant_names=frozenset(constant_names),
        constant_tokens=constant_tokens,
    )
