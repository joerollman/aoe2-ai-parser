from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re

from .linter import Finding, lint_file
from .parser import (
    Atom,
    Expression,
    active_source_lines,
    count_code_parens,
    iter_defconst_tokens,
    parse_script,
    read_script_text,
    resolve_constant_tokens,
    strip_comment,
)


LOAD_RE = re.compile(r'^\s*\(?\s*load\s+"([^"]+)"\s*\)?\s*(?:;.*)?$')
SOURCE_LOAD_RE = re.compile(r'^\s*#load\s+"([^"]+)"\s*(?:;.*)?$')
INCLUDE_RE = re.compile(r'^\s*\(?\s*include\s+"([^"]+)"\s*\)?\s*(?:;.*)?$')
LOAD_RANDOM_START_RE = re.compile(r"^\s*\(?\s*load-random\b")
LOAD_RANDOM_ENTRY_RE = re.compile(
    r'(?:(?P<weight>[+-]?\d+|\+[A-Za-z_][A-Za-z0-9_-]*|\+)\s+)?"(?P<include>[^"]+)"'
)
MAX_LOAD_NESTING_DEPTH = 10
XS_FUNCTION_RE = re.compile(
    r"^\s*(?:void|bool|int|float|string)\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(([^)]*)\)"
)


@dataclass(frozen=True)
class PackageRoot:
    ai_path: Path
    per_path: Path
    package_dir: Path | None = None


@dataclass(frozen=True)
class MissingLoad:
    path: Path
    line: int
    include: str
    candidates: tuple[Path, ...]
    confidence: str = "definite"


@dataclass(frozen=True)
class MissingInclude:
    path: Path
    line: int
    include: str
    candidates: tuple[Path, ...]
    confidence: str = "definite"


@dataclass(frozen=True)
class LoadReference:
    line: int
    include: str
    target: Path | None
    confidence: str
    candidates: tuple[Path, ...]
    source: str
    skipped_reason: str | None = None


@dataclass(frozen=True)
class PackageConstantDefinition:
    name: str
    value: str
    path: Path
    line: int
    confidence: str = "definite"
    resolved_value: int | None = None


@dataclass
class PackageLintResult:
    root: PackageRoot
    files: list[Path]
    xs_files: list[Path] = field(default_factory=list)
    file_confidence: dict[Path, str] = field(default_factory=dict)
    findings: list[tuple[Path, Finding]] = field(default_factory=list)
    missing_loads: list[MissingLoad] = field(default_factory=list)
    missing_includes: list[MissingInclude] = field(default_factory=list)
    constants: list[PackageConstantDefinition] = field(default_factory=list)


@dataclass(frozen=True)
class StaleAiRoot:
    ai_path: Path
    message: str


@dataclass(frozen=True)
class DuplicateLoadTarget:
    ai_path: Path
    target_path: Path
    references: tuple[LoadReference, ...]


@dataclass
class PackageIntegrityResult:
    package_dir: Path
    roots: list[PackageRoot]
    stale_ai_roots: list[StaleAiRoot] = field(default_factory=list)
    unreachable_per_files: list[Path] = field(default_factory=list)
    duplicate_root_targets: dict[Path, list[Path]] = field(default_factory=dict)
    duplicate_ai_names: dict[str, list[Path]] = field(default_factory=dict)
    duplicate_per_names: dict[str, list[Path]] = field(default_factory=dict)
    duplicate_load_targets: list[DuplicateLoadTarget] = field(default_factory=list)


def merge_confidence(existing: str, incoming: str) -> str:
    if existing == "conditional" or incoming == "conditional":
        return "conditional"
    return "definite"


def resolve_ai_root(ai_path: str | Path, *, package_dir: str | Path | None = None) -> PackageRoot | None:
    roots = resolve_ai_roots(ai_path, package_dir=package_dir)
    return roots[0] if roots else None


