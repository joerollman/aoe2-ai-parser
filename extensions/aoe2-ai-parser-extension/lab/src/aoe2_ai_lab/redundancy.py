from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .parser import Rule, first_symbol, parse_script


@dataclass(frozen=True)
class RuleRef:
    path: Path
    start_line: int

    def format(self) -> str:
        return f"{self.path}:{self.start_line}"


@dataclass(frozen=True)
class DuplicateGroup:
    fingerprint: str
    count: int
    refs: tuple[RuleRef, ...]


@dataclass(frozen=True)
class RedundancyReport:
    files: tuple[Path, ...]
    rule_count: int
    duplicate_rules: tuple[DuplicateGroup, ...]
    duplicate_action_blocks: tuple[DuplicateGroup, ...]
    action_command_counts: tuple[tuple[str, int], ...]
    fact_command_counts: tuple[tuple[str, int], ...]
    shape_counts: tuple[tuple[str, int], ...]


def find_per_files(paths: Iterable[str | Path]) -> list[Path]:
    files: list[Path] = []
    for value in paths:
        path = Path(value)
        if path.is_dir():
            files.extend(sorted(path.rglob("*.per")))
        elif path.suffix.lower() == ".per":
            files.append(path)
    return sorted(dict.fromkeys(files))


def normalize_expr(expr: str) -> str:
    return " ".join(expr.strip().split()).lower()


def normalize_rule(rule: Rule) -> str:
    facts = "\n".join(normalize_expr(fact) for fact in rule.facts)
    actions = "\n".join(normalize_expr(action) for action in rule.actions)
    return f"{facts}\n=>\n{actions}"


def normalize_action_block(rule: Rule) -> str:
    return "\n".join(normalize_expr(action) for action in rule.actions)


def rule_shape(rule: Rule) -> str:
    fact_symbols = ",".join(first_symbol(fact) or "?" for fact in rule.facts)
    action_symbols = ",".join(first_symbol(action) or "?" for action in rule.actions)
    return f"facts[{fact_symbols}]=>actions[{action_symbols}]"


def _duplicate_groups(groups: dict[str, list[RuleRef]], limit: int) -> tuple[DuplicateGroup, ...]:
    duplicates = [
        DuplicateGroup(fingerprint=fingerprint, count=len(refs), refs=tuple(refs))
        for fingerprint, refs in groups.items()
        if len(refs) > 1 and fingerprint
    ]
    duplicates.sort(key=lambda group: (-group.count, group.refs[0].format()))
    return tuple(duplicates[:limit])


def scan_redundancy(paths: Iterable[str | Path], limit: int = 10) -> RedundancyReport:
    files = find_per_files(paths)
    duplicate_rule_refs: dict[str, list[RuleRef]] = defaultdict(list)
    duplicate_action_refs: dict[str, list[RuleRef]] = defaultdict(list)
    fact_command_counts: Counter[str] = Counter()
    action_command_counts: Counter[str] = Counter()
    shape_counter: Counter[str] = Counter()
    rule_count = 0

    for file in files:
        script = parse_script(file)
        for rule in script.rules:
            ref = RuleRef(file, rule.start_line)
            rule_count += 1
            duplicate_rule_refs[normalize_rule(rule)].append(ref)
            duplicate_action_refs[normalize_action_block(rule)].append(ref)
            shape_counter[rule_shape(rule)] += 1

            for fact in rule.facts:
                fact_command_counts[first_symbol(fact) or "?"] += 1
            for action in rule.actions:
                action_command_counts[first_symbol(action) or "?"] += 1

    return RedundancyReport(
        files=tuple(files),
        rule_count=rule_count,
        duplicate_rules=_duplicate_groups(duplicate_rule_refs, limit),
        duplicate_action_blocks=_duplicate_groups(duplicate_action_refs, limit),
        action_command_counts=tuple(action_command_counts.most_common(limit)),
        fact_command_counts=tuple(fact_command_counts.most_common(limit)),
        shape_counts=tuple(shape_counter.most_common(limit)),
    )


def _format_refs(group: DuplicateGroup, max_refs: int) -> str:
    shown = ", ".join(ref.format() for ref in group.refs[:max_refs])
    remaining = group.count - max_refs
    if remaining > 0:
        return f"{shown}, ... +{remaining} more"
    return shown


def format_report(report: RedundancyReport, max_refs: int = 8) -> str:
    lines: list[str] = [
        f"files: {len(report.files)}",
        f"rules: {report.rule_count}",
        "",
        "top fact commands:",
    ]
    lines.extend(f"  {name}: {count}" for name, count in report.fact_command_counts)
    lines.append("")
    lines.append("top action commands:")
    lines.extend(f"  {name}: {count}" for name, count in report.action_command_counts)
    lines.append("")
    lines.append("top rule shapes:")
    lines.extend(f"  {count}x {shape}" for shape, count in report.shape_counts)
    lines.append("")
    lines.append("duplicate full rules:")
    if report.duplicate_rules:
        for group in report.duplicate_rules:
            refs = _format_refs(group, max_refs)
            lines.append(f"  {group.count}x {refs}")
    else:
        lines.append("  none")
    lines.append("")
    lines.append("duplicate action blocks:")
    if report.duplicate_action_blocks:
        for group in report.duplicate_action_blocks:
            refs = _format_refs(group, max_refs)
            lines.append(f"  {group.count}x {refs}")
    else:
        lines.append("  none")
    return "\n".join(lines)
