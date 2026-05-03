from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from .airef_registry import default_registry_path, load_registry, resolve_reference, search_registry
from .airef_scraper import (
    scrape_rms_fixtures,
    scrape_rms_topics,
    scrape_airef_commands,
    scrape_airef_objects,
    scrape_airef_parameters,
    scrape_airef_strategic_numbers,
    scrape_airef_techs,
    scrape_airef_value_families,
    scrape_xs_constants,
    scrape_xs_functions,
)
from .ai_package import find_include_targets, find_load_references, inspect_package_integrity, lint_package_root
from .assembler import assemble_per
from .binary_strings import scan_strings, write_filtered_strings, write_userpatch_sections
from .formatter import FormatOptions, discover_script_files, format_file, format_text
from .generator import (
    generate_goal_batch,
    generate_sn_defaults,
    generate_state_transition,
    insert_block_into_file,
    parse_assignment,
)
from .linter import CONFIDENCE_ORDER, SEVERITY_ORDER, Finding, has_failure, lint_file
from .parser import is_escaped_quote, parse_script, read_script_text, resolve_constant_tokens
from .redundancy import format_report, scan_redundancy


DEFAULT_CATEGORY_EXPLANATION = "Review this category against the local reference data and surrounding script context."
DIAGNOSTIC_REGISTRY_PATH = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "workflows"
    / "validator-diagnostic-codes.json"
)


def suppression_comment(code: str, *, next_line: bool = False) -> str:
    directive = "aoe2-ai-parser-disable-next-line" if next_line else "aoe2-ai-parser-disable-line"
    return f"; {directive} {code}"


def suppress_finding_in_file(path: Path, line: int, code: str, *, next_line: bool = False) -> None:
    if line < 1:
        raise ValueError("line must be 1 or greater")
    lines = path.read_text(encoding="utf-8").splitlines()
    comment = suppression_comment(code, next_line=next_line)
    if next_line:
        insert_index = min(line - 1, len(lines))
        if insert_index > 0:
            previous_indent = re.match(r"\s*", lines[insert_index - 1]).group(0)
        elif insert_index < len(lines):
            previous_indent = re.match(r"\s*", lines[insert_index]).group(0)
        else:
            previous_indent = ""
        lines.insert(insert_index, f"{previous_indent}{comment}")
    else:
        if line > len(lines):
            raise ValueError(f"line {line} is beyond end of file")
        if comment not in lines[line - 1]:
            lines[line - 1] = f"{lines[line - 1]} {comment}"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
DIAGNOSTIC_REGISTRY_MARKDOWN_PATH = DIAGNOSTIC_REGISTRY_PATH.with_suffix(".md")


@dataclass(frozen=True)
class LogCleanupCandidate:
    path: Path
    size: int