def resolve_ai_roots(ai_path: str | Path, *, package_dir: str | Path | None = None) -> list[PackageRoot]:
    path = Path(ai_path)
    package_root = Path(package_dir) if package_dir is not None else path.parent
    candidates: list[Path] = []

    for _, _, target, _, target_candidates in find_load_targets(path, package_root=package_root):
        if target is not None:
            candidates.append(target)
        else:
            candidates.extend(target_candidates)

    if not candidates and path.with_suffix(".per").exists():
        candidates.append(path.with_suffix(".per"))

    roots: list[PackageRoot] = []
    seen: set[Path] = set()
    for candidate in candidates:
        resolved = candidate.resolve()
        if candidate.exists() and resolved not in seen:
            roots.append(PackageRoot(ai_path=path, per_path=candidate, package_dir=package_root))
            seen.add(resolved)
    return roots


def describe_ai_root_failure(ai_path: str | Path, *, package_dir: str | Path | None = None) -> str:
    path = Path(ai_path)
    package_root = Path(package_dir) if package_dir is not None else path.parent
    candidates: list[Path] = []
    for _, _, target, _, target_candidates in find_load_targets(path, package_root=package_root):
        if target is not None:
            candidates.append(target)
        else:
            candidates.extend(target_candidates)
    if not candidates:
        candidates.append(path.with_suffix(".per"))
    unique_candidates: list[Path] = []
    for candidate in candidates:
        if candidate not in unique_candidates:
            unique_candidates.append(candidate)
    return "no root .per resolved; tried " + ", ".join(str(candidate) for candidate in unique_candidates)


def resolve_load_path(base_dir: Path, include_name: str) -> Path:
    normalized = include_name.replace("/", "\\")
    path = base_dir / normalized
    if path.suffix.lower() != ".per":
        path = path.with_suffix(".per")
    return path


def resolve_load_candidates(
    base_dir: Path,
    include_name: str,
    *,
    package_root: Path | None = None,
) -> list[Path]:
    candidates = [resolve_load_path(base_dir, include_name)]
    if package_root is not None:
        package_candidate = resolve_load_path(package_root, include_name)
        if package_candidate not in candidates:
            candidates.append(package_candidate)
    return candidates


def resolve_load_target(
    base_dir: Path,
    include_name: str,
    *,
    package_root: Path | None = None,
) -> Path | None:
    for candidate in resolve_load_candidates(base_dir, include_name, package_root=package_root):
        if candidate.exists():
            return candidate
    return None


def resolve_include_path(base_dir: Path, include_name: str) -> Path:
    normalized = include_name.replace("/", "\\")
    return base_dir / normalized


def resolve_include_candidates(
    base_dir: Path,
    include_name: str,
    *,
    package_root: Path | None = None,
) -> list[Path]:
    candidates = [resolve_include_path(base_dir, include_name)]
    if package_root is not None:
        package_candidate = resolve_include_path(package_root, include_name)
        if package_candidate not in candidates:
            candidates.append(package_candidate)
    return candidates


def resolve_include_target(
    base_dir: Path,
    include_name: str,
    *,
    package_root: Path | None = None,
) -> Path | None:
    for candidate in resolve_include_candidates(base_dir, include_name, package_root=package_root):
        if candidate.exists():
            return candidate
    return None


def iter_load_random_entries(code: str) -> list[tuple[str, bool, str | None]]:
    entries: list[tuple[str, bool, str | None]] = []
    for entry in LOAD_RANDOM_ENTRY_RE.finditer(code):
        weight = entry.group("weight")
        disabled = False
        if weight is not None:
            try:
                disabled = int(weight) <= 0
            except ValueError:
                disabled = False
        entries.append((entry.group("include"), disabled, weight))
    return entries


def find_load_references(
    path: str | Path,
    *,
    package_root: str | Path | None = None,
) -> list[LoadReference]:
    script_path = Path(path)
    root = Path(package_root) if package_root is not None else None
    references: list[LoadReference] = []
    in_load_random = False
    load_random_balance = 0

    for source_line in active_source_lines(script_path):
        line_number = source_line.number
        code = strip_comment(source_line.text)
        if not code:
            continue

        match = SOURCE_LOAD_RE.match(code) or LOAD_RE.match(code)
        if match:
            include = match.group(1)
            candidates = tuple(resolve_load_candidates(script_path.parent, include, package_root=root))
            target = resolve_load_target(script_path.parent, include, package_root=root)
            references.append(
                LoadReference(
                    line_number,
                    include,
                    target,
                    source_line.confidence,
                    candidates,
                    "#load" if SOURCE_LOAD_RE.match(code) else "load",
                )
            )
            continue

        if LOAD_RANDOM_START_RE.match(code):
            load_random_balance = count_code_parens(code)
            in_load_random = load_random_balance > 0
            for include, disabled, weight in iter_load_random_entries(code):
                candidates = tuple(resolve_load_candidates(script_path.parent, include, package_root=root))
                target = resolve_load_target(script_path.parent, include, package_root=root)
                references.append(
                    LoadReference(
                        line_number,
                        include,
                        None if disabled else target,
                        source_line.confidence,
                        candidates,
                        "load-random",
                        "zero-or-negative-weight" if disabled else None,
                    )
                )
            continue

        if not in_load_random:
            continue

        load_random_balance += count_code_parens(code)
        for include, disabled, weight in iter_load_random_entries(code):
            candidates = tuple(resolve_load_candidates(script_path.parent, include, package_root=root))
            target = resolve_load_target(script_path.parent, include, package_root=root)
            references.append(
                LoadReference(
                    line_number,
                    include,
                    None if disabled else target,
                    source_line.confidence,
                    candidates,
                    "load-random",
                    "zero-or-negative-weight" if disabled else None,
                )
            )
        if load_random_balance <= 0:
            in_load_random = False
            load_random_balance = 0

    return references


def find_load_targets(
    path: str | Path,
    *,
    package_root: str | Path | None = None,
) -> list[tuple[int, str, Path | None, str, tuple[Path, ...]]]:
    return [
        (reference.line, reference.include, reference.target, reference.confidence, reference.candidates)
        for reference in find_load_references(path, package_root=package_root)
        if reference.skipped_reason is None
    ]


def find_include_targets(
    path: str | Path,
    *,
    package_root: str | Path | None = None,
) -> list[tuple[int, str, Path | None, str, tuple[Path, ...]]]:
    script_path = Path(path)
    root = Path(package_root) if package_root is not None else None
    targets: list[tuple[int, str, Path | None, str, tuple[Path, ...]]] = []

    for source_line in active_source_lines(script_path):
        code = strip_comment(source_line.text)
        if not code:
            continue
        match = INCLUDE_RE.match(code)
        if not match:
            continue
        include = match.group(1)
        candidates = tuple(resolve_include_candidates(script_path.parent, include, package_root=root))
        target = resolve_include_target(script_path.parent, include, package_root=root)
        targets.append((source_line.number, include, target, source_line.confidence, candidates))

    return targets


def collect_reachable_per_files(
    root_path: str | Path,
    *,
    package_root: str | Path | None = None,
) -> tuple[list[Path], list[MissingLoad]]:
    root = Path(root_path).resolve()
    package_root_path = Path(package_root).resolve() if package_root is not None else None
    seen: set[Path] = set()
    ordered: list[Path] = []
    missing: list[MissingLoad] = []
    graph_findings: list[tuple[Path, Finding]] = []
    confidence_by_file: dict[Path, str] = {}

    def visit(path: Path, confidence: str = "definite", depth: int = 0, stack: tuple[Path, ...] = ()) -> None:
        resolved = path.resolve()
        confidence_by_file[resolved] = merge_confidence(confidence_by_file.get(resolved, "definite"), confidence)
        if resolved in seen:
            return
        seen.add(resolved)
        ordered.append(resolved)
        stack = (*stack, resolved)
        for line_number, include, target, load_confidence, candidates in find_load_targets(
            resolved,
            package_root=package_root_path,
        ):
            child_confidence = merge_confidence(confidence_by_file[resolved], load_confidence)
            if target is not None:
                target_resolved = target.resolve()
                child_depth = depth + 1
                if target_resolved in stack:
                    cycle = " -> ".join(path.name for path in (*stack, target_resolved))
                    graph_findings.append(
                        (
                            resolved,
                            Finding(
                                line_number,
                                "load-cycle",
                                f"load target {include!r} creates a cycle: {cycle}",
                                child_confidence,
                            ),
                        )
                    )
                    continue
                if child_depth > MAX_LOAD_NESTING_DEPTH:
                    graph_findings.append(
                        (
                            resolved,
                            Finding(
                                line_number,
                                "load-depth-exceeded",
                                f"load target {include!r} exceeds maximum nested load depth {MAX_LOAD_NESTING_DEPTH}",
                                child_confidence,
                            ),
                        )
                    )
                    continue
                visit(target, child_confidence, child_depth, stack)
            else:
                missing.append(
                    MissingLoad(
                        path=resolved,
                        line=line_number,
                        include=include,
                        candidates=candidates,
                        confidence=child_confidence,
                    )
                )

    visit(root)
    collect_reachable_per_files.last_confidence_by_file = confidence_by_file
    collect_reachable_per_files.last_graph_findings = graph_findings
    return ordered, missing