def find_log_cleanup_candidates(logs_root: Path, keep_latest: int) -> list[LogCleanupCandidate]:
    if not logs_root.exists():
        return []

    timestamped_dirs = sorted(
        [
            path
            for path in logs_root.iterdir()
            if path.is_dir() and path.name != "SlowLog"
        ],
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    preserved_dirs = set(timestamped_dirs[:keep_latest])
    candidates: list[LogCleanupCandidate] = []

    for path in timestamped_dirs[keep_latest:]:
        size = sum(file.stat().st_size for file in path.rglob("*") if file.is_file())
        candidates.append(LogCleanupCandidate(path, size))

    slow_log = logs_root / "SlowLog"
    if slow_log.exists():
        preserved_cutoff = min(
            (path.stat().st_mtime for path in preserved_dirs),
            default=float("inf"),
        )
        for file in slow_log.glob("*.txt"):
            if file.stat().st_mtime < preserved_cutoff:
                candidates.append(LogCleanupCandidate(file, file.stat().st_size))

    return candidates


def remove_log_candidate(candidate: LogCleanupCandidate) -> None:
    if candidate.path.is_dir():
        shutil.rmtree(candidate.path)
    else:
        candidate.path.unlink()


def find_de_profile_dirs(profiles_root: Path) -> list[Path]:
    if not profiles_root.exists():
        return []
    return sorted(
        path
        for path in profiles_root.iterdir()
        if path.is_dir() and path.name.isdigit()
    )


def install_rms_files(rms_dir: Path, profiles_root: Path) -> list[Path]:
    rms_files = sorted(
        path for path in rms_dir.glob("*") if path.suffix.lower() in {".rms", ".rms2"}
    )
    if not rms_files:
        raise ValueError(f"no .rms or .rms2 files found in {rms_dir}")

    targets: list[Path] = []
    for profile in find_de_profile_dirs(profiles_root):
        target = profile / "resources" / "_common" / "random-map-scripts"
        target.mkdir(parents=True, exist_ok=True)
        for rms_file in rms_files:
            shutil.copy2(rms_file, target / rms_file.name)
        targets.append(target)
    return targets


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="aoe2-ai-parser")
    subparsers = parser.add_subparsers(dest="command", required=True)

    lint = subparsers.add_parser("lint", help="lint a .per AI script")
    lint.add_argument("path", type=Path)
    lint.add_argument(
        "--profile",
        choices=["default", "corpus"],
        default="default",
        help="lint profile; corpus suppresses intentional compatibility alias noise",
    )
    lint.add_argument(
        "--suppress-code",
        action="append",
        default=[],
        help="suppress a finding code for this run; may be provided multiple times",
    )
    lint.add_argument(
        "--json",
        action="store_true",
        help="emit machine-readable lint results with source spans",
    )

    lint_package = subparsers.add_parser(
        "lint-package", help="lint AI package roots using reachable #load/load files"
    )
    lint_package.add_argument("path", type=Path)
    lint_package.add_argument(
        "--profile",
        choices=["default", "corpus"],
        default="corpus",
        help="lint profile to use for reachable package files",
    )
    lint_package.add_argument(
        "--max-findings",
        type=int,
        default=50,
        help="maximum findings to print per package root; use 0 for no limit",
    )
    lint_package.add_argument(
        "--summary",
        action="store_true",
        help="print grouped package findings instead of individual line findings",
    )
    lint_package.add_argument(
        "--fail-level",
        choices=["error", "warning", "info"],
        default="error",
        help="minimum severity that makes lint-package return a failing exit code",
    )
    lint_package.add_argument(
        "--fail-confidence",
        choices=["definite", "conditional"],
        default="definite",
        help="maximum preprocessor confidence that can fail lint-package; conditional includes uncertain branches",
    )
    lint_package.add_argument(
        "--json",
        action="store_true",
        help="emit machine-readable package lint results",
    )
    lint_package.add_argument(
        "--output",
        type=Path,
        help="write machine-readable package lint JSON to this path instead of stdout",
    )
    lint_package.add_argument(
        "--report",
        type=Path,
        help="write a verbose Markdown package lint report to this path",
    )
    lint_package.add_argument(
        "--suppress-code",
        action="append",
        default=[],
        help="suppress a finding code for this package run; may be provided multiple times",
    )

    suppress = subparsers.add_parser(
        "suppress-finding", help="insert an inline suppression comment for one diagnostic"
    )
    suppress.add_argument("path", type=Path)
    suppress.add_argument("line", type=int)
    suppress.add_argument("code", help="diagnostic code to suppress, or 'all'")
    suppress.add_argument(
        "--next-line",
        action="store_true",
        help="insert a suppression comment before the target line instead of appending to it",
    )

    diagnostics = subparsers.add_parser(
        "diagnostics",
        help="list or resolve validator diagnostic codes",
    )
    diagnostics.add_argument(
        "code",
        nargs="?",
        help="optional diagnostic code to resolve",
    )
    diagnostics.add_argument(
        "--json",
        action="store_true",
        help="emit machine-readable diagnostic registry entries",
    )

    stats = subparsers.add_parser("stats", help="print basic script stats")
    stats.add_argument("path", type=Path)

    formatter = subparsers.add_parser(
        "format",
        help="format .per files and enforce empty .ai entry files",
    )
    formatter.add_argument("path", type=Path)
    formatter.add_argument(
        "--write",
        action="store_true",
        help="write formatted files in place; default is dry-run",
    )
    formatter.add_argument(
        "--check",
        action="store_true",
        help="return 1 if any files would change",
    )
    formatter.add_argument(
        "--stdout",
        action="store_true",
        help="print the formatted content for a single file instead of writing it",
    )
    formatter.add_argument(
        "--stdin",
        action="store_true",
        help="read script text from stdin and print formatted text; path is used only for its suffix",
    )
    formatter.add_argument(
        "--max-line-length",
        type=int,
        default=255,
        help="wrap comment lines at this length; cannot exceed 255",
    )
    formatter.add_argument(
        "--format-chat",
        action="store_true",
        help="allow formatting chat-to-all/chat-to-player lines; default leaves chat lines unchanged",
    )

    redundancy = subparsers.add_parser(
        "redundancy", help="scan .per files for repeated rule patterns"
    )
    redundancy.add_argument("paths", nargs="+", type=Path)
    redundancy.add_argument("--limit", type=int, default=10)
    redundancy.add_argument("--max-refs", type=int, default=8)

    generate = subparsers.add_parser("generate", help="generate reusable .per blocks")
    generate_subparsers = generate.add_subparsers(dest="template", required=True)

    sn_defaults = generate_subparsers.add_parser(
        "sn-defaults", help="generate one-shot strategic number defaults"
    )
    sn_defaults.add_argument("--id", default="init.sn-defaults")
    sn_defaults.add_argument("--section", default="init")
    sn_defaults.add_argument("--insert", type=Path)

    goal_batch = generate_subparsers.add_parser(
        "goal-batch", help="generate a one-shot rule that sets several goals"
    )
    goal_batch.add_argument("--id", required=True)
    goal_batch.add_argument("--fact", action="append", default=[])
    goal_batch.add_argument("--set", action="append", default=[], dest="assignments")
    goal_batch.add_argument("--section", default="state")
    goal_batch.add_argument("--insert", type=Path)
    goal_batch.add_argument("--keep-enabled", action="store_true")

    transition = generate_subparsers.add_parser(
        "state-transition", help="generate a guarded goal state transition"
    )
    transition.add_argument("--id", required=True)
    transition.add_argument("--goal", required=True)
    transition.add_argument("--from", required=True, dest="from_value")
    transition.add_argument("--to", required=True, dest="to_value")
    transition.add_argument("--fact", action="append", default=[])
    transition.add_argument("--section", default="state")
    transition.add_argument("--insert", type=Path)
    transition.add_argument("--keep-enabled", action="store_true")

    install = subparsers.add_parser(
        "install-ai", help="lint and copy an AI package into DE profile AI folders"
    )
    install.add_argument("package_dir", type=Path)
    install.add_argument(
        "--profiles-root",
        type=Path,
        default=Path.home() / "Games" / "Age of Empires 2 DE",
    )

    install_rms = subparsers.add_parser(
        "install-rms", help="copy local RMS test maps into DE profile folders"
    )
    install_rms.add_argument("rms_dir", type=Path)
    install_rms.add_argument(
        "--profiles-root",
        type=Path,
        default=Path.home() / "Games" / "Age of Empires 2 DE",
    )

    clean_logs = subparsers.add_parser(
        "clean-logs", help="list or delete old AoE2 DE log runs"
    )
    clean_logs.add_argument(
        "--logs-root",
        type=Path,
        default=Path.home() / "Games" / "Age of Empires 2 DE" / "logs",
    )
    clean_logs.add_argument(
        "--keep-latest",
        type=int,
        default=3,
        help="number of newest timestamped log folders to preserve",
    )
    clean_logs.add_argument(
        "--delete",
        action="store_true",
        help="actually delete candidates; omitted means dry run",
    )
    clean_logs.add_argument(
        "--max-output",
        type=int,
        default=25,
        help="maximum candidates to print before summarizing the remainder",
    )

    strings = subparsers.add_parser(
        "scan-strings",
        help="search ASCII/UTF-16LE strings in a local binary for candidate names",
    )
    strings.add_argument("path", type=Path)
    strings.add_argument("--query", action="append", default=[])
    strings.add_argument("--query-file", type=Path)
    strings.add_argument("--min-length", type=int, default=4)
    strings.add_argument("--case-sensitive", action="store_true")
    strings.add_argument("--max-matches", type=int, default=20)

    filter_strings = subparsers.add_parser(
        "filter-strings",
        help="filter a Sysinternals strings dump into AI-oriented views",
    )
    filter_strings.add_argument("dump_path", type=Path)
    filter_strings.add_argument(
        "--output-dir",
        type=Path,
        default=Path("docs") / "extracted" / "raw" / "aoe2de",
    )
    filter_strings.add_argument("--rejected-limit", type=int, default=500)

    extract_userpatch = subparsers.add_parser(
        "extract-userpatch-sections",
        help="extract contiguous UserPatch registration sections from a strings dump",
    )
    extract_userpatch.add_argument("dump_path", type=Path)
    extract_userpatch.add_argument(
        "--output-dir",
        type=Path,
        default=Path("docs") / "extracted" / "raw" / "aoe2de" / "userpatch-sections",
    )

    search_registry_cmd = subparsers.add_parser(
        "search-registry",
        help="search the local curated AIRef registry",
    )
    search_registry_cmd.add_argument("query")
    search_registry_cmd.add_argument(
        "--path",
        type=Path,
        default=default_registry_path(),
    )
    search_registry_cmd.add_argument(
        "--kind",
        action="append",
        default=[],
        help="limit results to specific entry kinds such as concept, article, validated-command, project-command-note, command-inventory, parameter-inventory, strategic-number-inventory, value-family, value-entry, object-inventory, tech-inventory, xs-function-inventory, xs-constant-inventory, rms-fixture, rms-topic-inventory, binary-family, binary-token, command-category, command-type, or command-complexity",
    )
    search_registry_cmd.add_argument("--limit", type=int, default=10)

    resolve_reference_cmd = subparsers.add_parser(
        "resolve-reference",
        help="resolve one token against local offline AoE2 reference data",
    )
    resolve_reference_cmd.add_argument("query")
    resolve_reference_cmd.add_argument(
        "--path",
        type=Path,
        default=default_registry_path(),
    )
    resolve_reference_cmd.add_argument(
        "--kind",
        action="append",
        default=[],
        help="limit resolution to specific entry kinds",
    )
    resolve_reference_cmd.add_argument("--related-limit", type=int, default=5)

    scrape_airef = subparsers.add_parser(
        "scrape-airef-commands",
        help="scrape AIRef command pages into a local JSON inventory",
    )
    scrape_airef.add_argument(
        "--output",
        type=Path,
        default=Path("docs") / "extracted" / "inventories" / "airef-command-inventory.json",
    )
    scrape_airef.add_argument(
        "--cache-dir",
        type=Path,
        default=Path("docs") / "extracted" / "raw" / "airef-command-pages",
    )
    scrape_airef.add_argument(
        "--source-dir",
        type=Path,
        default=Path("docs") / "extracted" / "sources" / "airef-source",
    )
    scrape_airef.add_argument("--delay", type=float, default=0.0)
    scrape_airef.add_argument("--limit", type=int)

    scrape_airef_params = subparsers.add_parser(
        "scrape-airef-parameters",
        help="scrape AIRef parameter reference into a local JSON inventory",
    )
    scrape_airef_params.add_argument(
        "--output",
        type=Path,
        default=Path("docs") / "extracted" / "inventories" / "airef-parameter-inventory.json",
    )
    scrape_airef_params.add_argument(
        "--source-dir",
        type=Path,
        default=Path("docs") / "extracted" / "sources" / "airef-source",
    )

    scrape_airef_sns = subparsers.add_parser(
        "scrape-airef-strategic-numbers",
        help="scrape AIRef strategic number reference into a local JSON inventory",
    )
    scrape_airef_sns.add_argument(
        "--output",
        type=Path,
        default=Path("docs") / "extracted" / "inventories" / "airef-strategic-number-inventory.json",
    )
    scrape_airef_sns.add_argument(
        "--source-dir",
        type=Path,
        default=Path("docs") / "extracted" / "sources" / "airef-source",
    )

    scrape_airef_values = subparsers.add_parser(
        "scrape-airef-value-families",
        help="derive local enum/value inventories from AIRef parameter data",
    )
    scrape_airef_values.add_argument(
        "--output",
        type=Path,
        default=Path("docs") / "extracted" / "inventories" / "airef-value-family-inventory.json",
    )
    scrape_airef_values.add_argument(
        "--source-dir",
        type=Path,
        default=Path("docs") / "extracted" / "sources" / "airef-source",
    )

    scrape_airef_objects = subparsers.add_parser(
        "scrape-airef-objects",
        help="scrape AIRef objects table into a local JSON inventory",
    )
    scrape_airef_objects.add_argument(
        "--output",
        type=Path,
        default=Path("docs") / "extracted" / "inventories" / "airef-object-inventory.json",
    )
    scrape_airef_objects.add_argument(
        "--source-dir",
        type=Path,
        default=Path("docs") / "extracted" / "sources" / "airef-source",
    )

    scrape_airef_techs = subparsers.add_parser(
        "scrape-airef-techs",
        help="scrape AIRef techs table into a local JSON inventory",
    )
    scrape_airef_techs.add_argument(
        "--output",
        type=Path,
        default=Path("docs") / "extracted" / "inventories" / "airef-tech-inventory.json",
    )
    scrape_airef_techs.add_argument(
        "--source-dir",
        type=Path,
        default=Path("docs") / "extracted" / "sources" / "airef-source",
    )

    scrape_xs = subparsers.add_parser(
        "scrape-xs-functions",
        help="build a local XS function inventory from extracted DE XS strings",
    )
    scrape_xs.add_argument(
        "--output",
        type=Path,
        default=Path("docs") / "extracted" / "inventories" / "xs-function-inventory.json",
    )
    scrape_xs.add_argument(
        "--signatures-path",
        type=Path,
        default=Path("docs") / "extracted" / "raw" / "aoe2de" / "aoe2de-xs-function-signatures.txt",
    )
    scrape_xs.add_argument(
        "--names-path",
        type=Path,
        default=Path("docs") / "extracted" / "raw" / "aoe2de" / "aoe2de-xs-function-names.txt",
    )
    scrape_xs.add_argument(
        "--strings-path",
        type=Path,
        default=Path("docs") / "extracted" / "raw" / "aoe2de" / "aoe2de-xs-strings.txt",
    )

    scrape_rms = subparsers.add_parser(
        "scrape-rms-fixtures",
        help="build a local registry of project RMS test fixtures",
    )
    scrape_rms.add_argument(
        "--output",
        type=Path,
        default=Path("docs") / "extracted" / "inventories" / "rms-fixture-registry.json",
    )
    scrape_rms.add_argument(
        "--rms-dir",
        type=Path,
        default=Path("rms"),
    )

    scrape_rms_topics_cmd = subparsers.add_parser(
        "scrape-rms-topics",
        help="build a local topic index from the RMS guide text export",
    )
    scrape_rms_topics_cmd.add_argument(
        "--output",
        type=Path,
        default=Path("docs") / "extracted" / "inventories" / "rms-topic-inventory.json",
    )
    scrape_rms_topics_cmd.add_argument(
        "--guide-path",
        type=Path,
        default=Path("docs") / "extracted" / "raw" / "rms" / "rms-reference-google-doc.txt",
    )

    scrape_xs_constants_cmd = subparsers.add_parser(
        "scrape-xs-constants",
        help="build a local XS constant inventory from the UGC constants reference",
    )
    scrape_xs_constants_cmd.add_argument(
        "--output",
        type=Path,
        default=Path("docs") / "extracted" / "inventories" / "xs-constant-inventory.json",
    )
    scrape_xs_constants_cmd.add_argument(
        "--ugc-constants-path",
        type=Path,
        default=Path("docs") / "extracted" / "raw" / "xs" / "ugc-xs-constants.html",
    )

    return parser