def find_package_roots(package_dir: str | Path) -> list[PackageRoot]:
    root = Path(package_dir)
    if root.is_file() and root.suffix.lower() == ".ai":
        return resolve_ai_roots(root, package_dir=root.parent)
    if root.is_file() and root.suffix.lower() == ".per":
        return [PackageRoot(ai_path=root, per_path=root, package_dir=root.parent)]

    roots: list[PackageRoot] = []
    for ai_path in sorted(root.rglob("*.ai")):
        roots.extend(resolve_ai_roots(ai_path, package_dir=root))
    return roots


def find_duplicate_load_targets(ai_paths: list[Path], *, package_root: Path) -> list[DuplicateLoadTarget]:
    duplicates: list[DuplicateLoadTarget] = []
    for ai_path in sorted(set(ai_paths)):
        by_target: dict[Path, list[LoadReference]] = {}
        for reference in find_load_references(ai_path, package_root=package_root):
            if reference.target is None or reference.skipped_reason is not None:
                continue
            by_target.setdefault(reference.target.resolve(), []).append(reference)
        duplicates.extend(
            DuplicateLoadTarget(ai_path=ai_path, target_path=target, references=tuple(references))
            for target, references in sorted(by_target.items())
            if len(references) > 1
        )
    return duplicates


def inspect_package_integrity(package_dir: str | Path) -> PackageIntegrityResult:
    root = Path(package_dir)
    if root.is_file() and root.suffix.lower() == ".ai":
        package_root = root.parent
        roots = resolve_ai_roots(root, package_dir=package_root)
        stale_ai_roots = (
            []
            if roots
            else [
                StaleAiRoot(
                    ai_path=root,
                    message=describe_ai_root_failure(root, package_dir=package_root),
                )
            ]
        )
        return PackageIntegrityResult(
            package_dir=package_root,
            roots=roots,
            stale_ai_roots=stale_ai_roots,
            unreachable_per_files=[],
            duplicate_root_targets={},
            duplicate_load_targets=find_duplicate_load_targets([root], package_root=package_root),
        )
    if root.is_file() and root.suffix.lower() == ".per":
        package_root = root.parent
        roots = [PackageRoot(ai_path=root, per_path=root, package_dir=package_root)]
        return PackageIntegrityResult(
            package_dir=package_root,
            roots=roots,
            stale_ai_roots=[],
            unreachable_per_files=[],
            duplicate_root_targets={},
        )

    roots: list[PackageRoot] = []
    stale_ai_roots: list[StaleAiRoot] = []
    ai_names: dict[str, list[Path]] = {}
    per_names: dict[str, list[Path]] = {}
    for ai_path in sorted(root.rglob("*.ai")):
        ai_names.setdefault(ai_path.stem.lower(), []).append(ai_path)
        package_roots = resolve_ai_roots(ai_path, package_dir=root)
        if not package_roots:
            stale_ai_roots.append(
                StaleAiRoot(
                    ai_path=ai_path,
                    message=describe_ai_root_failure(ai_path, package_dir=root),
                )
            )
        else:
            roots.extend(package_roots)

    reachable: set[Path] = set()
    for package_root in roots:
        files, _ = collect_reachable_per_files(package_root.per_path, package_root=root)
        reachable.update(path.resolve() for path in files)

    all_per_files = {path.resolve() for path in root.rglob("*.per")}
    for per_path in sorted(all_per_files):
        per_names.setdefault(per_path.stem.lower(), []).append(per_path)
    unreachable = sorted(all_per_files - reachable)

    root_targets: dict[Path, set[Path]] = {}
    for package_root in roots:
        root_targets.setdefault(package_root.per_path.resolve(), set()).add(package_root.ai_path)
    duplicates = {
        per_path: sorted(ai_paths)
        for per_path, ai_paths in root_targets.items()
        if len(ai_paths) > 1
    }
    duplicate_ai_names = {
        name: paths
        for name, paths in sorted(ai_names.items())
        if len(paths) > 1
    }
    duplicate_per_names = {
        name: paths
        for name, paths in sorted(per_names.items())
        if len(paths) > 1
    }
    all_ai_paths = sorted(ai_path for paths in ai_names.values() for ai_path in paths)
    duplicate_load_targets = find_duplicate_load_targets(all_ai_paths, package_root=root)

    return PackageIntegrityResult(
        package_dir=root,
        roots=roots,
        stale_ai_roots=stale_ai_roots,
        unreachable_per_files=unreachable,
        duplicate_root_targets=duplicates,
        duplicate_ai_names=duplicate_ai_names,
        duplicate_per_names=duplicate_per_names,
        duplicate_load_targets=duplicate_load_targets,
    )


def package_defconst_alias_cycle_findings(
    tokens: dict[str, str],
    locations: dict[str, tuple[Path, int, str]],
) -> list[tuple[Path, Finding]]:
    findings: list[tuple[Path, Finding]] = []
    reported: set[tuple[str, ...]] = set()
    for name in tokens:
        path_names: list[str] = []
        current = name
        while current in tokens:
            if current in path_names:
                cycle = path_names[path_names.index(current):]
                key = tuple(sorted(cycle))
                if key not in reported:
                    reported.add(key)
                    cycle_files = {
                        locations[cycle_name][0].resolve()
                        for cycle_name in cycle
                        if cycle_name in locations
                    }
                    if len(cycle_files) > 1:
                        if any(locations[cycle_name][2] != "definite" for cycle_name in cycle if cycle_name in locations):
                            break
                        path, line, confidence = locations[cycle[0]]
                        chain = " -> ".join((*cycle, cycle[0]))
                        findings.append(
                            (
                                path,
                                Finding(
                                    line,
                                    "defconst-alias-cycle",
                                    f"package defconst alias cycle {chain!r} cannot resolve to a numeric value",
                                    confidence,
                                ),
                            )
                        )
                break
            path_names.append(current)
            next_value = tokens[current]
            if re.fullmatch(r"-?\d+", next_value):
                break
            current = next_value
    return findings


def strip_xs_line_comment(line: str) -> str:
    in_string = False
    escaped = False
    for index, char in enumerate(line):
        if escaped:
            escaped = False
            continue
        if char == "\\" and in_string:
            escaped = True
            continue
        if char == '"':
            in_string = not in_string
            continue
        if not in_string and line.startswith("//", index):
            return line[:index]
    return line


def xs_function_parameter_counts(xs_files: list[Path]) -> dict[str, tuple[int, Path, int]]:
    functions: dict[str, tuple[int, Path, int]] = {}
    for xs_file in xs_files:
        for line_number, raw_line in enumerate(read_script_text(xs_file).splitlines(), start=1):
            code = strip_xs_line_comment(raw_line)
            match = XS_FUNCTION_RE.match(code)
            if not match:
                continue
            name = match.group(1)
            params = match.group(2).strip()
            count = 0 if not params else len([param for param in params.split(",") if param.strip()])
            functions.setdefault(name, (count, xs_file, line_number))
    return functions


def quoted_token_value(value: str) -> str | None:
    if len(value) >= 2 and value.startswith('"') and value.endswith('"'):
        return value[1:-1].replace(r"\"", '"')
    return None