def format_finding_summary(findings: list[tuple[Path, Finding]]) -> list[str]:
    severity_counts = Counter(finding.severity for _, finding in findings)
    confidence_counts = Counter(finding.confidence for _, finding in findings)
    code_counts = Counter(finding.code for _, finding in findings)
    file_counts = Counter(path for path, _ in findings)
    lines: list[str] = []
    severity_parts = [
        f"{severity}: {severity_counts[severity]}"
        for severity in ("error", "warning", "info")
        if severity_counts[severity]
    ]
    if severity_parts:
        lines.append(f"  severity: {', '.join(severity_parts)}")
    confidence_parts = [
        f"{confidence}: {confidence_counts[confidence]}"
        for confidence in ("definite", "conditional")
        if confidence_counts[confidence]
    ]
    if confidence_parts:
        lines.append(f"  confidence: {', '.join(confidence_parts)}")
    if code_counts:
        lines.append("  codes:")
        for code, count in code_counts.most_common(10):
            lines.append(f"    {code}: {count}")
    if file_counts:
        lines.append("  top files:")
        for path, count in file_counts.most_common(5):
            lines.append(f"    {path}: {count}")
    return lines


def package_has_failure(
    findings: list[tuple[Path, Finding]],
    fail_level: str,
    fail_confidence: str = "definite",
) -> bool:
    threshold = SEVERITY_ORDER[fail_level]
    confidence_threshold = CONFIDENCE_ORDER[fail_confidence]
    return any(
        SEVERITY_ORDER[finding.severity] >= threshold
        and CONFIDENCE_ORDER[finding.confidence] <= confidence_threshold
        for _, finding in findings
    )


def suppress_package_findings(
    result: object,
    suppress_codes: set[str],
) -> None:
    if not suppress_codes:
        return
    result.findings = [
        (path, finding)
        for path, finding in result.findings
        if finding.code not in suppress_codes
    ]


def finding_span(path: Path, finding: Finding) -> dict[str, int] | None:
    if finding.span is not None:
        return {
            "start_line": finding.span.start_line,
            "start_col": finding.span.start_col,
            "end_line": finding.span.end_line,
            "end_col": finding.span.end_col,
        }

    try:
        lines = read_script_text(path).splitlines()
    except OSError:
        return None
    line_index = finding.line - 1
    if line_index < 0 or line_index >= len(lines):
        return None

    source_line = lines[line_index].rstrip("\r\n")

    def find_unquoted_token(token: str) -> int:
        def token_char(char: str) -> bool:
            return char.isalnum() or char in {"_", "-"}

        def has_token_boundaries(start: int) -> bool:
            before_ok = start == 0 or not token_char(source_line[start - 1])
            end = start + len(token)
            after_ok = end >= len(source_line) or not token_char(source_line[end])
            return before_ok and after_ok

        in_string = False
        index = 0
        while index <= len(source_line) - len(token):
            char = source_line[index]
            if char == '"' and not is_escaped_quote(source_line, index):
                in_string = not in_string
                index += 1
                continue
            if not in_string and source_line.startswith(token, index) and has_token_boundaries(index):
                return index
            index += 1
        return -1

    def span_for_token(token: str) -> dict[str, int] | None:
        if not token:
            return None
        start = find_unquoted_token(token)
        if start < 0:
            start = source_line.find(token)
        if start < 0:
            return None
        return {
            "start_line": finding.line,
            "start_col": start,
            "end_line": finding.line,
            "end_col": start + len(token),
        }

    def span_from_match(match: re.Match[str], group: int = 1) -> dict[str, int]:
        return {
            "start_line": finding.line,
            "start_col": match.start(group),
            "end_line": finding.line,
            "end_col": match.end(group),
        }

    if finding.code == "malformed-load-directive":
        match = re.search(r"^\s*#load\s+(\S+)", source_line)
        if match:
            return span_from_match(match)
        match = re.search(r"\(\s*load\s+([^) \t]+)", source_line)
        if match:
            return span_from_match(match)

    if finding.code == "malformed-include-directive":
        match = re.search(r"\(\s*include\s+([^) \t]+)", source_line)
        if match:
            return span_from_match(match)

    if finding.code == "malformed-load-random-directive":
        match = re.search(r"\b(?:[+-]?\d+|\+[A-Za-z_][A-Za-z0-9_-]*|\+)\s+([A-Za-z_./\\][A-Za-z0-9_./\\-]*)", source_line)
        if match:
            return span_from_match(match)
        match = re.search(r"\(\s*load-random\s+([^) \t]+)", source_line)
        if match:
            return span_from_match(match)

    quoted = re.search(r"'([^']+)'", finding.message)
    if quoted:
        span = span_for_token(quoted.group(1))
        if span is not None:
            return span

    if finding.code == "repeat-chat":
        match = re.search(r"\(\s*(chat-to-all|chat-to-player)\b", source_line)
        if match:
            return {
                "start_line": finding.line,
                "start_col": match.start(1),
                "end_line": finding.line,
                "end_col": match.end(1),
            }

    command_match = re.search(r"\(\s*([#A-Za-z][A-Za-z0-9_-]*)\b", source_line)
    if command_match:
        return {
            "start_line": finding.line,
            "start_col": command_match.start(1),
            "end_line": finding.line,
            "end_col": command_match.end(1),
        }

    return None


def finding_to_json(path: Path, finding: Finding) -> dict[str, object]:
    return {
        "path": str(path),
        "line": finding.line,
        "severity": finding.severity,
        "confidence": finding.confidence,
        "code": finding.code,
        "message": finding.message,
        "suggestion": finding.suggestion,
        "span": finding_span(path, finding),
    }