def xs_script_call_target(expr: Expression, constant_tokens: dict[str, str]) -> str | None:
    if expr.head != "xs-script-call" or len(expr.args) != 1:
        return None
    arg = expr.args[0]
    if not isinstance(arg, Atom):
        return None
    if target := quoted_token_value(arg.value):
        return target
    if arg.value in constant_tokens:
        return quoted_token_value(constant_tokens[arg.value])
    return None


def iter_xs_script_call_exprs(script_path: Path) -> list[Expression]:
    expressions: list[Expression] = []
    script = parse_script(script_path)

    def walk(expr: Expression) -> None:
        if expr.head == "xs-script-call":
            expressions.append(expr)
        for arg in expr.args:
            if isinstance(arg, Expression):
                walk(arg)

    for rule in script.rules:
        for expr in (*rule.fact_exprs, *rule.action_exprs):
            walk(expr)
    return expressions


def package_xs_script_call_findings(
    files: list[Path],
    xs_files: list[Path],
    constant_tokens: dict[str, str],
) -> list[tuple[Path, Finding]]:
    xs_functions = xs_function_parameter_counts(xs_files)
    if not xs_functions:
        return []

    findings: list[tuple[Path, Finding]] = []
    for file_path in files:
        for expr in iter_xs_script_call_exprs(file_path):
            target = xs_script_call_target(expr, constant_tokens)
            if target is None or target not in xs_functions:
                continue
            parameter_count, xs_file, line_number = xs_functions[target]
            if parameter_count == 0:
                continue
            findings.append(
                (
                    file_path,
                    Finding(
                        expr.line,
                        "xs-script-call-parameterized-function",
                        f"xs-script-call target {target!r} is defined with {parameter_count} parameter(s) in {xs_file.name}:{line_number}; only zero-parameter XS functions can be called",
                        span=expr.head_span,
                    ),
                )
            )
    return findings


def package_duplicate_include_findings(
    file_path: Path,
    includes: list[tuple[int, str, Path | None, str, tuple[Path, ...]]],
    *,
    file_confidence: str,
) -> list[tuple[Path, Finding]]:
    findings: list[tuple[Path, Finding]] = []
    first_by_target: dict[Path, tuple[int, str]] = {}
    for line_number, include, target, confidence, _candidates in includes:
        if target is None:
            continue
        resolved_target = target.resolve()
        if resolved_target not in first_by_target:
            first_by_target[resolved_target] = (line_number, include)
            continue
        first_line, first_include = first_by_target[resolved_target]
        findings.append(
            (
                file_path,
                Finding(
                    line_number,
                    "duplicate-include-target",
                    f"include target {include!r} resolves to the same .xs file as {first_include!r} on line {first_line}",
                    merge_confidence(file_confidence, confidence),
                ),
            )
        )
    return findings


def package_defconst_conflict_findings(
    definitions: dict[str, list[tuple[str, Path, int, str]]],
) -> list[tuple[Path, Finding]]:
    findings: list[tuple[Path, Finding]] = []
    for name, entries in sorted(definitions.items()):
        entries = [entry for entry in entries if entry[3] == "definite"]
        if len(entries) < 2:
            continue
        first_value, first_path, first_line, _first_confidence = entries[0]
        for value, path, line, confidence in entries[1:]:
            if value == first_value:
                continue
            if path.resolve() == first_path.resolve():
                continue
            findings.append(
                (
                    path,
                    Finding(
                        line,
                        "duplicate-defconst-conflict",
                        f"{name!r} is defined as {first_value!r} in {first_path} line {first_line} and {value!r} here",
                        confidence,
                    ),
                )
            )
            break
    return findings


def lint_package_root(root: PackageRoot, *, profile: str = "corpus") -> PackageLintResult:
    files, missing = collect_reachable_per_files(root.per_path, package_root=root.package_dir)
    file_confidence = getattr(collect_reachable_per_files, "last_confidence_by_file", {})
    graph_findings = getattr(collect_reachable_per_files, "last_graph_findings", [])
    xs_files: list[Path] = []
    missing_includes: list[MissingInclude] = []
    constant_names: set[str] = set()
    constant_tokens: dict[str, str] = {}
    constant_locations: dict[str, tuple[Path, int, str]] = {}
    constant_definitions: dict[str, list[tuple[str, Path, int, str]]] = {}
    package_constants: list[PackageConstantDefinition] = []
    for file_path in files:
        script = parse_script(file_path)
        constant_names.update(script.constant_names)
        if script.constant_tokens:
            constant_tokens.update(script.constant_tokens)
        for source_line in active_source_lines(file_path):
            for name, value in iter_defconst_tokens(source_line.text):
                constant_locations[name] = (file_path, source_line.number, source_line.confidence)
                constant_definitions.setdefault(name, []).append(
                    (value, file_path, source_line.number, source_line.confidence)
                )
    constant_values = resolve_constant_tokens(constant_tokens)

    for name, definitions in sorted(constant_definitions.items()):
        for value, file_path, line_number, confidence in definitions:
            package_constants.append(
                PackageConstantDefinition(
                    name=name,
                    value=value,
                    path=file_path,
                    line=line_number,
                    confidence=confidence,
                    resolved_value=constant_values.get(name),
                )
            )

    result = PackageLintResult(
        root=root,
        files=files,
        file_confidence=file_confidence,
        missing_loads=missing,
        constants=package_constants,
    )
    result.findings.extend(graph_findings)
    if profile != "corpus":
        result.findings.extend(package_defconst_conflict_findings(constant_definitions))
    result.findings.extend(package_defconst_alias_cycle_findings(constant_tokens, constant_locations))
    for file_path in files:
        file_level_confidence = file_confidence.get(file_path.resolve(), "definite")
        includes = find_include_targets(
            file_path,
            package_root=root.package_dir,
        )
        result.findings.extend(
            package_duplicate_include_findings(file_path, includes, file_confidence=file_level_confidence)
        )
        for line_number, include, target, include_confidence, candidates in includes:
            child_confidence = merge_confidence(file_level_confidence, include_confidence)
            if target is not None:
                resolved_target = target.resolve()
                if resolved_target not in {path.resolve() for path in xs_files}:
                    xs_files.append(resolved_target)
                    file_confidence[resolved_target] = child_confidence
            else:
                missing_includes.append(
                    MissingInclude(
                        path=file_path,
                        line=line_number,
                        include=include,
                        candidates=candidates,
                        confidence=child_confidence,
                    )
                )
        for finding in lint_file(
            file_path,
            extra_constants=constant_names,
            extra_constant_values=constant_values,
            allow_raw_loads=True,
            profile=profile,
        ):
            if file_level_confidence == "conditional" and finding.confidence == "definite":
                finding = Finding(
                    finding.line,
                    finding.code,
                    finding.message,
                    "conditional",
                    finding.span,
                )
            result.findings.append((file_path, finding))
    result.xs_files = xs_files
    result.missing_includes = missing_includes
    for xs_file in xs_files:
        file_level_confidence = file_confidence.get(xs_file.resolve(), "definite")
        for finding in lint_file(xs_file, profile=profile):
            if file_level_confidence == "conditional" and finding.confidence == "definite":
                finding = Finding(
                    finding.line,
                    finding.code,
                    finding.message,
                    "conditional",
                    finding.span,
                )
            result.findings.append((xs_file, finding))
    result.findings.extend(package_xs_script_call_findings(files, xs_files, constant_tokens))
    for missing_load in missing:
        result.findings.append(
            (
                missing_load.path,
                Finding(
                    missing_load.line,
                    "missing-load-target",
                    f"load target {missing_load.include!r} could not be resolved; tried {', '.join(str(candidate) for candidate in missing_load.candidates)}",
                    missing_load.confidence,
                ),
            )
        )
    for missing_include in missing_includes:
        result.findings.append(
            (
                missing_include.path,
                Finding(
                    missing_include.line,
                    "missing-include-target",
                    f"include target {missing_include.include!r} could not be resolved; tried {', '.join(str(candidate) for candidate in missing_include.candidates)}",
                    missing_include.confidence,
                ),
            )
        )
    return result