def finding_groups_to_json(findings: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[str, list[dict[str, object]]] = {}
    for finding in findings:
        grouped.setdefault(str(finding["code"]), []).append(finding)

    groups: list[dict[str, object]] = []
    for code, items in sorted(grouped.items()):
        severity_counts = Counter(str(item["severity"]) for item in items)
        confidence_counts = Counter(str(item["confidence"]) for item in items)
        unique_occurrences = {
            (
                str(item["path"]),
                int(item["line"]),
                str(item["severity"]),
                str(item["confidence"]),
                str(item["message"]),
            )
            for item in items
        }
        examples = sorted(items, key=lambda item: (str(item["path"]), int(item["line"])))[:5]
        groups.append(
            {
                "code": code,
                "count": len(items),
                "unique_occurrence_count": len(unique_occurrences),
                "severity_counts": dict(sorted(severity_counts.items())),
                "confidence_counts": dict(sorted(confidence_counts.items())),
                "explanation": diagnostic_code_explanation(code),
                "documentation_path": DIAGNOSTIC_REGISTRY_MARKDOWN_PATH.as_posix(),
                "documentation_anchor": diagnostic_code_anchor(code),
                "documentation_markdown": diagnostic_code_markdown_link(code),
                "examples": examples,
            }
        )
    return groups


def package_result_to_json(
    root: object,
    result: object,
    fail_level: str,
    fail_confidence: str = "definite",
) -> dict[str, object]:
    severity_counts = Counter(finding.severity for _, finding in result.findings)
    code_counts = Counter(finding.code for _, finding in result.findings)
    confidence_counts = Counter(finding.confidence for _, finding in result.findings)
    linted_files = list(result.files) + [path for path in result.xs_files if path not in result.files]
    file_confidence_counts = Counter(result.file_confidence.get(path.resolve(), "definite") for path in linted_files)
    findings_by_file: dict[Path, list[Finding]] = {}
    for path, finding in result.findings:
        findings_by_file.setdefault(path.resolve(), []).append(finding)
    failing = package_has_failure(result.findings, fail_level, fail_confidence)
    finding_payloads = [
        finding_to_json(path, finding)
        for path, finding in result.findings
    ]
    return {
        "ai_path": str(root.ai_path),
        "per_path": str(root.per_path),
        "package_dir": str(root.package_dir) if root.package_dir is not None else None,
        "files": [str(path) for path in result.files],
        "xs_files": [str(path) for path in result.xs_files],
        "xs_file_count": len(result.xs_files),
        "file_summaries": [
            {
                "path": str(path),
                "confidence": result.file_confidence.get(path.resolve(), "definite"),
                "finding_count": len(findings_by_file.get(path.resolve(), [])),
                "severity_counts": dict(
                    sorted(Counter(finding.severity for finding in findings_by_file.get(path.resolve(), [])).items())
                ),
                "code_counts": dict(
                    sorted(Counter(finding.code for finding in findings_by_file.get(path.resolve(), [])).items())
                ),
            }
            for path in linted_files
        ],
        "file_count": len(result.files),
        "load_graph": package_load_graph_to_json(result),
        "constants": [
            {
                "name": constant.name,
                "value": constant.value,
                "resolved_value": constant.resolved_value,
                "path": str(constant.path),
                "line": constant.line,
                "confidence": constant.confidence,
            }
            for constant in result.constants
        ],
        "constant_count": len(result.constants),
        "finding_count": len(result.findings),
        "severity_counts": dict(sorted(severity_counts.items())),
        "code_counts": dict(sorted(code_counts.items())),
        "confidence_counts": dict(sorted(confidence_counts.items())),
        "file_confidence_counts": dict(sorted(file_confidence_counts.items())),
        "fail_level": fail_level,
        "fail_confidence": fail_confidence,
        "failed": failing,
        "missing_loads": [
            {
                "path": str(missing.path),
                "line": missing.line,
                "include": missing.include,
                "confidence": missing.confidence,
                "candidates": [str(candidate) for candidate in missing.candidates],
            }
            for missing in result.missing_loads
        ],
        "missing_includes": [
            {
                "path": str(missing.path),
                "line": missing.line,
                "include": missing.include,
                "confidence": missing.confidence,
                "candidates": [str(candidate) for candidate in missing.candidates],
            }
            for missing in result.missing_includes
        ],
        "findings": finding_payloads,
        "finding_groups": finding_groups_to_json(finding_payloads),
    }


def package_load_graph_to_json(result: object) -> list[dict[str, object]]:
    package_root = result.root.package_dir
    graph: list[dict[str, object]] = []
    for file_path in result.files:
        load_entries = [
            {
                "line": reference.line,
                "include": reference.include,
                "source": reference.source,
                "confidence": reference.confidence,
                "status": "skipped" if reference.skipped_reason is not None else "resolved" if reference.target is not None else "unresolved",
                "skipped_reason": reference.skipped_reason,
                "resolved_path": str(reference.target) if reference.target is not None else None,
            }
            for reference in find_load_references(file_path, package_root=package_root)
        ]
        include_entries = [
            {
                "line": line,
                "include": include,
                "confidence": confidence,
                "status": "resolved" if target is not None else "unresolved",
                "resolved_path": str(target) if target is not None else None,
            }
            for line, include, target, confidence, _candidates in find_include_targets(
                file_path,
                package_root=package_root,
            )
        ]
        graph.append(
            {
                "path": str(file_path),
                "confidence": result.file_confidence.get(file_path.resolve(), "definite"),
                "loads": load_entries,
                "includes": include_entries,
            }
        )
    return graph


def package_integrity_to_json(integrity: object) -> dict[str, object]:
    severity_counts = {
        "error": len(integrity.stale_ai_roots),
        "info": len(integrity.unreachable_per_files),
        "warning": (
            len(integrity.duplicate_root_targets)
            + len(integrity.duplicate_ai_names)
            + len(integrity.duplicate_per_names)
            + len(integrity.duplicate_load_targets)
        ),
    }
    severity_counts = {key: value for key, value in sorted(severity_counts.items()) if value}
    code_counts = {
        "duplicate-ai-name": len(integrity.duplicate_ai_names),
        "duplicate-load-target": len(integrity.duplicate_load_targets),
        "duplicate-per-name": len(integrity.duplicate_per_names),
        "duplicate-root-target": len(integrity.duplicate_root_targets),
        "stale-ai-root": len(integrity.stale_ai_roots),
        "unreachable-per-file": len(integrity.unreachable_per_files),
    }
    code_counts = {key: value for key, value in sorted(code_counts.items()) if value}
    return {
        "severity_counts": severity_counts,
        "code_counts": code_counts,
        "root_manifest": package_root_manifest_to_json(integrity),
        "stale_ai_roots": [
            {
                "ai_path": str(stale.ai_path),
                "message": stale.message,
            }
            for stale in integrity.stale_ai_roots
        ],
        "stale_ai_root_count": len(integrity.stale_ai_roots),
        "unreachable_per_files": [str(path) for path in integrity.unreachable_per_files],
        "unreachable_per_file_count": len(integrity.unreachable_per_files),
        "duplicate_root_targets": [
            {
                "per_path": str(per_path),
                "ai_paths": [str(path) for path in ai_paths],
            }
            for per_path, ai_paths in sorted(
                integrity.duplicate_root_targets.items(),
                key=lambda item: str(item[0]),
            )
        ],
        "duplicate_root_target_count": len(integrity.duplicate_root_targets),
        "duplicate_ai_names": [
            {
                "name": name,
                "ai_paths": [str(path) for path in ai_paths],
            }
            for name, ai_paths in sorted(integrity.duplicate_ai_names.items())
        ],
        "duplicate_ai_name_count": len(integrity.duplicate_ai_names),
        "duplicate_per_names": [
            {
                "name": name,
                "per_paths": [str(path) for path in per_paths],
            }
            for name, per_paths in sorted(integrity.duplicate_per_names.items())
        ],
        "duplicate_per_name_count": len(integrity.duplicate_per_names),
        "duplicate_load_targets": [
            {
                "ai_path": str(duplicate.ai_path),
                "target_path": str(duplicate.target_path),
                "references": [
                    {
                        "line": reference.line,
                        "include": reference.include,
                        "source": reference.source,
                        "confidence": reference.confidence,
                    }
                    for reference in duplicate.references
                ],
            }
            for duplicate in integrity.duplicate_load_targets
        ],
        "duplicate_load_target_count": len(integrity.duplicate_load_targets),
    }


def package_root_manifest_to_json(integrity: object) -> list[dict[str, object]]:
    roots_by_ai: dict[Path, list[Path]] = {}
    for root in integrity.roots:
        roots_by_ai.setdefault(root.ai_path, []).append(root.per_path)

    ai_paths = sorted({path for path in roots_by_ai} | {stale.ai_path for stale in integrity.stale_ai_roots})
    manifest: list[dict[str, object]] = []
    for ai_path in ai_paths:
        resolved_roots = roots_by_ai.get(ai_path, [])
        root_resolved_paths = {path.resolve() for path in resolved_roots}
        entries: list[dict[str, object]] = []
        for reference in find_load_references(ai_path, package_root=integrity.package_dir):
            target_resolved = reference.target.resolve() if reference.target is not None else None
            status = "skipped" if reference.skipped_reason is not None else "resolved" if target_resolved in root_resolved_paths else "unresolved"
            entries.append(
                {
                    "line": reference.line,
                    "include": reference.include,
                    "source": reference.source,
                    "confidence": reference.confidence,
                    "status": status,
                    "skipped_reason": reference.skipped_reason,
                    "resolved_path": str(reference.target) if reference.target is not None else None,
                    "candidates": [str(candidate) for candidate in reference.candidates],
                }
            )
        if not entries and ai_path.with_suffix(".per").exists():
            entries.append(
                {
                    "line": None,
                    "include": ai_path.with_suffix(".per").name,
                    "confidence": "definite",
                    "status": "resolved",
                    "resolved_path": str(ai_path.with_suffix(".per")),
                    "candidates": [str(ai_path.with_suffix(".per"))],
                    "source": "matching-per",
                }
            )
        manifest.append(
            {
                "ai_path": str(ai_path),
                "status": "resolved" if resolved_roots else "stale",
                "resolved_roots": [str(path) for path in resolved_roots],
                "entries": entries,
            }
        )
    return manifest


def package_integrity_has_failure(integrity: object, fail_level: str) -> bool:
    threshold = SEVERITY_ORDER[fail_level]
    if integrity.stale_ai_roots and SEVERITY_ORDER["error"] >= threshold:
        return True
    if integrity.duplicate_root_targets and SEVERITY_ORDER["warning"] >= threshold:
        return True
    if integrity.duplicate_ai_names and SEVERITY_ORDER["warning"] >= threshold:
        return True
    if integrity.duplicate_per_names and SEVERITY_ORDER["warning"] >= threshold:
        return True
    if integrity.duplicate_load_targets and SEVERITY_ORDER["warning"] >= threshold:
        return True
    if integrity.unreachable_per_files and SEVERITY_ORDER["info"] >= threshold:
        return True
    return False


def package_totals_to_json(root_payloads: list[dict[str, object]], integrity_payload: dict[str, object]) -> dict[str, object]:
    severity_counts: Counter[str] = Counter()
    code_counts: Counter[str] = Counter()
    confidence_counts: Counter[str] = Counter()
    file_confidence_counts: Counter[str] = Counter()
    finding_count = 0
    reachable_file_count = 0
    xs_file_count = 0
    failed_root_count = 0
    definite_error_count = 0
    conditional_error_count = 0
    for root_payload in root_payloads:
        finding_count += int(root_payload["finding_count"])
        reachable_file_count += int(root_payload["file_count"])
        xs_file_count += int(root_payload["xs_file_count"])
        if root_payload["failed"]:
            failed_root_count += 1
        severity_counts.update(root_payload["severity_counts"])
        code_counts.update(root_payload["code_counts"])
        confidence_counts.update(root_payload["confidence_counts"])
        file_confidence_counts.update(root_payload["file_confidence_counts"])
        for finding in root_payload["findings"]:
            if finding["severity"] == "error" and finding["confidence"] == "definite":
                definite_error_count += 1
            elif finding["severity"] == "error" and finding["confidence"] == "conditional":
                conditional_error_count += 1

    return {
        "finding_count": finding_count,
        "severity_counts": dict(sorted(severity_counts.items())),
        "code_counts": dict(sorted(code_counts.items())),
        "confidence_counts": dict(sorted(confidence_counts.items())),
        "file_confidence_counts": dict(sorted(file_confidence_counts.items())),
        "reachable_file_count": reachable_file_count,
        "xs_file_count": xs_file_count,
        "failed_root_count": failed_root_count,
        "definite_error_count": definite_error_count,
        "conditional_error_count": conditional_error_count,
        "stale_ai_root_count": integrity_payload["stale_ai_root_count"],
        "unreachable_per_file_count": integrity_payload["unreachable_per_file_count"],
        "duplicate_root_target_count": integrity_payload["duplicate_root_target_count"],
        "duplicate_ai_name_count": integrity_payload["duplicate_ai_name_count"],
        "duplicate_per_name_count": integrity_payload["duplicate_per_name_count"],
        "duplicate_load_target_count": integrity_payload["duplicate_load_target_count"],
        "integrity_severity_counts": integrity_payload["severity_counts"],
        "integrity_code_counts": integrity_payload["code_counts"],
    }


def package_finding_groups_to_json(root_payloads: list[dict[str, object]]) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    for root_payload in root_payloads:
        findings.extend(root_payload["findings"])
    return finding_groups_to_json(findings)


def package_integrity_groups_to_json(integrity_payload: dict[str, object]) -> list[dict[str, object]]:
    groups: list[dict[str, object]] = []
    specs = [
        ("stale-ai-root", "error", integrity_payload["stale_ai_roots"]),
        ("duplicate-root-target", "warning", integrity_payload["duplicate_root_targets"]),
        ("duplicate-ai-name", "warning", integrity_payload["duplicate_ai_names"]),
        ("duplicate-per-name", "warning", integrity_payload["duplicate_per_names"]),
        ("duplicate-load-target", "warning", integrity_payload["duplicate_load_targets"]),
        ("unreachable-per-file", "info", integrity_payload["unreachable_per_files"]),
    ]
    for code, severity, items in specs:
        if not items:
            continue
        examples: list[dict[str, object]] = []
        if code == "stale-ai-root":
            examples = [
                {
                    "path": item["ai_path"],
                    "severity": severity,
                    "confidence": "definite",
                    "code": code,
                    "message": item["message"],
                }
                for item in items[:5]
            ]
        elif code == "duplicate-root-target":
            examples = [
                {
                    "path": item["per_path"],
                    "severity": severity,
                    "confidence": "definite",
                    "code": code,
                    "message": "loaded as a root by multiple .ai files",
                    "ai_paths": item["ai_paths"],
                }
                for item in items[:5]
            ]
        elif code == "duplicate-ai-name":
            examples = [
                {
                    "path": item["ai_paths"][0],
                    "severity": severity,
                    "confidence": "definite",
                    "code": code,
                    "message": "multiple .ai files share the same display name",
                    "ai_paths": item["ai_paths"],
                }
                for item in items[:5]
            ]
        elif code == "duplicate-per-name":
            examples = [
                {
                    "path": item["per_paths"][0],
                    "severity": severity,
                    "confidence": "definite",
                    "code": code,
                    "message": "multiple .per files share the same case-insensitive basename",
                    "per_paths": item["per_paths"],
                }
                for item in items[:5]
            ]
        elif code == "duplicate-load-target":
            examples = [
                {
                    "path": item["ai_path"],
                    "line": item["references"][1]["line"] if len(item["references"]) > 1 else item["references"][0]["line"],
                    "severity": severity,
                    "confidence": "definite",
                    "code": code,
                    "message": "same .per target is loaded more than once by one .ai file",
                    "target_path": item["target_path"],
                    "references": item["references"],
                }
                for item in items[:5]
            ]
        elif code == "unreachable-per-file":
            examples = [
                {
                    "path": path,
                    "severity": severity,
                    "confidence": "definite",
                    "code": code,
                    "message": "not reachable from any resolved .ai root",
                }
                for path in items[:5]
            ]
        groups.append(
            {
                "code": code,
                "source": "integrity",
                "count": len(items),
                "severity_counts": {severity: len(items)},
                "confidence_counts": {"definite": len(items)},
                "explanation": diagnostic_code_explanation(code),
                "documentation_path": DIAGNOSTIC_REGISTRY_MARKDOWN_PATH.as_posix(),
                "documentation_anchor": diagnostic_code_anchor(code),
                "documentation_markdown": diagnostic_code_markdown_link(code),
                "examples": examples,
            }
        )
    return groups


def package_issue_groups_to_json(root_payloads: list[dict[str, object]], integrity_payload: dict[str, object]) -> list[dict[str, object]]:
    lint_groups = [
        {"source": "lint", **group}
        for group in package_finding_groups_to_json(root_payloads)
    ]
    integrity_groups = package_integrity_groups_to_json(integrity_payload)
    severity_rank = {"error": 0, "warning": 1, "info": 2}

    def group_sort_key(group: dict[str, object]) -> tuple[int, str]:
        severities = group.get("severity_counts", {})
        if isinstance(severities, dict) and severities:
            rank = min(severity_rank.get(str(severity), 99) for severity in severities)
        else:
            rank = 99
        return (rank, str(group["code"]))

    return sorted([*lint_groups, *integrity_groups], key=group_sort_key)


_DIAGNOSTIC_CODE_EXPLANATIONS: dict[str, str] | None = None


def diagnostic_code_explanations() -> dict[str, str]:
    global _DIAGNOSTIC_CODE_EXPLANATIONS
    if _DIAGNOSTIC_CODE_EXPLANATIONS is not None:
        return _DIAGNOSTIC_CODE_EXPLANATIONS
    if not DIAGNOSTIC_REGISTRY_PATH.exists():
        _DIAGNOSTIC_CODE_EXPLANATIONS = {}
        return _DIAGNOSTIC_CODE_EXPLANATIONS
    registry = json.loads(DIAGNOSTIC_REGISTRY_PATH.read_text(encoding="utf-8"))
    _DIAGNOSTIC_CODE_EXPLANATIONS = {
        str(entry["code"]): str(entry["meaning"])
        for entry in registry.get("codes", [])
        if "code" in entry and "meaning" in entry
    }
    return _DIAGNOSTIC_CODE_EXPLANATIONS


def diagnostic_code_explanation(code: str) -> str:
    return diagnostic_code_explanations().get(code, DEFAULT_CATEGORY_EXPLANATION)


def diagnostic_code_anchor(code: str) -> str:
    return f"diagnostic-{re.sub(r'[^a-z0-9_-]+', '-', code.lower())}"


def diagnostic_code_markdown_link(code: str) -> str:
    anchor = diagnostic_code_anchor(code)
    return f"[validator-diagnostic-codes.md#{anchor}]({DIAGNOSTIC_REGISTRY_MARKDOWN_PATH.as_posix()}#{anchor})"


def diagnostic_registry_entries() -> list[dict[str, object]]:
    if not DIAGNOSTIC_REGISTRY_PATH.exists():
        return []
    registry = json.loads(DIAGNOSTIC_REGISTRY_PATH.read_text(encoding="utf-8"))
    return [
        dict(entry)
        for entry in registry.get("codes", [])
        if isinstance(entry, dict) and "code" in entry
    ]


def matching_diagnostic_entries(code: str | None = None) -> list[dict[str, object]]:
    entries = diagnostic_registry_entries()
    if code is None:
        return sorted(entries, key=lambda entry: str(entry["code"]))
    return [
        entry
        for entry in entries
        if entry.get("code") == code
    ]


def diagnostic_entry_to_json(entry: dict[str, object]) -> dict[str, object]:
    code = str(entry["code"])
    return {
        **entry,
        "documentation_path": DIAGNOSTIC_REGISTRY_MARKDOWN_PATH.as_posix(),
        "documentation_anchor": diagnostic_code_anchor(code),
        "documentation_markdown": diagnostic_code_markdown_link(code),
    }


def format_diagnostic_entry(entry: dict[str, object]) -> str:
    return "\n".join(
        [
            str(entry["code"]),
            f"  source: {entry.get('source', '')}",
            f"  severity: {entry.get('severity', '')}",
            f"  corpus: {entry.get('corpus', '')}",
            f"  cursor action: {entry.get('cursor_action', '')}",
            f"  meaning: {entry.get('meaning', '')}",
        ]
    )


def package_report_to_markdown(payload: dict[str, object]) -> str:
    totals = payload["totals"]
    integrity = payload["integrity"]
    lines = [
        "# AI Package Validation Report",
        "",
        "## Summary",
        "",
        f"- Path: `{payload['path']}`",
        f"- Profile: `{payload['profile']}`",
        f"- Failed: `{payload['failed']}`",
        f"- Roots: `{payload['root_count']}`",
        f"- Reachable `.per` files: `{totals['reachable_file_count']}`",
        f"- Included `.xs` files: `{totals['xs_file_count']}`",
        f"- Findings: `{totals['finding_count']}`",
        f"- Severity counts: `{totals['severity_counts']}`",
        f"- Confidence counts: `{totals['confidence_counts']}`",
        f"- Definite errors: `{totals['definite_error_count']}`",
        f"- Conditional errors: `{totals['conditional_error_count']}`",
        f"- Integrity counts: `{totals['integrity_code_counts']}`",
        "",
        "## Issue Categories",
        "",
    ]

    findings_by_code: dict[str, list[dict[str, object]]] = {}
    for root_payload in payload["roots"]:
        for finding in root_payload["findings"]:
            findings_by_code.setdefault(finding["code"], []).append(finding)

    integrity_categories = {
        "stale-ai-root": integrity["stale_ai_roots"],
        "unreachable-per-file": integrity["unreachable_per_files"],
        "duplicate-root-target": integrity["duplicate_root_targets"],
        "duplicate-ai-name": integrity["duplicate_ai_names"],
        "duplicate-per-name": integrity["duplicate_per_names"],
        "duplicate-load-target": integrity["duplicate_load_targets"],
    }

    all_codes = sorted(set(findings_by_code) | {code for code, items in integrity_categories.items() if items})
    if not all_codes:
        lines.append("No lint or package-integrity issues were reported.")
    else:
        for code in all_codes:
            findings = findings_by_code.get(code, [])
            integrity_items = integrity_categories.get(code, [])
            count = len(findings) if findings else len(integrity_items)
            unique_count = count
            if findings:
                unique_count = len(
                    {
                        (
                            finding["path"],
                            finding["line"],
                            finding["severity"],
                            finding["confidence"],
                            finding["message"],
                        )
                        for finding in findings
                    }
                )
            lines.extend(
                [
                    f"### `{code}`",
                    "",
                    f"- Count: `{count}`",
                    f"- Unique occurrences: `{unique_count}`",
                    f"- Explanation: {diagnostic_code_explanation(code)}",
                    f"- Documentation: {diagnostic_code_markdown_link(code)}",
                ]
            )
            suggestions = sorted({finding.get("suggestion") for finding in findings if finding.get("suggestion")})
            if suggestions:
                lines.append(f"- Suggestion: {suggestions[0]}")
            lines.extend(["", "Occurrences:", ""])

            if findings:
                occurrence_counts = Counter(
                    (
                        finding["path"],
                        finding["line"],
                        finding["severity"],
                        finding["confidence"],
                        finding["message"],
                    )
                    for finding in findings
                )
                for (path, line, severity, confidence, message), occurrence_count in sorted(occurrence_counts.items()):
                    repeat = f" x{occurrence_count}" if occurrence_count > 1 else ""
                    lines.append(f"- `{path}:{line}` `{severity}` `{confidence}`{repeat}: {message}")
            elif code == "stale-ai-root":
                for item in integrity_items:
                    lines.append(f"- `{item['ai_path']}`: {item['message']}")
            elif code == "unreachable-per-file":
                for path in integrity_items:
                    lines.append(f"- `{path}`")
            elif code == "duplicate-root-target":
                for item in integrity_items:
                    lines.append(f"- `{item['per_path']}` referenced by `{', '.join(item['ai_paths'])}`")
            elif code == "duplicate-ai-name":
                for item in integrity_items:
                    lines.append(f"- `{item['name']}` used by `{', '.join(item['ai_paths'])}`")
            elif code == "duplicate-per-name":
                for item in integrity_items:
                    lines.append(f"- `{item['name']}` used by `{', '.join(item['per_paths'])}`")
            elif code == "duplicate-load-target":
                for item in integrity_items:
                    lines.append(f"- `{item['ai_path']}` loads `{item['target_path']}` more than once")
            lines.append("")

    lines.extend(["## Root Manifest", ""])

    for entry in integrity["root_manifest"]:
        lines.append(f"- `{entry['ai_path']}`: `{entry['status']}`")
        for resolved_root in entry["resolved_roots"]:
            lines.append(f"  - root: `{resolved_root}`")
        for load_entry in entry["entries"]:
            source = load_entry.get("source")
            status = load_entry.get("status")
            include = load_entry.get("include")
            line = load_entry.get("line")
            suffix = f", reason: `{load_entry['skipped_reason']}`" if load_entry.get("skipped_reason") else ""
            lines.append(f"  - {source} line {line}: `{include}` -> `{status}`{suffix}")

    lines.extend(["", "## Load And Include Graph", ""])

    for root_payload in payload["roots"]:
        lines.append(f"### `{root_payload['per_path']}`")
        lines.append("")
        for graph_entry in root_payload["load_graph"]:
            lines.append(f"- `{graph_entry['path']}` `{graph_entry['confidence']}`")
            for load_entry in graph_entry["loads"]:
                suffix = f", reason: `{load_entry['skipped_reason']}`" if load_entry.get("skipped_reason") else ""
                lines.append(
                    f"  - {load_entry['source']} line {load_entry['line']}: `{load_entry['include']}` -> `{load_entry['status']}`{suffix}"
                )
            for include_entry in graph_entry["includes"]:
                lines.append(
                    f"  - include line {include_entry['line']}: `{include_entry['include']}` -> `{include_entry['status']}`"
                )
        lines.append("")

    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "lint":
        allow_raw_loads = bool(list(args.path.parent.glob("*.ai")))
        findings = lint_file(
            args.path,
            allow_raw_loads=allow_raw_loads,
            profile=args.profile,
            suppress_codes=set(args.suppress_code),
        )
        if args.json:
            print(
                json.dumps(
                    {
                        "path": str(args.path),
                        "finding_count": len(findings),
                        "findings": [
                            finding_to_json(args.path, finding)
                            for finding in findings
                        ],
                        "failed": has_failure(findings, "info"),
                    },
                    indent=2,
                )
            )
            return 1 if has_failure(findings, "info") else 0
        for finding in findings:
            print(finding.format(args.path))
        return 1 if has_failure(findings, "info") else 0

    if args.command == "lint-package":
        integrity = inspect_package_integrity(args.path)
        roots = integrity.roots
        if not roots:
            print(f"no AI package roots found in {args.path}", file=sys.stderr)
            return 2
        exit_code = 1 if package_integrity_has_failure(integrity, args.fail_level) else 0
        json_roots: list[dict[str, object]] = []
        suppress_codes = set(args.suppress_code)
        for root in roots:
            result = lint_package_root(root, profile=args.profile)
            suppress_package_findings(result, suppress_codes)
            root_failed = package_has_failure(result.findings, args.fail_level, args.fail_confidence)
            if args.json or args.output or args.report:
                json_roots.append(
                    package_result_to_json(
                        root,
                        result,
                        args.fail_level,
                        args.fail_confidence,
                    )
                )
                if root_failed:
                    exit_code = 1
                continue
            print(f"{root.ai_path} -> {root.per_path}")
            print(f"  files: {len(result.files)}")
            print(f"  findings: {len(result.findings)}")
            if args.summary:
                for line in format_finding_summary(result.findings):
                    print(line)
            else:
                findings_to_show = result.findings
                if args.max_findings > 0:
                    findings_to_show = result.findings[: args.max_findings]
                for file_path, finding in findings_to_show:
                    print(f"  {finding.format(file_path)}")
                omitted = len(result.findings) - len(findings_to_show)
                if omitted > 0:
                    print(f"  ... {omitted} more findings omitted; rerun with --max-findings 0 to show all")
            if root_failed:
                exit_code = 1
        if args.json or args.output or args.report:
            integrity_payload = package_integrity_to_json(integrity)
            payload = {
                "path": str(args.path),
                "profile": args.profile,
                "fail_level": args.fail_level,
                "fail_confidence": args.fail_confidence,
                "suppressed_codes": sorted(suppress_codes),
                "root_count": len(json_roots),
                "failed": exit_code != 0,
                "integrity": integrity_payload,
                "totals": package_totals_to_json(json_roots, integrity_payload),
                "finding_groups": package_finding_groups_to_json(json_roots),
                "issue_groups": package_issue_groups_to_json(json_roots, integrity_payload),
                "roots": json_roots,
            }
            json_text = json.dumps(payload, indent=2, sort_keys=True)
            report_written = False
            if args.report:
                args.report.parent.mkdir(parents=True, exist_ok=True)
                args.report.write_text(package_report_to_markdown(payload), encoding="utf-8")
                report_written = True
            if args.output:
                args.output.parent.mkdir(parents=True, exist_ok=True)
                args.output.write_text(json_text + "\n", encoding="utf-8")
                if not args.json:
                    print(args.output)
                    if report_written:
                        print(args.report)
            else:
                if args.json:
                    print(json_text)
                elif report_written:
                    print(args.report)
        else:
            if integrity.stale_ai_roots:
                print("package integrity:")
                print(f"  stale AI roots: {len(integrity.stale_ai_roots)}")
                for stale in integrity.stale_ai_roots[:10]:
                    print(f"  {stale.ai_path}: error: stale-ai-root: {stale.message}")
                omitted = len(integrity.stale_ai_roots) - 10
                if omitted > 0:
                    print(f"  ... {omitted} more stale AI roots omitted")
            if integrity.unreachable_per_files:
                print("package integrity:")
                print(f"  unreachable .per files: {len(integrity.unreachable_per_files)}")
                for path in integrity.unreachable_per_files[:10]:
                    print(f"  {path}: info: unreachable-per-file: not reachable from any resolved .ai root")
                omitted = len(integrity.unreachable_per_files) - 10
                if omitted > 0:
                    print(f"  ... {omitted} more unreachable .per files omitted")
            if integrity.duplicate_root_targets:
                print("package integrity:")
                print(f"  duplicate root targets: {len(integrity.duplicate_root_targets)}")
                for per_path, ai_paths in list(integrity.duplicate_root_targets.items())[:10]:
                    joined = ", ".join(str(path) for path in ai_paths)
                    print(f"  {per_path}: warning: duplicate-root-target: referenced by {joined}")
            if integrity.duplicate_ai_names:
                print("package integrity:")
                print(f"  duplicate AI names: {len(integrity.duplicate_ai_names)}")
                for name, ai_paths in list(integrity.duplicate_ai_names.items())[:10]:
                    joined = ", ".join(str(path) for path in ai_paths)
                    print(f"  {name}: warning: duplicate-ai-name: referenced by {joined}")
            if integrity.duplicate_per_names:
                print("package integrity:")
                print(f"  duplicate .per names: {len(integrity.duplicate_per_names)}")
                for name, per_paths in list(integrity.duplicate_per_names.items())[:10]:
                    joined = ", ".join(str(path) for path in per_paths)
                    print(f"  {name}: warning: duplicate-per-name: referenced by {joined}")
            if integrity.duplicate_load_targets:
                print("package integrity:")
                print(f"  duplicate load targets: {len(integrity.duplicate_load_targets)}")
                for duplicate in integrity.duplicate_load_targets[:10]:
                    print(
                        f"  {duplicate.ai_path}: warning: duplicate-load-target: "
                        f"loads {duplicate.target_path} more than once"
                    )
        return exit_code

    if args.command == "suppress-finding":
        try:
            suppress_finding_in_file(args.path, args.line, args.code, next_line=args.next_line)
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        print(f"inserted suppression for {args.code} in {args.path}:{args.line}")
        return 0

    if args.command == "diagnostics":
        entries = matching_diagnostic_entries(args.code)
        if args.json:
            diagnostics = [diagnostic_entry_to_json(entry) for entry in entries]
            print(
                json.dumps(
                    {
                        "code": args.code,
                        "count": len(diagnostics),
                        "diagnostics": diagnostics,
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
        else:
            if args.code and not entries:
                print(f"unknown diagnostic code: {args.code}", file=sys.stderr)
                return 2
            for index, entry in enumerate(entries):
                if index:
                    print()
                print(format_diagnostic_entry(entry))
        if args.code and not entries:
            return 2
        return 0

    if args.command == "stats":
        script = parse_script(args.path)
        print(f"rules: {len(script.rules)}")
        print(f"constants: {len(script.constants)}")
        return 0

    if args.command == "format":
        try:
            options = FormatOptions(
                max_line_length=args.max_line_length,
                format_chat=args.format_chat,
            )
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        if args.stdin:
            print(format_text(sys.stdin.read(), args.path.suffix, options), end="")
            return 0
        files = discover_script_files(args.path)
        if not files:
            print(f"no .ai or .per files found at {args.path}", file=sys.stderr)
            return 2
        if args.stdout and len(files) != 1:
            print("--stdout requires a single .ai or .per file", file=sys.stderr)
            return 2
        results = [format_file(path, options) for path in files]
        if args.stdout:
            print(results[0].formatted_text, end="")
            return 0
        changed = [result for result in results if result.changed]
        if args.write:
            for result in changed:
                result.path.write_text(result.formatted_text, encoding="utf-8")
        for result in changed:
            action = "formatted" if args.write else "would format"
            print(f"{action}: {result.path}")
        if args.check and changed:
            return 1
        return 0

    if args.command == "redundancy":
        report = scan_redundancy(args.paths, limit=args.limit)
        print(format_report(report, max_refs=args.max_refs))
        return 0

    if args.command == "generate":
        if args.template == "sn-defaults":
            block = generate_sn_defaults(args.id)
        elif args.template == "goal-batch":
            assignments = [parse_assignment(value) for value in args.assignments]
            block = generate_goal_batch(
                args.id,
                args.fact,
                assignments,
                disable_self=not args.keep_enabled,
            )
        elif args.template == "state-transition":
            block = generate_state_transition(
                args.id,
                args.goal,
                args.from_value,
                args.to_value,
                args.fact,
                disable_self=not args.keep_enabled,
            )
        else:
            return 2

        if args.insert:
            insert_block_into_file(args.insert, args.section, block)
        else:
            print(block.with_markers())
        return 0

    if args.command == "install-ai":
        package_dir = args.package_dir
        ai_files = sorted(package_dir.glob("*.ai"))
        per_files = sorted(package_dir.rglob("*.per"))
        xs_files = sorted(package_dir.glob("*.xs"))
        if len(ai_files) != 1 or not per_files:
            print(f"expected exactly one .ai and at least one .per in {package_dir}", file=sys.stderr)
            return 2

        defined_constants: set[str] = set()
        defined_constant_tokens: dict[str, str] = {}
        for per_file in per_files:
            script = parse_script(per_file)
            defined_constants.update(script.constant_names)
            if script.constant_tokens:
                defined_constant_tokens.update(script.constant_tokens)
        defined_constant_values = resolve_constant_tokens(defined_constant_tokens)

        finding_pairs = [
            (per_file, finding)
            for per_file in per_files
            for finding in lint_file(
                per_file,
                extra_constants=defined_constants,
                extra_constant_values=defined_constant_values,
                allow_raw_loads=per_file.parent == package_dir,
            )
        ]
        finding_pairs.extend(
            (xs_file, finding)
            for xs_file in xs_files
            for finding in lint_file(xs_file)
        )
        if finding_pairs:
            for per_file, finding in finding_pairs:
                print(finding.format(per_file), file=sys.stderr)
            return 1

        root_per_files = sorted(package_dir.glob("*.per"))
        if len(root_per_files) != 1:
            print(f"expected exactly one root .per in {package_dir}", file=sys.stderr)
            return 2

        assembled_per = assemble_per(root_per_files[0])

        for profile in find_de_profile_dirs(args.profiles_root):
            target = profile / "resources" / "_common" / "ai"
            target.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ai_files[0], target / ai_files[0].name)
            (target / root_per_files[0].name).write_text(assembled_per, encoding="utf-8")
            xs_target = profile / "resources" / "_common" / "xs"
            xs_target.mkdir(parents=True, exist_ok=True)
            for xs_file in xs_files:
                shutil.copy2(xs_file, xs_target / xs_file.name)
            print(target)
        return 0

    if args.command == "install-rms":
        try:
            targets = install_rms_files(args.rms_dir, args.profiles_root)
        except ValueError as error:
            print(str(error), file=sys.stderr)
            return 2
        for target in targets:
            print(target)
        return 0

    if args.command == "clean-logs":
        candidates = find_log_cleanup_candidates(args.logs_root, args.keep_latest)
        total_size = sum(candidate.size for candidate in candidates)
        mode = "delete" if args.delete else "dry-run"
        print(f"{mode}: {len(candidates)} candidates, {total_size} bytes")
        shown_candidates = candidates[: args.max_output]
        for candidate in shown_candidates:
            print(f"{candidate.size}\t{candidate.path}")
            if args.delete:
                remove_log_candidate(candidate)
        for candidate in candidates[args.max_output :]:
            if args.delete:
                remove_log_candidate(candidate)
        remaining = len(candidates) - len(shown_candidates)
        if remaining > 0:
            print(f"... {remaining} more candidates omitted; rerun with --max-output to show more")
        return 0

    if args.command == "scan-strings":
        queries = list(args.query)
        if args.query_file:
            queries.extend(
                line.strip()
                for line in args.query_file.read_text(encoding="utf-8").splitlines()
                if line.strip() and not line.strip().startswith("#")
            )
        if not queries:
            print("provide at least one --query or --query-file", file=sys.stderr)
            return 2

        results = scan_strings(
            args.path,
            queries,
            min_length=args.min_length,
            ignore_case=not args.case_sensitive,
        )
        for result in results:
            status = "FOUND" if result.matches else "MISSING"
            print(f"{status}\t{result.query}\t{len(result.matches)}")
            for match in result.matches[: args.max_matches]:
                print(f"  {match}")
            remaining = len(result.matches) - args.max_matches
            if remaining > 0:
                print(f"  ... {remaining} more")
        return 0

    if args.command == "filter-strings":
        filtered = write_filtered_strings(
            args.dump_path,
            args.output_dir,
            rejected_limit=args.rejected_limit,
        )
        print(f"sections: {len(filtered.sections)}")
        print(f"identifiers: {len(filtered.identifiers)}")
        print(f"messages: {len(filtered.messages)}")
        print(f"ai_messages: {len(filtered.ai_messages)}")
        print(f"rejected_sample: {len(filtered.rejected_sample)}")
        print(args.output_dir)
        return 0

    if args.command == "extract-userpatch-sections":
        sections = write_userpatch_sections(args.dump_path, args.output_dir)
        print(f"sections: {len(sections)}")
        for heading, lines in sorted(sections.items()):
            print(f"{len(lines) - 1}\t{heading}")
        print(args.output_dir)
        return 0

    if args.command == "search-registry":
        data = load_registry(args.path)
        kinds = set(args.kind) if args.kind else None
        matches = search_registry(data, args.query, kinds=kinds, limit=args.limit)
        print(f"query: {args.query}")
        print(f"matches: {len(matches)}")
        for entry in matches:
            print(f"{entry.kind}\t{entry.entry_id}\t{entry.name}")
            print(f"  status: {entry.validation_status}")
            if entry.aliases:
                print(f"  aliases: {', '.join(entry.aliases[:5])}")
            if entry.tags:
                print(f"  tags: {', '.join(entry.tags[:6])}")
            if entry.summary:
                print(f"  {entry.summary}")
            for url in entry.source_urls[:2]:
                print(f"  source: {url}")
        return 0

    if args.command == "resolve-reference":
        data = load_registry(args.path)
        kinds = set(args.kind) if args.kind else None
        resolved = resolve_reference(data, args.query, kinds=kinds, limit=args.related_limit)
        print(f"query: {args.query}")
        if resolved.primary is None:
            print("resolved: 0")
            return 1
        primary = resolved.primary
        print("resolved: 1")
        print(f"primary: {primary.kind}\t{primary.entry_id}\t{primary.name}")
        print(f"  status: {primary.validation_status}")
        if primary.aliases:
            print(f"  aliases: {', '.join(primary.aliases[:5])}")
        if primary.tags:
            print(f"  tags: {', '.join(primary.tags[:8])}")
        if primary.summary:
            print(f"  summary: {primary.summary}")
        details = resolved.details
        for key in [
            "syntax",
            "command_type",
            "complexity",
            "signature",
            "prototype",
            "range",
            "version",
            "es_param_name",
            "sn_id",
            "default_value",
            "required_range",
            "allowable_range",
            "category",
            "parameter_name",
            "family_type",
            "id",
            "de_id",
            "value",
            "value_type",
            "parameter",
            "players",
            "object_id",
            "ai_name",
            "line",
            "object_class",
            "cmd_id",
            "building",
            "group_name",
            "age",
            "dataset",
            "tech_id",
            "civilization",
            "cost",
            "time",
            "level",
            "title",
            "map_type",
            "recommended_probe",
            "notes",
            "offset",
            "ai_context_status",
        ]:
            value = details.get(key)
            if value not in (None, "", []):
                print(f"  {key}: {value}")
        for key in [
            "categories",
            "parameters",
            "related_commands",
            "related_strategic_numbers",
            "related_parameters",
            "used_in_commands",
            "linked_sns",
            "related_sns",
            "aliases",
            "path",
            "create_objects",
            "sections",
            "use_cases",
            "contexts",
            "examples",
            "secondary_sources",
        ]:
            values = details.get(key) or []
            if values:
                print(f"  {key}: {', '.join(str(value) for value in values[:10])}")
        for url in primary.source_urls[:2]:
            print(f"  source: {url}")
        print(f"related: {len(resolved.related)}")
        for entry in resolved.related:
            print(f"  {entry.kind}\t{entry.entry_id}\t{entry.name}")
        return 0

    if args.command == "scrape-airef-commands":
        payload = scrape_airef_commands(
            output_path=args.output,
            cache_dir=args.cache_dir,
            delay_seconds=args.delay,
            limit=args.limit,
            source_dir=args.source_dir,
        )
        print(f"commands: {payload['metadata']['command_count']}")
        print(f"failures: {payload['metadata']['failure_count']}")
        print(args.output)
        return 0

    if args.command == "scrape-airef-parameters":
        payload = scrape_airef_parameters(
            output_path=args.output,
            source_dir=args.source_dir,
        )
        print(f"parameters: {payload['metadata']['parameter_count']}")
        print(args.output)
        return 0

    if args.command == "scrape-airef-strategic-numbers":
        payload = scrape_airef_strategic_numbers(
            output_path=args.output,
            source_dir=args.source_dir,
        )
        print(f"strategic_numbers: {payload['metadata']['strategic_number_count']}")
        print(args.output)
        return 0

    if args.command == "scrape-airef-value-families":
        payload = scrape_airef_value_families(
            output_path=args.output,
            source_dir=args.source_dir,
        )
        print(f"families: {payload['metadata']['family_count']}")
        print(args.output)
        return 0

    if args.command == "scrape-airef-objects":
        payload = scrape_airef_objects(
            output_path=args.output,
            source_dir=args.source_dir,
        )
        print(f"objects: {payload['metadata']['object_count']}")
        print(args.output)
        return 0

    if args.command == "scrape-airef-techs":
        payload = scrape_airef_techs(
            output_path=args.output,
            source_dir=args.source_dir,
        )
        print(f"techs: {payload['metadata']['tech_count']}")
        print(args.output)
        return 0

    if args.command == "scrape-xs-functions":
        payload = scrape_xs_functions(
            output_path=args.output,
            signatures_path=args.signatures_path,
            names_path=args.names_path,
            strings_path=args.strings_path,
        )
        print(f"xs functions: {payload['metadata']['function_count']}")
        print(args.output)
        return 0

    if args.command == "scrape-rms-fixtures":
        payload = scrape_rms_fixtures(
            output_path=args.output,
            rms_dir=args.rms_dir,
        )
        print(f"rms fixtures: {payload['metadata']['fixture_count']}")
        print(args.output)
        return 0

    if args.command == "scrape-rms-topics":
        payload = scrape_rms_topics(
            output_path=args.output,
            guide_path=args.guide_path,
        )
        print(f"rms topics: {payload['metadata']['topic_count']}")
        print(args.output)
        return 0

    if args.command == "scrape-xs-constants":
        payload = scrape_xs_constants(
            output_path=args.output,
            ugc_constants_path=args.ugc_constants_path,
        )
        print(f"xs constants: {payload['metadata']['constant_count']}")
        print(args.output)
        return 0

    return 2


if __name__ == "__main__":
    sys.exit(main())
