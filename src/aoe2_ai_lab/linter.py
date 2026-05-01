from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re

from .parser import (
    Atom,
    Expression,
    SourceSpan,
    active_source_lines,
    count_code_parens,
    defconst_form_spans,
    first_symbol,
    iter_defconst_tokens,
    is_escaped_quote,
    is_defrule_start,
    parse_defconst_form,
    parse_script,
    preprocessor_issues,
    read_script_text,
    split_rule_arrow,
    strip_comment,
)


SEVERITY_ORDER = {"info": 0, "warning": 1, "error": 2}
CONFIDENCE_ORDER = {"definite": 0, "conditional": 1}
INFO_FINDING_CODES = {
    "builtin-constant-alias",
    "redundant-built-in-defconst",
}
WARNING_FINDING_CODES = {
    "command-argument-mismatch",
    "command-family-mismatch",
    "command-numeric-range-mismatch",
    "command-typed-operand-mismatch",
    "defconst-alias-cycle",
    "duplicate-defconst-conflict",
    "duplicate-include-target",
    "duplicate-per-load-target",
    "livestock-default-point",
    "load-after-include",
    "load-random-plus-weight-de-behavior",
    "repeat-chat",
    "unsafe-set-target-object",
    "unscoped-duc-target",
    "undefined-constant",
    "undefined-identifier",
    "undefined-position-constant",
    "undefined-strategic-number",
    "unsafe-goal-block",
    "up-can-build-zero-escrow",
    "up-build-place-point-coordinate-as-escrow",
    "xs-script-call-parameterized-function",
}
SUPPRESSION_MARKER = "aoe2-ai-parser-disable"


def finding_severity(code: str) -> str:
    if code in INFO_FINDING_CODES:
        return "info"
    if code in WARNING_FINDING_CODES:
        return "warning"
    return "error"


def finding_suggestion(code: str, message: str) -> str | None:
    if code == "command-typed-prefix-mismatch":
        return "Use a plain typeOp such as c:, g:, or s:. For example, replace g:= with g: in typeOp slots."
    if code == "command-typed-operand-mismatch":
        return "Use the typeOp that matches the following operand: g: for goals, s: for strategic numbers, and c: for constants."
    if code == "command-family-mismatch":
        return "Use a symbol family that matches the documented argument slot, such as a goal constant for GoalId or an sn-* constant for SnId."
    if code == "command-numeric-range-mismatch":
        return "Use a literal or defconst value within the documented range, or use a dynamic typed value if the value is computed at runtime."
    if code == "duplicate-defconst-conflict":
        return "Keep only one definite defconst value for the symbol, or guard conflicting values with mutually exclusive preprocessor branches."
    if code == "defconst-alias-cycle":
        return "Break the alias cycle by assigning one constant a numeric value or a non-cyclic documented symbol."
    if code == "defconst-value-out-of-range":
        return "Use a value from -32768 to 32767, or store wider runtime values in goals or strategic numbers instead of defconsts."
    if code == "command-role-mismatch":
        if "likely intended action:" in message:
            return message.split("likely intended action:", 1)[1].strip()
        return "Move the command to the documented context or replace it with the matching fact/action command."
    if code == "missing-load-target":
        return "Add the missing .per file to the package or update the load path to a reachable file."
    if code == "missing-include-target":
        return "Add the missing included file to the package or update the include path to a reachable file."
    if code == "up-can-build-zero-escrow":
        return "Define a goal set to without-escrow and pass that goal instead of literal 0."
    if code == "command-argument-mismatch" and "mathOp" in message:
        return "Use a documented math operator such as c:=, g:=, c:+, c:-, g:+, or g:- as appropriate."
    if code == "logical-operator-arity-mismatch":
        return "Use exactly one child fact for not, and exactly two child facts for binary logical operators; nest operators for larger groups."
    return None


@dataclass(frozen=True)
class Finding:
    line: int
    code: str
    message: str
    confidence: str = "definite"
    span: SourceSpan | None = None

    @property
    def severity(self) -> str:
        return finding_severity(self.code)

    @property
    def suggestion(self) -> str | None:
        return finding_suggestion(self.code, self.message)

    def format(self, path: Path) -> str:
        return f"{path}:{self.line}: {self.severity}: {self.code}: {self.message}"


def _line_comment_text(line: str) -> str:
    in_string = False
    for index, char in enumerate(line):
        if char == '"' and not is_escaped_quote(line, index):
            in_string = not in_string
        elif char == ";" and not in_string:
            return line[index + 1 :]
    return ""


def _suppression_codes(comment: str, directive: str) -> set[str]:
    match = re.search(rf"\b{re.escape(directive)}\b(?P<codes>.*)", comment, flags=re.IGNORECASE)
    if not match:
        return set()
    codes = {
        token.strip().lower()
        for token in re.split(r"[\s,]+", match.group("codes").strip())
        if token.strip()
    }
    return codes or {"all"}


def source_suppression_map(path: str | Path) -> dict[int, set[str]]:
    suppressions: dict[int, set[str]] = {}
    for line_number, raw_line in enumerate(read_script_text(path).splitlines(), start=1):
        comment = _line_comment_text(raw_line)
        line_codes = _suppression_codes(comment, f"{SUPPRESSION_MARKER}-line")
        next_line_codes = _suppression_codes(comment, f"{SUPPRESSION_MARKER}-next-line")
        if line_codes:
            suppressions.setdefault(line_number, set()).update(line_codes)
        if next_line_codes:
            suppressions.setdefault(line_number + 1, set()).update(next_line_codes)
    return suppressions


def source_suppresses_finding(suppressions: dict[int, set[str]], finding: Finding) -> bool:
    codes = suppressions.get(finding.line, set())
    return "all" in codes or finding.code.lower() in codes


@dataclass(frozen=True)
class CommandExpressionUse:
    expr: Expression
    context: str


def has_failure(
    findings: list[Finding],
    fail_level: str = "error",
    fail_confidence: str = "definite",
) -> bool:
    threshold = SEVERITY_ORDER[fail_level]
    confidence_threshold = CONFIDENCE_ORDER[fail_confidence]
    return any(
        SEVERITY_ORDER[finding.severity] >= threshold
        and CONFIDENCE_ORDER[finding.confidence] <= confidence_threshold
        for finding in findings
    )


def apply_confidence(findings: list[Finding], confidence: str) -> list[Finding]:
    if confidence == "definite":
        return findings
    return [
        Finding(
            line=finding.line,
            code=finding.code,
            message=finding.message,
            confidence=confidence,
            span=finding.span,
        )
        for finding in findings
    ]


BUILTIN_TYPED_CONSTANTS = {
    "-1",
    "0",
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "10",
    "action-move",
    "any-ally",
    "any-computer",
    "any-enemy",
    "any-human",
    "any-player",
    "c:",
    "false",
    "house",
    "my-player-number",
    "no-attack",
    "search-local",
    "search-remote",
    "target-player",
    "true",
}
BUILTIN_DYNAMIC_UNIT_IDS = {
    "my-elite-unique-unit",
    "my-unique-unit",
    "my-unique-unit-line",
}
BUILTIN_DYNAMIC_TECH_IDS = {
    "my-second-unique-research",
    "my-unique-research",
    "my-unique-unit-upgrade",
}
COMPATIBILITY_TECH_IDS = {
    "ri-cartography",
    "ri-fast-fire-ship",
}
BINARY_OBSERVED_STRATEGIC_NUMBER_NAMES = {
    "sn-target-evaluation-ally-proximity",
    "sn-target-evaluation-attack-attempts",
    "sn-target-evaluation-boat",
    "sn-target-evaluation-continent",
    "sn-target-evaluation-damage-capability",
    "sn-target-evaluation-distance",
    "sn-target-evaluation-hitpoints",
    "sn-target-evaluation-in-progress",
    "sn-target-evaluation-kills",
    "sn-target-evaluation-randomness",
    "sn-target-evaluation-range",
    "sn-target-evaluation-rof",
    "sn-target-evaluation-siege-weapon",
    "sn-target-evaluation-time-kill-ratio",
}

BUILTIN_POSITION_CONSTANTS = {
    "position-self",
    "position-center",
    "position-object",
}

COMMON_DEFINED_IDENTIFIER_PREFIXES = (
    "search-",
    "object-data-",
    "action-",
    "sn-",
    "class-",
)
STRATEGIC_NUMBER_COMMAND_HEADS = {
    "strategic-number",
    "set-strategic-number",
    "up-modify-sn",
    "up-compare-sn",
}

IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_-]*$")
RAW_LOAD_RE = re.compile(r"^#load\s+")
VALID_LOAD_RE = re.compile(r'^\s*\(?\s*load\s+"([^"]+)"\s*\)?\s*$')
VALID_SOURCE_LOAD_RE = re.compile(r'^\s*#load\s+"([^"]+)"\s*$')
VALID_INCLUDE_RE = re.compile(r'^\s*\(?\s*include\s+"([^"]+)"\s*\)?\s*$')
LOAD_RANDOM_START_RE = re.compile(r"^\s*\(?\s*load-random(?:\s|\)|$)")
LOAD_RANDOM_ENTRY_RE = re.compile(
    r'(?:(?P<weight>[+-]?\d+|\+[A-Za-z_][A-Za-z0-9_-]*|\+)\s+)?"(?P<include>[^"]+)"'
)
SPLIT_TYPED_COMPARISON_RE = re.compile(r"\s(?:<=|>=|<|>|==|!=)\s+g:")
UNSUPPORTED_AI_XS_FUNCTIONS = {
    "xsGetUnitTargetId": "not accepted by the AoE2 DE AI XS parser in sample_ai testing",
}
FATAL_PRE_PARSE_CODES = {
    "defrule-missing-arrow",
    "duplicate-preprocessor-else",
    "malformed-preprocessor-directive",
    "preprocessor-nesting-depth-exceeded",
    "unbalanced-parentheses",
    "unexpected-preprocessor-else",
    "unexpected-preprocessor-end-if",
    "unterminated-defrule",
    "unterminated-preprocessor-conditional",
}
RECOVERABLE_STRUCTURE_CODES = {
    "unbalanced-parentheses",
    "unterminated-defrule",
}
DEFCONST_MIN_VALUE = -32768
DEFCONST_MAX_VALUE = 32767
MAX_SOURCE_LINE_LENGTH = 255


def _load_builtin_class_entries() -> tuple[set[str], dict[int, set[str]]]:
    inventory_path = (
        Path(__file__).resolve().parents[2]
        / "docs"
        / "extracted"
        / "inventories"
        / "airef-value-family-inventory.json"
    )
    if not inventory_path.exists():
        return set(), {}

    data = json.loads(inventory_path.read_text(encoding="utf-8-sig"))
    builtin_names: set[str] = set()
    builtin_ids: dict[int, set[str]] = {}
    for family in data.get("families", []):
        if family.get("parameter_name") != "ClassId":
            continue
        for entry in family.get("entries", []):
            name = entry.get("name")
            entry_id = entry.get("id")
            if not name or entry_id is None:
                continue
            builtin_names.add(name)
            if name.endswith("*"):
                builtin_names.add(name.rstrip("*"))
            try:
                numeric_id = int(entry_id)
            except (TypeError, ValueError):
                continue
            builtin_ids.setdefault(numeric_id, set()).add(name)
            if name.endswith("*"):
                builtin_ids.setdefault(numeric_id, set()).add(name.rstrip("*"))
    return builtin_names, builtin_ids


BUILTIN_CLASS_NAMES, BUILTIN_CLASS_NAMES_BY_ID = _load_builtin_class_entries()


def _load_command_entries() -> dict[str, dict]:
    inventory_path = (
        Path(__file__).resolve().parents[2]
        / "docs"
        / "extracted"
        / "inventories"
        / "airef-command-inventory.json"
    )
    if not inventory_path.exists():
        return {}

    data = json.loads(inventory_path.read_text(encoding="utf-8-sig"))
    commands = {
        command.get("name", ""): command
        for command in data.get("commands", [])
        if command.get("name")
    }
    # AIRef currently labels this slot as GoalId, but the command compares
    # strategic numbers and the documented example uses sn-maximum-town-size.
    if "up-compare-sn" in commands and commands["up-compare-sn"].get("command_parameters"):
        commands["up-compare-sn"]["command_parameters"][0]["name"] = "SnId"
    return commands


COMMAND_ENTRIES = _load_command_entries()
COMMAND_TYPES = {
    name: command.get("command_type", "")
    for name, command in COMMAND_ENTRIES.items()
}
FACT_LOGICAL_HEADS = {
    "and",
    "or",
    "not",
    "nand",
    "nor",
    "xor",
    "xnor",
}
SCHEMA_VALIDATED_COMMANDS = {
    "build",
    "build-forward",
    "building-count",
    "can-build",
    "can-build-with-escrow",
    "can-research",
    "can-research-with-escrow",
    "can-train",
    "can-train-with-escrow",
    "goal",
    "building-available",
    "building-type-count",
    "building-type-count-total",
    "cc-players-unit-type-count",
    "acknowledge-taunt",
    "chat-local-to-self",
    "chat-to-all",
    "chat-to-allies",
    "chat-to-player",
    "civilian-population",
    "current-age",
    "difficulty",
    "disable-timer",
    "disable-self",
    "do-nothing",
    "enable-timer",
    "food-amount",
    "game-time",
    "gold-amount",
    "research",
    "research-available",
    "research-completed",
    "idle-farm-count",
    "military-population",
    "population",
    "population-cap",
    "release-escrow",
    "resource-found",
    "set-goal",
    "set-escrow-percentage",
    "set-strategic-number",
    "soldier-count",
    "stone-amount",
    "strategic-number",
    "taunt-detected",
    "timer-triggered",
    "train",
    "unit-count",
    "unit-available",
    "unit-type-count",
    "unit-type-count-total",
    "up-add-object-by-id",
    "up-clean-search",
    "up-compare-const",
    "up-copy-point",
    "up-drop-resources",
    "up-filter-distance",
    "up-filter-include",
    "up-filter-status",
    "up-find-resource",
    "up-gather-inside",
    "up-build",
    "up-can-build",
    "up-can-research",
    "up-can-train",
    "up-compare-goal",
    "up-compare-sn",
    "up-find-local",
    "up-find-remote",
    "up-get-object-data",
    "up-get-point",
    "up-get-point-distance",
    "up-get-search-state",
    "up-modify-goal",
    "up-modify-escrow",
    "up-modify-sn",
    "up-object-data",
    "up-point-distance",
    "up-pending-objects",
    "up-pending-placement",
    "up-full-reset-search",
    "up-remove-objects",
    "up-reset-search",
    "up-research",
    "up-research-status",
    "up-release-escrow",
    "up-set-target-by-id",
    "up-set-target-object",
    "up-target-objects",
    "up-target-point",
    "up-set-target-point",
    "up-timer-status",
    "up-train",
    "up-jump-rule",
    "wood-amount",
    "can-buy-commodity",
    "can-sell-commodity",
    "death-match-game",
    "housing-headroom",
    "true",
    "up-allied-resource-amount",
    "up-compare-flag",
    "up-enemy-units-in-town",
    "up-find-status-local",
    "up-find-status-remote",
    "up-gaia-type-count",
    "up-get-player-fact",
    "up-modify-flag",
    "up-players-in-game",
    "buy-commodity",
    "can-afford-building",
    "civ-selected",
    "commodity-buying-price",
    "commodity-selling-price",
    "current-age-time",
    "dropsite-min-distance",
    "enemy-buildings-in-town",
    "escrow-amount",
    "map-type",
    "player-valid",
    "players-building-count",
    "players-building-type-count",
    "players-current-age",
    "players-military-population",
    "players-population",
    "players-stance",
    "players-unit-type-count",
    "sell-commodity",
    "stance-toward",
    "town-under-attack",
    "up-allied-goal",
    "up-assign-builders",
    "up-can-build-line",
    "up-chat-data-to-all",
    "up-chat-data-to-player",
    "up-create-group",
    "up-cross-tiles",
    "up-filter-exclude",
    "up-get-fact",
    "up-get-focus-fact",
    "up-get-object-target-data",
    "up-get-precise-time",
    "up-get-target-fact",
    "up-jump-direct",
    "up-lerp-tiles",
    "up-modify-group-flag",
    "up-object-target-data",
    "up-point-contains",
    "up-projectile-detected",
    "up-reset-filters",
    "up-reset-group",
    "up-set-attack-stance",
    "up-set-defense-priority",
    "up-set-offense-priority",
    "up-set-placement-data",
    "cc-add-resource",
    "delete-unit",
    "false",
    "generate-random-number",
    "player-human",
    "player-in-game",
    "player-number",
    "players-civ",
    "players-civilian-population",
    "players-current-age-time",
    "population-headroom",
    "starting-age",
    "tribute-to-player",
    "up-add-object-cost",
    "up-add-point",
    "up-add-research-cost",
    "up-bound-precise-point",
    "up-build-line",
    "up-delete-objects",
    "up-filter-garrison",
    "up-filter-range",
    "up-find-player",
    "up-get-indirect-goal",
    "up-get-point-elevation",
    "up-get-rule-id",
    "up-group-size",
    "up-log-data",
    "up-point-explored",
    "up-projectile-target",
    "up-reset-cost-data",
    "up-reset-placement",
    "up-reset-scouts",
    "up-reset-unit",
    "up-resource-amount",
    "up-retreat-to",
    "up-send-flare",
    "up-send-scout",
    "up-set-group",
    "up-set-indirect-goal",
    "up-set-precise-target-point",
    "up-set-timer",
    "up-setup-cost-data",
    "up-tribute-to-player",
    "up-ungarrison",
    "warboat-count",
    "can-afford-research",
    "chat-to-allies-using-id",
    "current-score",
    "delete-building",
    "enemy-captured-relics",
    "hold-koh-ruin",
    "hold-relics",
    "map-size",
    "player-computer",
    "players-score",
    "random-number",
    "regicide-game",
    "set-difficulty-parameter",
    "starting-resources",
    "up-allied-sn",
    "up-bound-point",
    "up-building-type-in-town",
    "up-buy-commodity",
    "up-cc-add-resource",
    "up-chat-data-to-self",
    "up-compare-text",
    "up-disband-group-type",
    "up-enemy-villagers-in-town",
    "up-find-flare",
    "up-find-next-player",
    "up-gaia-type-count-total",
    "up-garrison",
    "up-get-fact-sum",
    "up-get-group-size",
    "up-get-object-type-data",
    "up-get-path-distance",
    "up-get-player-color",
    "up-get-point-contains",
    "up-get-timer",
    "up-guard-unit",
    "up-idle-unit-count",
    "up-lerp-percent",
    "up-object-type-count-total",
    "up-path-distance",
    "up-point-terrain",
    "up-remaining-boar-amount",
    "up-resource-amount",
    "up-retask-gatherers",
    "up-retreat-now",
    "up-sell-commodity",
    "up-store-player-name",
    "up-train-site-ready",
    "up-tribute-to-player",
    "up-unit-type-in-town",
    "up-update-targets",
    "victory-condition",
    "wall-completed-percentage",
    "attack-now",
    "chat-to-all-using-id",
    "chat-to-player-using-id",
    "enable-wall-placement",
    "game-type",
    "player-resigned",
    "resign",
    "set-stance",
    "up-attacker-class",
    "up-cc-send-cheat",
    "up-change-name",
    "up-delete-distant-farms",
    "up-enemy-buildings-in-town",
    "up-get-threat-data",
    "up-get-victory-data",
    "up-object-type-count",
    "up-player-distance",
    "up-point-elevation",
    "up-reset-building",
    "up-store-player-chat",
    "up-store-tech-name",
    "up-store-type-name",
    "xs-script-call",
    "acknowledge-event",
    "attack-soldier-count",
    "attack-warboat-count",
    "build-gate",
    "building-count-total",
    "build-wall",
    "can-afford-complete-wall",
    "can-afford-unit",
    "can-build-gate",
    "can-build-gate-with-escrow",
    "can-build-wall",
    "can-build-wall-with-escrow",
    "can-spy",
    "can-spy-with-escrow",
    "cc-players-building-count",
    "cc-players-building-type-count",
    "cc-players-unit-count",
    "chat-local",
    "chat-local-using-id",
    "chat-local-using-range",
    "chat-to-allies-using-range",
    "chat-to-all-using-range",
    "chat-to-enemies",
    "chat-to-enemies-using-id",
    "chat-to-enemies-using-range",
    "chat-to-player-using-range",
    "chat-trace",
    "cheats-enabled",
    "clear-tribute-memory",
    "defend-soldier-count",
    "defend-warboat-count",
    "disable-rule",
    "doctrine",
    "enable-rule",
    "event-detected",
    "gate-count",
    "log",
    "log-trace",
    "players-tribute",
    "players-unit-count",
    "set-author-email",
    "set-author-name",
    "set-author-version",
    "set-doctrine",
    "set-shared-goal",
    "set-signal",
    "shared-goal",
    "sheep-and-forage-too-far",
    "spy",
    "taunt",
    "taunt-using-range",
    "trace-fact",
    "unit-count-total",
    "wall-invisible-percentage",
    "up-add-cost-data",
    "up-allied-resource-percent",
    "up-can-search",
    "up-defender-count",
    "up-delete-idle-units",
    "up-find-player-flare",
    "up-get-attacker-class",
    "up-get-cost-delta",
    "up-get-event",
    "up-get-fact-max",
    "up-get-fact-min",
    "up-get-guard-state",
    "up-get-point-terrain",
    "up-get-point-zone",
    "up-get-projectile-player",
    "up-get-shared-goal",
    "up-get-signal",
    "up-get-treaty-data",
    "up-get-upgrade-id",
    "up-get-victory-limit",
    "up-jump-dynamic",
    "up-point-zone",
    "up-request-hunters",
    "up-reset-attack-now",
    "up-reset-target-priorities",
    "up-resource-percent",
    "up-set-event",
    "up-set-shared-goal",
    "up-set-signal",
    "up-store-map-name",
    "up-store-object-name",
    "up-store-text",
    "up-villager-type-in-town",
    "fe-break-point",
    "fe-cc-effect-amount",
    "fe-cc-effect-percent",
    "fe-exclude-from-attack-group",
    "fe-filter-garrisoned",
    "fe-idle-pasture-count",
    "fe-reset-attack-group-exclusion-list",
    "fe-set-signal",
    "fe-sub-game-type",
}
TYPE_OP_VALUES = {"c:", "g:", "s:", "c:<", "g:<", "s:<"}
SEARCH_SOURCE_VALUES = {"search-local", "search-remote"}
BARE_COMPARE_VALUES = {"<", "<=", ">", ">=", "==", "!="}


def _load_value_family_names(parameter_name: str) -> set[str]:
    inventory_path = (
        Path(__file__).resolve().parents[2]
        / "docs"
        / "extracted"
        / "inventories"
        / "airef-value-family-inventory.json"
    )
    if not inventory_path.exists():
        return set()

    data = json.loads(inventory_path.read_text(encoding="utf-8-sig"))
    for family in data.get("families", []):
        if family.get("parameter_name") != parameter_name:
            continue
        return {
            entry.get("name", "")
            for entry in family.get("entries", [])
            if entry.get("name")
        }
    return set()


def normalize_value_family_names(values: set[str]) -> set[str]:
    normalized: set[str] = set()
    for value in values:
        if not value:
            continue
        normalized.add(value)
        if value.endswith("*"):
            normalized.add(value.rstrip("*"))
    return normalized


def expand_value_aliases(values: set[str]) -> set[str]:
    expanded: set[str] = set()
    for value in values:
        for part in value.split(","):
            stripped = part.strip()
            if stripped:
                expanded.add(stripped)
    return expanded


def normalize_inventory_aliases(value: str) -> set[str]:
    aliases: set[str] = set()
    for part in value.split(","):
        stripped = re.sub(r"\s*\([^)]*\)", "", part).strip()
        if stripped:
            aliases.add(stripped)
    return aliases


def _load_object_ai_names() -> set[str]:
    inventory_path = (
        Path(__file__).resolve().parents[2]
        / "docs"
        / "extracted"
        / "inventories"
        / "airef-object-inventory.json"
    )
    if not inventory_path.exists():
        return set()

    data = json.loads(inventory_path.read_text(encoding="utf-8-sig"))
    names: set[str] = set()
    for entry in data.get("objects", []):
        names.update(normalize_inventory_aliases(str(entry.get("ai_name") or "")))
        names.update(normalize_inventory_aliases(str(entry.get("line") or "")))
        notes = str(entry.get("notes") or "")
        for match in re.finditer(r"Can be counted with ([A-Za-z0-9_-]+)", notes):
            names.add(match.group(1))
    return names


def _load_tech_ai_names() -> set[str]:
    inventory_path = (
        Path(__file__).resolve().parents[2]
        / "docs"
        / "extracted"
        / "inventories"
        / "airef-tech-inventory.json"
    )
    if not inventory_path.exists():
        return set()

    data = json.loads(inventory_path.read_text(encoding="utf-8-sig"))
    names: set[str] = set()
    for entry in data.get("techs", []):
        names.update(normalize_inventory_aliases(str(entry.get("ai_name") or "")))
    return names


def _load_strategic_number_names() -> set[str]:
    inventory_path = (
        Path(__file__).resolve().parents[2]
        / "docs"
        / "extracted"
        / "inventories"
        / "airef-strategic-number-inventory.json"
    )
    if not inventory_path.exists():
        return set()

    data = json.loads(inventory_path.read_text(encoding="utf-8-sig"))
    return {
        entry.get("name", "")
        for entry in data.get("strategic_numbers", [])
        if entry.get("name")
    }


def _load_archived_symbol_names(filename: str) -> set[str]:
    archive_path = Path(__file__).resolve().parents[2] / "docs" / "extracted" / filename
    if not archive_path.exists():
        return set()
    names: set[str] = set()
    for line in archive_path.read_text(encoding="utf-8-sig").splitlines():
        match = re.match(r"\|\s*`([^`]+)`\s*\|", line)
        if match:
            names.add(match.group(1))
    return names


DUC_ACTION_VALUES = _load_value_family_names("DUCAction")
FORMATION_VALUES = _load_value_family_names("Formation")
ATTACK_STANCE_VALUES = _load_value_family_names("AttackStance")
COMPARE_OP_VALUES = _load_value_family_names("compareOp") | BARE_COMPARE_VALUES
MATH_OP_VALUES = _load_value_family_names("mathOp")
PLACEMENT_TYPE_VALUES = _load_value_family_names("PlacementType")
RESEARCH_STATE_VALUES = _load_value_family_names("ResearchState")
RESOURCE_VALUES = _load_value_family_names("Resource")
ESCROW_RESOURCE_VALUES = {"food", "wood", "stone", "gold"}
AGE_VALUES = _load_value_family_names("Age")
DIFFICULTY_VALUES = _load_value_family_names("Difficulty")
OBJECT_DATA_VALUES = _load_value_family_names("ObjectData")
PLAYER_STANCE_VALUES = _load_value_family_names("PlayerStance")
POSITION_TYPE_VALUES = _load_value_family_names("PositionType") | {"position-curr-object"}
TIMER_STATE_VALUES = _load_value_family_names("TimerState")
OBJECT_LIST_VALUES = _load_value_family_names("ObjectList")
OBJECT_STATUS_VALUES = _load_value_family_names("ObjectStatus")
SEARCH_ORDER_VALUES = _load_value_family_names("SearchOrder")
CIV_VALUES = _load_value_family_names("Civ")
COMMODITY_VALUES = _load_value_family_names("Commodity")
FACT_ID_VALUES = _load_value_family_names("FactId")
SUPPLEMENTAL_MAP_TYPE_VALUES = {"custom"}
OBSERVED_UNVERIFIED_MAP_TYPE_VALUES = {"michi"}
MAP_TYPE_VALUES = _load_value_family_names("MapType") | SUPPLEMENTAL_MAP_TYPE_VALUES
PROJECTILE_TYPE_VALUES = _load_value_family_names("ProjectileType")
RESOURCE_TYPE_VALUES = _load_value_family_names("ResourceType") | ESCROW_RESOURCE_VALUES
EVENT_TYPE_VALUES = _load_value_family_names("EventType")
EXPLORED_STATE_VALUES = _load_value_family_names("ExploredState")
FIND_PLAYER_METHOD_VALUES = _load_value_family_names("FindPlayerMethod")
GAME_TYPE_VALUES = _load_value_family_names("GameType")
GROUP_TYPE_VALUES = _load_value_family_names("GroupType")
IDLE_TYPE_VALUES = _load_value_family_names("IdleType")
MAP_SIZE_VALUES = expand_value_aliases(_load_value_family_names("MapSize"))
PRIORITY_TYPE_VALUES = _load_value_family_names("PriorityType")
SCOUT_METHOD_VALUES = _load_value_family_names("ScoutMethod")
STARTING_RESOURCES_VALUES = _load_value_family_names("StartingResources")
SUB_GAME_TYPE_VALUES = _load_value_family_names("SubGameType")
VICTORY_CONDITION_VALUES = _load_value_family_names("VictoryCondition")
ACTION_ID_VALUES = _load_value_family_names("ActionId")
ATTR_ID_VALUES = _load_value_family_names("AttrId")
DIFF_PARAMETER_ID_VALUES = _load_value_family_names("DiffParameterId")
EFFECT_ID_VALUES = _load_value_family_names("EffectId")
ORDER_ID_VALUES = _load_value_family_names("OrderId")
TERRAIN_VALUES = _load_value_family_names("Terrain")
WALL_ID_VALUES = _load_value_family_names("WallId") | {"stone-wall-line"}
DOCUMENTED_VALUE_CONSTANTS = normalize_value_family_names(
    DUC_ACTION_VALUES
    | FORMATION_VALUES
    | ATTACK_STANCE_VALUES
    | PLACEMENT_TYPE_VALUES
    | RESEARCH_STATE_VALUES
    | RESOURCE_VALUES
    | ESCROW_RESOURCE_VALUES
    | AGE_VALUES
    | DIFFICULTY_VALUES
    | OBJECT_DATA_VALUES
    | PLAYER_STANCE_VALUES
    | POSITION_TYPE_VALUES
    | TIMER_STATE_VALUES
    | OBJECT_LIST_VALUES
    | OBJECT_STATUS_VALUES
    | SEARCH_ORDER_VALUES
    | CIV_VALUES
    | COMMODITY_VALUES
    | FACT_ID_VALUES
    | MAP_TYPE_VALUES
    | PROJECTILE_TYPE_VALUES
    | RESOURCE_TYPE_VALUES
    | EVENT_TYPE_VALUES
    | EXPLORED_STATE_VALUES
    | FIND_PLAYER_METHOD_VALUES
    | GAME_TYPE_VALUES
    | GROUP_TYPE_VALUES
    | IDLE_TYPE_VALUES
    | MAP_SIZE_VALUES
    | PRIORITY_TYPE_VALUES
    | SCOUT_METHOD_VALUES
    | STARTING_RESOURCES_VALUES
    | SUB_GAME_TYPE_VALUES
    | VICTORY_CONDITION_VALUES
    | ACTION_ID_VALUES
    | ATTR_ID_VALUES
    | DIFF_PARAMETER_ID_VALUES
    | EFFECT_ID_VALUES
    | ORDER_ID_VALUES
    | TERRAIN_VALUES
    | WALL_ID_VALUES
)
# AIRef currently documents several villager gatherer aliases through object
# notes, but omits the aggregate food gatherer alias that appears in the
# AoE2 AiScript extension unit-id data as id 978.
SUPPLEMENTAL_DOCUMENTED_OBJECT_NAMES = {"villager-food"}
DOCUMENTED_OBJECT_NAMES = _load_object_ai_names() | SUPPLEMENTAL_DOCUMENTED_OBJECT_NAMES
DOCUMENTED_TECH_NAMES = _load_tech_ai_names()
ARCHIVED_NON_DE_OBJECT_NAMES = _load_archived_symbol_names("non-de-object-archive.md")
ARCHIVED_NON_DE_TECH_NAMES = _load_archived_symbol_names("non-de-tech-archive.md")
ARCHIVED_NON_DE_STRATEGIC_NUMBER_NAMES = _load_archived_symbol_names("non-de-strategic-number-archive.md")
DOCUMENTED_STRATEGIC_NUMBER_NAMES = _load_strategic_number_names()
KNOWN_STRATEGIC_NUMBER_NAMES = DOCUMENTED_STRATEGIC_NUMBER_NAMES | BINARY_OBSERVED_STRATEGIC_NUMBER_NAMES
DOCUMENTED_TYPED_CONSTANTS = (
    DOCUMENTED_OBJECT_NAMES
    | DOCUMENTED_TECH_NAMES
    | BUILTIN_DYNAMIC_UNIT_IDS
    | BUILTIN_DYNAMIC_TECH_IDS
    | COMPATIBILITY_TECH_IDS
)

LINT_PROFILE_SUPPRESSIONS = {
    "default": set(),
    "corpus": {
        "builtin-constant-alias",
        "duplicate-defconst-conflict",
        "load-random-plus-weight-de-behavior",
        "redundant-built-in-defconst",
        "repeat-chat",
        "up-can-build-zero-escrow",
    },
}


def expression_tokens(expr: str) -> list[str]:
    tokens: list[str] = []
    token: list[str] = []
    in_string = False
    for index, char in enumerate(expr):
        if char == '"' and not is_escaped_quote(expr, index):
            if token:
                tokens.append("".join(token))
                token = []
            in_string = not in_string
            continue
        if in_string:
            continue
        if char.isspace() or char in "()":
            if token:
                tokens.append("".join(token))
                token = []
            continue
        token.append(char)
    if token:
        tokens.append("".join(token))
    return tokens


def expressions_with_lines(expressions: tuple[str, ...], lines: tuple[int, ...], fallback_line: int) -> list[tuple[str, int]]:
    if len(lines) == len(expressions):
        return list(zip(expressions, lines))
    return [(expression, fallback_line) for expression in expressions]


def is_int_literal(value: str) -> bool:
    return value.lstrip("-").isdigit()


def is_symbolic_identifier(value: str) -> bool:
    return bool(IDENTIFIER_RE.match(value))


def undefined_typed_constant_message(value: str) -> str:
    if value in ARCHIVED_NON_DE_TECH_NAMES:
        return f"{value!r} follows c: but is archived as non-DE and is excluded from the DE tech registry"
    if value in ARCHIVED_NON_DE_OBJECT_NAMES:
        return f"{value!r} follows c: but is archived as non-DE and is excluded from the DE object registry"
    if value in ARCHIVED_NON_DE_STRATEGIC_NUMBER_NAMES:
        return f"{value!r} follows c: but is archived as non-DE and is excluded from the DE strategic-number registry"
    return f"{value!r} follows c: but is not defined with defconst"


def lint_typed_constants(
    line: int,
    expr: str,
    defined_constants: set[str],
) -> list[Finding]:
    findings: list[Finding] = []
    tokens = expression_tokens(expr)
    for index, token in enumerate(tokens[:-1]):
        if token != "c:":
            continue
        value = tokens[index + 1]
        if is_int_literal(value):
            continue
        if (
            value in defined_constants
            or value in BUILTIN_TYPED_CONSTANTS
            or value in DOCUMENTED_TYPED_CONSTANTS
            or value in BUILTIN_CLASS_NAMES
            or value in DOCUMENTED_VALUE_CONSTANTS
        ):
            continue
        if value.startswith(("g:", "s:", "c:")):
            continue
        if is_symbolic_identifier(value):
            findings.append(
                Finding(
                    line,
                    "undefined-constant",
                    undefined_typed_constant_message(value),
                )
            )
    return findings


def lint_strategic_number_identifier(
    line: int,
    expr: str,
    defined_constants: set[str],
) -> list[Finding]:
    symbol = first_symbol(expr)
    if symbol not in STRATEGIC_NUMBER_COMMAND_HEADS:
        return []

    tokens = expression_tokens(expr)
    if len(tokens) < 2:
        return []

    value = tokens[1]
    if is_int_literal(value):
        return []
    if value in defined_constants:
        return []
    if value in KNOWN_STRATEGIC_NUMBER_NAMES:
        return []
    if value.startswith(("g:", "s:", "c:")):
        return []
    if value.startswith("sn-") and is_symbolic_identifier(value):
        if value in ARCHIVED_NON_DE_STRATEGIC_NUMBER_NAMES:
            message = f"{value!r} is archived as non-DE and is excluded from the DE strategic-number registry"
        else:
            message = f"{value!r} is used as a strategic number but is not defined with defconst"
        return [
            Finding(
                line,
                "undefined-strategic-number",
                message,
            )
        ]
    return []


def lint_multi_goal_writer(
    line: int,
    expr: str,
    constants: dict[str, int],
) -> list[Finding]:
    symbol = first_symbol(expr)
    tokens = expression_tokens(expr)
    if symbol == "up-get-point":
        if len(tokens) < 3:
            return []
        goal_token = tokens[2]
        min_goal = 41
        width = 2
    elif symbol == "up-get-search-state":
        if len(tokens) < 2:
            return []
        goal_token = tokens[1]
        min_goal = 41
        width = 4
    else:
        return []

    if is_int_literal(goal_token):
        goal_id = int(goal_token)
    else:
        goal_id = constants.get(goal_token)
        if goal_id is None:
            return []

    if goal_id < min_goal:
        return [
            Finding(
                line,
                "unsafe-goal-block",
                f"{symbol} writes {width} consecutive goals; use goal {min_goal} or higher",
            )
        ]
    return []


def lint_up_get_point_position_identifier(
    line: int,
    expr: str,
    defined_constants: set[str],
) -> list[Finding]:
    if first_symbol(expr) != "up-get-point":
        return []

    tokens = expression_tokens(expr)
    if len(tokens) < 3:
        return []

    position_token = tokens[1]
    if is_int_literal(position_token):
        return []
    if position_token in BUILTIN_POSITION_CONSTANTS:
        return []
    if position_token in defined_constants:
        return []
    if position_token.startswith(("g:", "s:", "c:")):
        return []
    if is_symbolic_identifier(position_token):
        return [
            Finding(
                line,
                "undefined-position-constant",
                f"{position_token!r} is used by up-get-point but is not defined with defconst",
            )
        ]
    return []


def lint_up_can_build_zero_escrow(line: int, expr: str) -> list[Finding]:
    if first_symbol(expr) != "up-can-build":
        return []

    tokens = expression_tokens(expr)
    if len(tokens) < 2:
        return []
    if tokens[1] != "0":
        return []

    return [
        Finding(
            line,
            "up-can-build-zero-escrow",
            "use a goal set to without-escrow instead of literal 0 to avoid DE AIScript 'Invalid goal used (0)' logs",
        )
    ]


def lint_split_typed_comparison(line: int, expr: str) -> list[Finding]:
    if not SPLIT_TYPED_COMPARISON_RE.search(expr):
        return []

    return [
        Finding(
            line,
            "split-typed-comparison",
            "use typed comparison operators like g:< or g:<=, not '< g:' or '<= g:'",
        )
    ]


def lint_common_identifier_uses(
    line: int,
    expr: str,
    defined_constants: set[str],
) -> list[Finding]:
    findings: list[Finding] = []
    tokens = expression_tokens(expr)
    if not tokens:
        return findings

    head = tokens[0]
    for token in tokens[1:]:
        if token in defined_constants or token in BUILTIN_TYPED_CONSTANTS:
            continue
        if token in DOCUMENTED_TYPED_CONSTANTS or token in KNOWN_STRATEGIC_NUMBER_NAMES:
            continue
        if token in OBJECT_DATA_VALUES:
            continue
        if token in SEARCH_ORDER_VALUES:
            continue
        if token in DUC_ACTION_VALUES:
            continue
        if head in STRATEGIC_NUMBER_COMMAND_HEADS and token.startswith("sn-"):
            continue
        if token.startswith(("g:", "s:", "c:")):
            continue
        if is_int_literal(token):
            continue
        if not is_symbolic_identifier(token):
            continue
        if token == head:
            continue
        if any(token.startswith(prefix) for prefix in COMMON_DEFINED_IDENTIFIER_PREFIXES):
            findings.append(
                Finding(
                    line,
                    "undefined-identifier",
                    f"{token!r} looks like an AoE identifier but is not defined with defconst",
                )
            )
    return findings


def lint_builtin_defconst_shadow(path: Path) -> list[Finding]:
    findings: list[Finding] = []
    for source_line in active_source_lines(path):
        index = source_line.number
        raw_line = source_line.text
        for name, value_token in iter_defconst_tokens(raw_line):
            value = int(value_token) if is_int_literal(value_token) else None
            if name in BUILTIN_CLASS_NAMES:
                findings.append(
                    Finding(
                        index,
                        "redundant-built-in-defconst",
                        f"{name!r} is already a documented built-in class constant; prefer the built-in name directly",
                    )
                )
                continue
            if not name.startswith("class-"):
                continue
            if value_token in BUILTIN_CLASS_NAMES:
                findings.append(
                    Finding(
                        index,
                        "builtin-constant-alias",
                        f"{name!r} aliases documented built-in class constant {value_token!r}; prefer the built-in name directly",
                    )
                )
                continue
            if value is None:
                continue
            builtin_names = BUILTIN_CLASS_NAMES_BY_ID.get(value, set())
            if builtin_names:
                preferred = sorted(builtin_names)[0]
                findings.append(
                    Finding(
                        index,
                        "builtin-constant-alias",
                        f"{name!r} redefines built-in id {value}; prefer documented built-in name {preferred!r}",
                    )
                )
    return findings


def lint_defconst_conflicts(path: Path) -> list[Finding]:
    findings: list[Finding] = []
    seen: dict[str, tuple[str, int]] = {}
    for source_line in active_source_lines(path):
        if source_line.confidence != "definite":
            continue
        for name, value in iter_defconst_tokens(source_line.text):
            previous = seen.get(name)
            if previous is None:
                seen[name] = (value, source_line.number)
                continue
            previous_value, previous_line = previous
            if previous_value == value:
                continue
            findings.append(
                Finding(
                    source_line.number,
                    "duplicate-defconst-conflict",
                    f"{name!r} is defined as {previous_value!r} on line {previous_line} and {value!r} here",
                )
            )
    return findings


def lint_defconst_alias_cycles(path: Path) -> list[Finding]:
    tokens: dict[str, str] = {}
    locations: dict[str, tuple[int, str]] = {}
    for source_line in active_source_lines(path):
        for name, value in iter_defconst_tokens(source_line.text):
            tokens[name] = value
            locations[name] = (source_line.number, source_line.confidence)

    findings: list[Finding] = []
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
                    line, confidence = locations[cycle[0]]
                    chain = " -> ".join((*cycle, cycle[0]))
                    findings.append(
                        Finding(
                            line,
                            "defconst-alias-cycle",
                            f"defconst alias cycle {chain!r} cannot resolve to a numeric value",
                            confidence,
                        )
                    )
                break
            path_names.append(current)
            next_value = tokens[current]
            if is_int_literal(next_value):
                break
            current = next_value
    return findings


def lint_malformed_defconst(path: Path) -> list[Finding]:
    findings: list[Finding] = []
    for source_line in active_source_lines(path):
        code = strip_comment(source_line.text)
        if "(defconst" not in code:
            continue
        spans = defconst_form_spans(code)
        if not spans and code.strip().startswith("(defconst"):
            findings.append(
                Finding(
                    source_line.number,
                    "malformed-defconst",
                    "defconst requires exactly a symbol name and integer value",
                    source_line.confidence,
                )
            )
            continue
        for _start, form in spans:
            parsed = parse_defconst_form(form)
            if parsed is not None:
                continue
            value = form.removeprefix("(defconst").rstrip(")").strip()
            if len(value.split()) < 2:
                findings.append(
                    Finding(
                        source_line.number,
                        "malformed-defconst",
                        "defconst requires exactly a symbol name and integer value",
                        source_line.confidence,
                    )
                )
                continue
            if value.startswith('"') or ' "' in value:
                quote_count = sum(
                    1
                    for index, char in enumerate(value)
                    if char == '"' and not is_escaped_quote(value, index)
                )
                quote_message = "missing a closing quote" if quote_count % 2 == 1 else "is malformed"
                findings.append(
                    Finding(
                        source_line.number,
                        "malformed-defconst",
                        f"defconst quoted value {value!r} {quote_message}",
                        source_line.confidence,
                    )
                )
                continue
            findings.append(
                Finding(
                    source_line.number,
                    "malformed-defconst",
                    f"defconst value {value!r} must be a single token or quoted text",
                    source_line.confidence,
                )
            )
    return findings


def lint_line_length(path: Path) -> list[Finding]:
    findings: list[Finding] = []
    for source_line in active_source_lines(path):
        if len(source_line.text) <= MAX_SOURCE_LINE_LENGTH:
            continue
        findings.append(
            Finding(
                source_line.number,
                "source-line-too-long",
                f"line has {len(source_line.text)} characters; AI scripts allow at most {MAX_SOURCE_LINE_LENGTH} including comments",
                source_line.confidence,
            )
        )
    return findings


def lint_defconst_numeric_range(path: Path) -> list[Finding]:
    findings: list[Finding] = []
    for source_line in active_source_lines(path):
        for name, value_token in iter_defconst_tokens(source_line.text):
            if not is_int_literal(value_token):
                continue
            value = int(value_token)
            if DEFCONST_MIN_VALUE <= value <= DEFCONST_MAX_VALUE:
                continue
            findings.append(
                Finding(
                    source_line.number,
                    "defconst-value-out-of-range",
                    f"defconst {name!r} value {value} is outside signed 16-bit range {DEFCONST_MIN_VALUE} to {DEFCONST_MAX_VALUE}",
                    source_line.confidence,
                )
            )
    return findings


def lint_malformed_load_directives(path: Path) -> list[Finding]:
    findings: list[Finding] = []
    for source_line in active_source_lines(path):
        code = strip_comment(source_line.text)
        if not code:
            continue
        if code.startswith("#load") and not code.startswith(("#load-if-defined", "#load-if-not-defined")):
            if not VALID_SOURCE_LOAD_RE.match(code):
                findings.append(
                    Finding(
                        source_line.number,
                        "malformed-load-directive",
                        '#load requires one quoted target, for example #load "tasks/init"',
                        source_line.confidence,
                    )
                )
            continue
        if re.match(r"^\s*\(?\s*load(?:\s|\))", code):
            if not VALID_LOAD_RE.match(code):
                findings.append(
                    Finding(
                        source_line.number,
                        "malformed-load-directive",
                        'load requires one quoted target, for example (load "tasks/init")',
                        source_line.confidence,
                    )
                )
            continue
        if re.match(r"^\s*\(?\s*include\b", code):
            match = VALID_INCLUDE_RE.match(code)
            if not match:
                findings.append(
                    Finding(
                        source_line.number,
                        "malformed-include-directive",
                        'include requires one quoted target, for example (include "debug.xs")',
                        source_line.confidence,
                    )
                )
                continue
            if Path(match.group(1)).suffix.lower() != ".xs":
                findings.append(
                    Finding(
                        source_line.number,
                        "include-missing-xs-extension",
                        'include target should include the .xs file extension, for example (include "debug.xs")',
                        source_line.confidence,
                    )
                )
    return findings


def _load_random_remainder_after_start(code: str) -> str:
    return LOAD_RANDOM_START_RE.sub("", code, count=1)


def _load_random_remainder_is_valid(remainder: str) -> bool:
    text = remainder.strip()
    if not text:
        return True

    while text:
        if text.startswith(")"):
            text = text[1:].strip()
            if text:
                return False
            return True

        match = LOAD_RANDOM_ENTRY_RE.match(text)
        if not match:
            return False
        text = text[match.end() :].strip()

    return True


def _load_random_plus_weights(remainder: str) -> list[str]:
    weights: list[str] = []
    text = remainder.strip()
    while text:
        if text.startswith(")"):
            break
        match = LOAD_RANDOM_ENTRY_RE.match(text)
        if not match:
            break
        weight = match.group("weight")
        if weight and weight.startswith("+"):
            weights.append(weight)
        text = text[match.end() :].strip()
    return weights


def lint_malformed_load_random_directives(path: Path) -> list[Finding]:
    findings: list[Finding] = []
    in_load_random = False
    load_random_balance = 0

    for source_line in active_source_lines(path):
        code = strip_comment(source_line.text)
        if not code:
            continue

        if not in_load_random:
            if not LOAD_RANDOM_START_RE.match(code):
                continue
            in_load_random = count_code_parens(code) > 0
            remainder = _load_random_remainder_after_start(code)
        else:
            remainder = code

        if not _load_random_remainder_is_valid(remainder):
            findings.append(
                Finding(
                    source_line.number,
                    "malformed-load-random-directive",
                    'load-random entries require an optional weight followed by a quoted target, for example 50 "strategy-a"',
                    source_line.confidence,
                )
            )

        if in_load_random:
            load_random_balance += count_code_parens(code)
            if load_random_balance <= 0:
                in_load_random = False
                load_random_balance = 0

    return findings


def lint_load_random_plus_weight_behavior(path: Path) -> list[Finding]:
    findings: list[Finding] = []
    in_load_random = False
    load_random_balance = 0

    for source_line in active_source_lines(path):
        code = strip_comment(source_line.text)
        if not code:
            continue

        if not in_load_random:
            if not LOAD_RANDOM_START_RE.match(code):
                continue
            in_load_random = count_code_parens(code) > 0
            remainder = _load_random_remainder_after_start(code)
        else:
            remainder = code

        if _load_random_remainder_is_valid(remainder):
            for weight in _load_random_plus_weights(remainder):
                findings.append(
                    Finding(
                        source_line.number,
                        "load-random-plus-weight-de-behavior",
                        f"load-random plus weight {weight!r} is documented as UP syntax with uncertain or bugged DE behavior",
                        source_line.confidence,
                    )
                )

        if in_load_random:
            load_random_balance += count_code_parens(code)
            if load_random_balance <= 0:
                in_load_random = False
                load_random_balance = 0

    return findings


def lint_parenthesis_balance(path: Path) -> list[Finding]:
    findings: list[Finding] = []
    balance = 0
    for source_line in active_source_lines(path):
        index = source_line.number
        raw_line = source_line.text
        code = strip_comment(raw_line)
        balance += count_code_parens(code)
        if balance < 0:
            findings.append(
                Finding(
                    index,
                    "unbalanced-parentheses",
                    "line closes more parentheses than have been opened",
                )
            )
            return findings

    if balance > 0:
        findings.append(
            Finding(
                index if "index" in locals() else 1,
                "unbalanced-parentheses",
                "file is missing one or more closing parentheses",
            )
        )
    return findings


def lint_defrule_structure(path: Path) -> list[Finding]:
    findings: list[Finding] = []
    in_rule = False
    saw_arrow = False
    start_line = 0
    rule_balance = 0

    for source_line in active_source_lines(path):
        index = source_line.number
        raw_line = source_line.text
        code = strip_comment(raw_line)
        if not code:
            continue

        if is_defrule_start(code):
            if in_rule:
                findings.append(
                    Finding(
                        start_line,
                        "unterminated-defrule",
                        "previous defrule is missing its closing parenthesis",
                    )
                )
            in_rule = True
            saw_arrow = False
            start_line = index
            rule_balance = count_code_parens(code)
            if split_rule_arrow(code) is not None:
                saw_arrow = True
            if rule_balance == 0:
                if not saw_arrow:
                    findings.append(
                        Finding(
                            start_line,
                            "defrule-missing-arrow",
                            "defrule closes without an => action separator",
                        )
                    )
                in_rule = False
                saw_arrow = False
                start_line = 0
                rule_balance = 0
            continue

        if not in_rule:
            continue

        if split_rule_arrow(code) is not None:
            saw_arrow = True

        rule_balance += count_code_parens(code)
        if rule_balance == 0:
            if not saw_arrow:
                findings.append(
                    Finding(
                        start_line,
                        "defrule-missing-arrow",
                        "defrule closes without an => action separator",
                    )
                )
            in_rule = False
            saw_arrow = False
            start_line = 0
            rule_balance = 0

    return findings


def lint_xs_file(path: str | Path) -> list[Finding]:
    script_path = Path(path)
    findings: list[Finding] = []
    for index, raw_line in enumerate(read_script_text(script_path).splitlines(), start=1):
        code = raw_line.split("//", 1)[0]
        for function_name, reason in UNSUPPORTED_AI_XS_FUNCTIONS.items():
            if re.search(rf"\b{re.escape(function_name)}\s*\(", code):
                findings.append(
                    Finding(
                        index,
                        "unsupported-ai-xs-function",
                        f"{function_name} is blocked for AI XS: {reason}",
                    )
                )
    return findings


def lint_livestock_point_default(rule: object) -> list[Finding]:
    facts = getattr(rule, "facts")
    actions = getattr(rule, "actions")
    line = getattr(rule, "start_line")
    searches_livestock = any(
        first_symbol(expr) in {"up-find-local", "up-find-remote"}
        and "livestock" in expr
        for expr in (*facts, *actions)
    )
    if not searches_livestock:
        return []
    if any(
        first_symbol(action) == "up-target-point" and " action-default " in action
        for action in actions
    ):
        return [
            Finding(
                line,
                "livestock-default-point",
                "use action-move, not action-default, when moving livestock to a point",
            )
        ]
    return []


def lint_unscoped_duc_targets(rules: tuple[object, ...]) -> list[Finding]:
    has_local_scope = False
    findings: list[Finding] = []

    def reset_clears_local(expr: str) -> bool:
        tokens = expression_tokens(expr)
        return len(tokens) < 3 or tokens[2] == "1"

    for rule in rules:
        facts = getattr(rule, "facts")
        actions = getattr(rule, "actions")
        fact_lines = getattr(rule, "fact_lines", ()) or (getattr(rule, "start_line"),) * len(facts)
        action_lines = getattr(rule, "action_lines", ()) or (getattr(rule, "start_line"),) * len(actions)

        for expr, line in (
            *expressions_with_lines(facts, fact_lines, getattr(rule, "start_line")),
            *expressions_with_lines(actions, action_lines, getattr(rule, "start_line")),
        ):
            symbol = first_symbol(expr)
            if symbol == "up-full-reset-search" or (symbol == "up-reset-search" and reset_clears_local(expr)):
                has_local_scope = False
            elif symbol in {
                "up-find-local",
                "up-add-object-by-id",
                "up-set-target-by-id",
                "up-set-target-object",
                "up-set-group",
            }:
                has_local_scope = True
            elif symbol in {"up-target-point", "up-target-objects"} and not has_local_scope:
                findings.append(
                    Finding(
                        line,
                        "unscoped-duc-target",
                        f"{symbol} runs without finding/adding/setting local target objects in retained search state",
                    )
                )
    return findings


def lint_up_build_place_point_escrow(rule: object) -> list[Finding]:
    actions = getattr(rule, "actions")
    action_lines = getattr(rule, "action_lines", ()) or (getattr(rule, "start_line"),) * len(actions)
    findings: list[Finding] = []
    for action, line in expressions_with_lines(actions, action_lines, getattr(rule, "start_line")):
        tokens = expression_tokens(action)
        if len(tokens) < 4:
            continue
        if tokens[0] != "up-build" or tokens[1] != "place-point":
            continue
        escrow_token = tokens[2]
        if escrow_token.endswith("-x") or escrow_token.endswith("-y") or "point" in escrow_token:
            findings.append(
                Finding(
                    line,
                    "up-build-place-point-coordinate-as-escrow",
                    "up-build place-point uses the target set by up-set-target-point; its third argument is escrow state, not the point coordinate",
                )
            )
    return findings


def count_rule_elements(rule: object) -> int:
    def count_expr(expr: Expression) -> int:
        total = 1
        for arg in expr.args:
            if isinstance(arg, Expression):
                total += count_expr(arg)
        return total

    fact_exprs = getattr(rule, "fact_exprs", ())
    action_exprs = getattr(rule, "action_exprs", ())
    if not fact_exprs and not action_exprs:
        return len(getattr(rule, "facts")) + len(getattr(rule, "actions"))
    return sum(count_expr(expr) for expr in (*fact_exprs, *action_exprs))


def expression_arg_values(expr: Expression) -> list[str] | None:
    values: list[str] = []
    for arg in expr.args:
        if not isinstance(arg, Atom):
            return None
        values.append(arg.value)
    return values


def expression_arg_span(expr: Expression, index: int) -> SourceSpan | None:
    if index < 0 or index >= len(expr.args):
        return None
    arg = expr.args[index]
    if not isinstance(arg, Atom):
        return None
    return SourceSpan(arg.line, arg.start_col, arg.line, arg.end_col)


def finding_for_arg(expr: Expression, index: int, code: str, message: str) -> Finding:
    return Finding(expr.line, code, message, span=expression_arg_span(expr, index))


def iter_command_expression_uses(rule: object) -> list[CommandExpressionUse]:
    expressions: list[CommandExpressionUse] = []

    def walk_fact(expr: Expression) -> None:
        if expr.head not in FACT_LOGICAL_HEADS:
            expressions.append(CommandExpressionUse(expr, "fact"))
        for arg in expr.args:
            if isinstance(arg, Expression):
                walk_fact(arg)

    for expr in getattr(rule, "fact_exprs", ()):
        walk_fact(expr)
    expressions.extend(CommandExpressionUse(expr, "action") for expr in getattr(rule, "action_exprs", ()))
    return expressions


def is_known_schema_value(value: str, valid_values: set[str], defined_constants: set[str]) -> bool:
    return value in valid_values or value in defined_constants or is_int_literal(value)


def direct_id_values_for_parameter(parameter_name: str) -> set[str] | None:
    if parameter_name in {"BuildingId", "ObjectId", "UnitId"}:
        return DOCUMENTED_OBJECT_NAMES | BUILTIN_DYNAMIC_UNIT_IDS | BUILTIN_CLASS_NAMES
    if parameter_name == "TechId":
        return DOCUMENTED_TECH_NAMES | BUILTIN_DYNAMIC_TECH_IDS | COMPATIBILITY_TECH_IDS
    if parameter_name == "ClassId":
        return BUILTIN_CLASS_NAMES
    return None


def direct_id_not_documented_message(command: str, parameter_name: str, value: str) -> str:
    if parameter_name in {"BuildingId", "ObjectId", "UnitId"} and value in ARCHIVED_NON_DE_OBJECT_NAMES:
        return f"{command} {parameter_name} {value!r} is archived as non-DE and is excluded from the DE object registry"
    if parameter_name == "TechId" and value in ARCHIVED_NON_DE_TECH_NAMES:
        return f"{command} {parameter_name} {value!r} is archived as non-DE and is excluded from the DE tech registry"
    return f"{command} {parameter_name} {value!r} is not documented"


def is_any_every_player_wildcard(value: str) -> bool:
    return value.startswith("any-") or value.startswith("every-")


def is_flare_unsupported_player_wildcard(value: str) -> bool:
    return value.startswith("this-any-") or value.startswith("every-")


SINGLE_PLAYER_NUMBER_COMMANDS = {
    "up-get-player-color",
    "up-get-upgrade-id",
    "up-get-player-fact",
    "up-set-placement-data",
    "up-store-player-chat",
    "up-store-player-name",
}


def typed_operand_kind(value: str) -> str | None:
    if value.startswith("sn-"):
        return "strategic number"
    if value.startswith(("gl-", "goal-")):
        return "goal"
    return None


def expected_family_for_parameter(parameter_name: str) -> str | None:
    if parameter_name in {"GoalId", "EscrowGoalId", "OptionGoalId", "SharedGoalId"}:
        return "goal"
    if parameter_name == "SnId":
        return "strategic number"
    if parameter_name in {"BuildingId", "UnitId", "ObjectId", "TechId", "ClassId"}:
        return parameter_name.removesuffix("Id").lower()
    return None


def lint_parameter_family_operand(
    expr: Expression,
    parameters: list[dict],
    parameter_name: str,
    value: str,
    index: int,
) -> Finding | None:
    if index > 0 and parameters[index - 1].get("name") in {"typeOp", "mathOp", "compareOp"}:
        return None
    expected_kind = expected_family_for_parameter(parameter_name)
    actual_kind = typed_operand_kind(value)
    if expected_kind is None or actual_kind is None or expected_kind == actual_kind:
        return None
    return finding_for_arg(
        expr,
        index,
        "command-family-mismatch",
        f"{expr.head} {parameter_name} argument {index + 1} uses {value!r}, which looks like a {actual_kind}; expected {expected_kind}",
    )


NUMERIC_RANGE_PARAMETER_NAMES = {
    "EventId",
    "GoalId",
    "SharedGoalId",
    "SignalId",
    "TauntId",
    "TimerId",
}


def explicit_numeric_range(parameter: dict) -> tuple[int, int] | None:
    range_text = str(parameter.get("range", ""))
    if not range_text or " or " in range_text.lower():
        return None
    match = re.search(r"(?:from\s+)?(-?[\d,]+)\s+to\s+(-?[\d,]+)", range_text, re.IGNORECASE)
    if not match:
        return None
    minimum = int(match.group(1).replace(",", ""))
    maximum = int(match.group(2).replace(",", ""))
    if minimum > maximum:
        minimum, maximum = maximum, minimum
    return minimum, maximum


def lint_numeric_range_operand(
    expr: Expression,
    args: list[str],
    parameters: list[dict],
    parameter: dict,
    value: str,
    index: int,
    constant_values: dict[str, int],
) -> Finding | None:
    parameter_name = parameter.get("name", "")
    if parameter_name not in NUMERIC_RANGE_PARAMETER_NAMES:
        return None
    numeric_range = explicit_numeric_range(parameter)
    if numeric_range is None:
        return None
    if index > 0 and parameters[index - 1].get("name") in {"typeOp", "mathOp", "compareOp"}:
        operator = args[index - 1]
        if not operator.startswith("c:"):
            return None
    if is_int_literal(value):
        numeric_value = int(value)
        resolved = ""
    elif value in constant_values:
        numeric_value = constant_values[value]
        resolved = f" (defined as {numeric_value})"
    else:
        return None
    minimum, maximum = numeric_range
    if minimum <= numeric_value <= maximum:
        return None
    return finding_for_arg(
        expr,
        index,
        "command-numeric-range-mismatch",
        f"{expr.head} {parameter_name} argument {index + 1} uses {value!r}{resolved}; expected {minimum} to {maximum}",
    )


def expected_operand_kind_for_typed_operator(operator: str) -> str | None:
    if operator.startswith("g:"):
        return "goal"
    if operator.startswith("s:"):
        return "strategic number"
    return None


def lint_type_op_operand(
    expr: Expression,
    args: list[str],
    parameter_index: int,
) -> Finding | None:
    if parameter_index + 1 >= len(args):
        return None
    operator = args[parameter_index]
    expected_kind = expected_operand_kind_for_typed_operator(operator)
    if expected_kind is None:
        return None
    operand = args[parameter_index + 1]
    actual_kind = typed_operand_kind(operand)
    if actual_kind is None or actual_kind == expected_kind:
        return None
    suggested_prefix = "g:" if actual_kind == "goal" else "s:"
    return finding_for_arg(
        expr,
        parameter_index + 1,
        "command-typed-operand-mismatch",
        f"{expr.head} argument {parameter_index + 2} uses {operand!r}, which looks like a {actual_kind}, "
        f"but argument {parameter_index + 1} is {operator!r}; use {suggested_prefix} when reading a {actual_kind} value",
    )


def lint_command_schema(rule: object, defined_constants: set[str], constant_values: dict[str, int]) -> list[Finding]:
    findings: list[Finding] = []

    for command_use in iter_command_expression_uses(rule):
        expr = command_use.expr
        if expr.head not in SCHEMA_VALIDATED_COMMANDS:
            continue
        if SPLIT_TYPED_COMPARISON_RE.search(expr.source):
            continue
        command = COMMAND_ENTRIES.get(expr.head)
        if not command:
            continue
        args = expression_arg_values(expr)
        if args is None:
            continue

        parameters = command.get("command_parameters", [])
        expected_count = len(parameters)
        if len(args) != expected_count:
            findings.append(
                Finding(
                    expr.line,
                    "command-arity-mismatch",
                    f"{expr.head} expects {expected_count} arguments, got {len(args)}",
                    span=expr.head_span,
                )
            )
            continue

        for index, parameter in enumerate(parameters):
            parameter_name = parameter.get("name", "")
            value = args[index]
            if (
                expr.head in SINGLE_PLAYER_NUMBER_COMMANDS
                and command_use.context == "action"
                and parameter_name == "PlayerNumber"
                and is_any_every_player_wildcard(value)
            ):
                findings.append(
                    finding_for_arg(
                        expr,
                        index,
                        "command-argument-mismatch",
                        f"{expr.head} PlayerNumber {value!r} cannot use any/every wildcard players; use an exact player, my-player-number, scenario-player-#, lobby-player-#, or this-any-* rule variable",
                    )
                )
            if (
                expr.head == "up-find-player-flare"
                and parameter_name == "PlayerNumber"
                and is_flare_unsupported_player_wildcard(value)
            ):
                findings.append(
                    finding_for_arg(
                        expr,
                        index,
                        "command-argument-mismatch",
                        f"{expr.head} PlayerNumber {value!r} is not designed for flare lookup; use any-*, my-player-number, focus-player, target-player, scenario-player-#, lobby-player-#, or loop exact players",
                    )
                )
            family_finding = lint_parameter_family_operand(expr, parameters, parameter_name, value, index)
            if family_finding is not None:
                findings.append(family_finding)
            range_finding = lint_numeric_range_operand(expr, args, parameters, parameter, value, index, constant_values)
            if range_finding is not None:
                findings.append(range_finding)
            direct_id_values = direct_id_values_for_parameter(parameter_name)
            if (
                direct_id_values is not None
                and not (index > 0 and parameters[index - 1].get("name") in {"typeOp", "mathOp", "compareOp"})
                and not is_known_schema_value(value, direct_id_values, defined_constants)
            ):
                findings.append(
                    finding_for_arg(
                        expr,
                        index,
                        "command-argument-mismatch",
                        direct_id_not_documented_message(expr.head, parameter_name, value),
                    )
                )
            if parameter_name == "typeOp" and value not in TYPE_OP_VALUES:
                findings.append(
                    finding_for_arg(
                        expr,
                        index,
                        "command-typed-prefix-mismatch",
                        f"{expr.head} argument {index + 1} uses {value!r}; expected a plain typeOp like c:, g:, or s:, not a math/compare operator",
                    )
                )
            elif parameter_name == "typeOp":
                finding = lint_type_op_operand(expr, args, index)
                if finding is not None:
                    findings.append(finding)
            elif (
                parameter_name == "SearchSource"
                and not is_known_schema_value(value, SEARCH_SOURCE_VALUES, defined_constants)
            ):
                findings.append(
                    finding_for_arg(
                        expr,
                        index,
                        "command-argument-mismatch",
                        f"{expr.head} SearchSource {value!r} should be search-local or search-remote",
                    )
                )
            elif (
                parameter_name == "DUCAction"
                and DUC_ACTION_VALUES
                and not is_known_schema_value(value, DUC_ACTION_VALUES, defined_constants)
            ):
                findings.append(
                    finding_for_arg(
                        expr,
                        index,
                        "command-argument-mismatch",
                        f"{expr.head} DUCAction {value!r} is not documented",
                    )
                )
            elif (
                parameter_name == "Formation"
                and FORMATION_VALUES
                and expr.head not in {"up-target-objects", "up-target-point"}
                and not is_known_schema_value(value, FORMATION_VALUES, defined_constants)
            ):
                findings.append(
                    finding_for_arg(
                        expr,
                        index,
                        "command-argument-mismatch",
                        f"{expr.head} Formation {value!r} is not documented",
                    )
                )
            elif (
                parameter_name == "AttackStance"
                and ATTACK_STANCE_VALUES
                and expr.head not in {"up-target-objects", "up-target-point"}
                and not is_known_schema_value(value, ATTACK_STANCE_VALUES, defined_constants)
            ):
                findings.append(
                    finding_for_arg(
                        expr,
                        index,
                        "command-argument-mismatch",
                        f"{expr.head} AttackStance {value!r} is not documented",
                    )
                )
            elif (
                parameter_name == "compareOp"
                and COMPARE_OP_VALUES
                and not is_known_schema_value(value, COMPARE_OP_VALUES, defined_constants)
            ):
                findings.append(
                    finding_for_arg(
                        expr,
                        index,
                        "command-argument-mismatch",
                        f"{expr.head} compareOp {value!r} is not documented",
                    )
                )
            elif parameter_name == "compareOp":
                finding = lint_type_op_operand(expr, args, index)
                if finding is not None:
                    findings.append(finding)
            elif (
                parameter_name == "mathOp"
                and MATH_OP_VALUES
                and not is_known_schema_value(value, MATH_OP_VALUES, defined_constants)
            ):
                findings.append(
                    finding_for_arg(
                        expr,
                        index,
                        "command-argument-mismatch",
                        f"{expr.head} mathOp {value!r} is not documented",
                    )
                )
            elif parameter_name == "mathOp":
                finding = lint_type_op_operand(expr, args, index)
                if finding is not None:
                    findings.append(finding)
            elif (
                parameter_name == "PlacementType"
                and PLACEMENT_TYPE_VALUES
                and not is_known_schema_value(value, PLACEMENT_TYPE_VALUES, defined_constants)
            ):
                findings.append(
                    finding_for_arg(
                        expr,
                        index,
                        "command-argument-mismatch",
                        f"{expr.head} PlacementType {value!r} is not documented",
                    )
                )
            elif (
                parameter_name == "ResearchState"
                and RESEARCH_STATE_VALUES
                and not is_known_schema_value(value, RESEARCH_STATE_VALUES, defined_constants)
            ):
                findings.append(
                    finding_for_arg(
                        expr,
                        index,
                        "command-argument-mismatch",
                        f"{expr.head} ResearchState {value!r} is not documented",
                    )
                )
            elif parameter_name == "Resource":
                resource_unit_id_commands = {
                    "up-drop-resources",
                    "up-find-resource",
                    "up-gaia-type-count",
                    "up-gaia-type-count-total",
                }
                if expr.head in resource_unit_id_commands:
                    continue
                valid_resources = ESCROW_RESOURCE_VALUES if expr.head in {
                    "release-escrow",
                    "set-escrow-percentage",
                    "up-modify-escrow",
                } else RESOURCE_VALUES
                if valid_resources and not is_known_schema_value(value, valid_resources, defined_constants):
                    findings.append(
                        finding_for_arg(
                            expr,
                            index,
                            "command-argument-mismatch",
                            f"{expr.head} Resource {value!r} is not documented",
                        )
                    )
            elif (
                parameter_name == "Age"
                and AGE_VALUES
                and not is_known_schema_value(value, AGE_VALUES, defined_constants)
            ):
                findings.append(
                    finding_for_arg(
                        expr,
                        index,
                        "command-argument-mismatch",
                        f"{expr.head} Age {value!r} is not documented",
                    )
                )
            elif (
                parameter_name == "Difficulty"
                and DIFFICULTY_VALUES
                and not is_known_schema_value(value, DIFFICULTY_VALUES, defined_constants)
            ):
                findings.append(
                    finding_for_arg(
                        expr,
                        index,
                        "command-argument-mismatch",
                        f"{expr.head} Difficulty {value!r} is not documented",
                    )
                )
            elif (
                parameter_name == "ObjectData"
                and OBJECT_DATA_VALUES
                and not is_known_schema_value(value, OBJECT_DATA_VALUES, defined_constants)
            ):
                findings.append(
                    finding_for_arg(
                        expr,
                        index,
                        "command-argument-mismatch",
                        f"{expr.head} ObjectData {value!r} is not documented",
                    )
                )
            elif (
                parameter_name == "PlayerStance"
                and PLAYER_STANCE_VALUES
                and not is_known_schema_value(value, PLAYER_STANCE_VALUES, defined_constants)
            ):
                findings.append(
                    finding_for_arg(
                        expr,
                        index,
                        "command-argument-mismatch",
                        f"{expr.head} PlayerStance {value!r} is not documented",
                    )
                )
            elif (
                parameter_name == "PositionType"
                and POSITION_TYPE_VALUES
                and not is_known_schema_value(value, POSITION_TYPE_VALUES, defined_constants)
            ):
                findings.append(
                    finding_for_arg(
                        expr,
                        index,
                        "command-argument-mismatch",
                        f"{expr.head} PositionType {value!r} is not documented",
                    )
                )
            elif (
                parameter_name == "TimerState"
                and TIMER_STATE_VALUES
                and not is_known_schema_value(value, TIMER_STATE_VALUES, defined_constants)
            ):
                findings.append(
                    finding_for_arg(
                        expr,
                        index,
                        "command-argument-mismatch",
                        f"{expr.head} TimerState {value!r} is not documented",
                    )
                )
            elif (
                parameter_name == "ObjectList"
                and OBJECT_LIST_VALUES
                and not is_known_schema_value(value, OBJECT_LIST_VALUES, defined_constants)
            ):
                findings.append(
                    finding_for_arg(
                        expr,
                        index,
                        "command-argument-mismatch",
                        f"{expr.head} ObjectList {value!r} is not documented",
                    )
                )
            elif (
                parameter_name == "ObjectStatus"
                and OBJECT_STATUS_VALUES
                and not is_known_schema_value(value, OBJECT_STATUS_VALUES, defined_constants)
            ):
                findings.append(
                    finding_for_arg(
                        expr,
                        index,
                        "command-argument-mismatch",
                        f"{expr.head} ObjectStatus {value!r} is not documented",
                    )
                )
            elif (
                parameter_name == "SearchOrder"
                and SEARCH_ORDER_VALUES
                and not is_known_schema_value(value, SEARCH_ORDER_VALUES, defined_constants)
            ):
                findings.append(
                    finding_for_arg(
                        expr,
                        index,
                        "command-argument-mismatch",
                        f"{expr.head} SearchOrder {value!r} is not documented",
                    )
                )
            elif (
                parameter_name == "Civ"
                and CIV_VALUES
                and not is_known_schema_value(value, CIV_VALUES, defined_constants)
            ):
                findings.append(
                    finding_for_arg(
                        expr,
                        index,
                        "command-argument-mismatch",
                        f"{expr.head} Civ {value!r} is not documented",
                    )
                )
            elif (
                parameter_name == "Commodity"
                and COMMODITY_VALUES
                and not is_known_schema_value(value, COMMODITY_VALUES, defined_constants)
            ):
                findings.append(
                    finding_for_arg(
                        expr,
                        index,
                        "command-argument-mismatch",
                        f"{expr.head} Commodity {value!r} is not documented",
                    )
                )
            elif (
                parameter_name == "FactId"
                and FACT_ID_VALUES
                and not is_known_schema_value(value, FACT_ID_VALUES, defined_constants)
            ):
                findings.append(
                    finding_for_arg(
                        expr,
                        index,
                        "command-argument-mismatch",
                        f"{expr.head} FactId {value!r} is not documented",
                    )
                )
            elif (
                parameter_name == "MapType"
                and MAP_TYPE_VALUES
                and not is_known_schema_value(value, MAP_TYPE_VALUES, defined_constants)
            ):
                message = f"{expr.head} MapType {value!r} is not documented"
                if value in OBSERVED_UNVERIFIED_MAP_TYPE_VALUES:
                    message = (
                        f"{expr.head} MapType {value!r} is observed in community scripts "
                        "but is not present in the local MapType registry; Michi-style maps "
                        "are documented through the RMS ai_info_map_type Michi flag / "
                        "UP-MICHI-STYLE, so verify this fact in game before relying on it"
                    )
                findings.append(
                    finding_for_arg(
                        expr,
                        index,
                        "command-argument-mismatch",
                        message,
                    )
                )
            elif (
                parameter_name == "ProjectileType"
                and PROJECTILE_TYPE_VALUES
                and not is_known_schema_value(value, PROJECTILE_TYPE_VALUES, defined_constants)
            ):
                findings.append(
                    finding_for_arg(
                        expr,
                        index,
                        "command-argument-mismatch",
                        f"{expr.head} ProjectileType {value!r} is not documented",
                    )
                )
            elif (
                parameter_name == "ResourceType"
                and RESOURCE_TYPE_VALUES
                and not is_known_schema_value(value, RESOURCE_TYPE_VALUES, defined_constants)
            ):
                findings.append(
                    finding_for_arg(
                        expr,
                        index,
                        "command-argument-mismatch",
                        f"{expr.head} ResourceType {value!r} is not documented",
                    )
                )
            elif (
                parameter_name == "EventType"
                and EVENT_TYPE_VALUES
                and not is_known_schema_value(value, EVENT_TYPE_VALUES, defined_constants)
            ):
                findings.append(
                    finding_for_arg(
                        expr,
                        index,
                        "command-argument-mismatch",
                        f"{expr.head} EventType {value!r} is not documented",
                    )
                )
            elif (
                parameter_name == "ExploredState"
                and EXPLORED_STATE_VALUES
                and not is_known_schema_value(value, EXPLORED_STATE_VALUES, defined_constants)
            ):
                findings.append(
                    finding_for_arg(
                        expr,
                        index,
                        "command-argument-mismatch",
                        f"{expr.head} ExploredState {value!r} is not documented",
                    )
                )
            elif (
                parameter_name == "FindPlayerMethod"
                and FIND_PLAYER_METHOD_VALUES
                and not is_known_schema_value(value, FIND_PLAYER_METHOD_VALUES, defined_constants)
            ):
                findings.append(
                    finding_for_arg(
                        expr,
                        index,
                        "command-argument-mismatch",
                        f"{expr.head} FindPlayerMethod {value!r} is not documented",
                    )
                )
            elif (
                parameter_name == "GameType"
                and GAME_TYPE_VALUES
                and not is_known_schema_value(value, GAME_TYPE_VALUES, defined_constants)
            ):
                findings.append(
                    finding_for_arg(
                        expr,
                        index,
                        "command-argument-mismatch",
                        f"{expr.head} GameType {value!r} is not documented",
                    )
                )
            elif (
                parameter_name == "GroupType"
                and GROUP_TYPE_VALUES
                and not is_known_schema_value(value, GROUP_TYPE_VALUES, defined_constants)
            ):
                findings.append(
                    finding_for_arg(
                        expr,
                        index,
                        "command-argument-mismatch",
                        f"{expr.head} GroupType {value!r} is not documented",
                    )
                )
            elif (
                parameter_name == "IdleType"
                and IDLE_TYPE_VALUES
                and not is_known_schema_value(value, IDLE_TYPE_VALUES, defined_constants)
            ):
                findings.append(
                    finding_for_arg(
                        expr,
                        index,
                        "command-argument-mismatch",
                        f"{expr.head} IdleType {value!r} is not documented",
                    )
                )
            elif (
                parameter_name == "MapSize"
                and MAP_SIZE_VALUES
                and not is_known_schema_value(value, MAP_SIZE_VALUES, defined_constants)
            ):
                findings.append(
                    finding_for_arg(
                        expr,
                        index,
                        "command-argument-mismatch",
                        f"{expr.head} MapSize {value!r} is not documented",
                    )
                )
            elif (
                parameter_name == "PriorityType"
                and PRIORITY_TYPE_VALUES
                and not is_known_schema_value(value, PRIORITY_TYPE_VALUES, defined_constants)
            ):
                findings.append(
                    finding_for_arg(
                        expr,
                        index,
                        "command-argument-mismatch",
                        f"{expr.head} PriorityType {value!r} is not documented",
                    )
                )
            elif (
                parameter_name == "ScoutMethod"
                and SCOUT_METHOD_VALUES
                and not is_known_schema_value(value, SCOUT_METHOD_VALUES, defined_constants)
            ):
                findings.append(
                    finding_for_arg(
                        expr,
                        index,
                        "command-argument-mismatch",
                        f"{expr.head} ScoutMethod {value!r} is not documented",
                    )
                )
            elif (
                parameter_name == "StartingResources"
                and STARTING_RESOURCES_VALUES
                and not is_known_schema_value(value, STARTING_RESOURCES_VALUES, defined_constants)
            ):
                findings.append(
                    finding_for_arg(
                        expr,
                        index,
                        "command-argument-mismatch",
                        f"{expr.head} StartingResources {value!r} is not documented",
                    )
                )
            elif (
                parameter_name == "SubGameType"
                and SUB_GAME_TYPE_VALUES
                and not is_known_schema_value(value, SUB_GAME_TYPE_VALUES, defined_constants)
            ):
                findings.append(
                    finding_for_arg(
                        expr,
                        index,
                        "command-argument-mismatch",
                        f"{expr.head} SubGameType {value!r} is not documented",
                    )
                )
            elif (
                parameter_name == "VictoryCondition"
                and VICTORY_CONDITION_VALUES
                and not is_known_schema_value(value, VICTORY_CONDITION_VALUES, defined_constants)
            ):
                findings.append(
                    finding_for_arg(
                        expr,
                        index,
                        "command-argument-mismatch",
                        f"{expr.head} VictoryCondition {value!r} is not documented",
                    )
                )
            elif (
                parameter_name == "ActionId"
                and ACTION_ID_VALUES
                and not is_known_schema_value(value, ACTION_ID_VALUES, defined_constants)
            ):
                findings.append(
                    finding_for_arg(
                        expr,
                        index,
                        "command-argument-mismatch",
                        f"{expr.head} ActionId {value!r} is not documented",
                    )
                )
            elif (
                parameter_name == "AttrId"
                and ATTR_ID_VALUES
                and not is_known_schema_value(value, ATTR_ID_VALUES, defined_constants)
            ):
                findings.append(
                    finding_for_arg(
                        expr,
                        index,
                        "command-argument-mismatch",
                        f"{expr.head} AttrId {value!r} is not documented",
                    )
                )
            elif (
                parameter_name == "DiffParameterId"
                and DIFF_PARAMETER_ID_VALUES
                and not is_known_schema_value(value, DIFF_PARAMETER_ID_VALUES, defined_constants)
            ):
                findings.append(
                    finding_for_arg(
                        expr,
                        index,
                        "command-argument-mismatch",
                        f"{expr.head} DiffParameterId {value!r} is not documented",
                    )
                )
            elif (
                parameter_name == "EffectId"
                and EFFECT_ID_VALUES
                and not is_known_schema_value(value, EFFECT_ID_VALUES, defined_constants)
            ):
                findings.append(
                    finding_for_arg(
                        expr,
                        index,
                        "command-argument-mismatch",
                        f"{expr.head} EffectId {value!r} is not documented",
                    )
                )
            elif (
                parameter_name == "OrderId"
                and ORDER_ID_VALUES
                and not is_known_schema_value(value, ORDER_ID_VALUES, defined_constants)
            ):
                findings.append(
                    finding_for_arg(
                        expr,
                        index,
                        "command-argument-mismatch",
                        f"{expr.head} OrderId {value!r} is not documented",
                    )
                )
            elif (
                parameter_name == "Terrain"
                and parameter.get("type") != "Goal"
                and TERRAIN_VALUES
                and not is_known_schema_value(value, TERRAIN_VALUES, defined_constants)
            ):
                findings.append(
                    finding_for_arg(
                        expr,
                        index,
                        "command-argument-mismatch",
                        f"{expr.head} Terrain {value!r} is not documented",
                    )
                )
            elif (
                parameter_name == "WallId"
                and WALL_ID_VALUES
                and not is_known_schema_value(value, WALL_ID_VALUES, defined_constants)
            ):
                findings.append(
                    finding_for_arg(
                        expr,
                        index,
                        "command-argument-mismatch",
                        f"{expr.head} WallId {value!r} is not documented",
                    )
                )
            elif (
                parameter.get("type") == "Text"
                and value not in defined_constants
                and not (value.startswith('"') and value.endswith('"'))
            ):
                findings.append(
                    finding_for_arg(
                        expr,
                        index,
                        "command-argument-mismatch",
                        f"{expr.head} {parameter_name} {value!r} should be quoted text",
                    )
                )

    return findings


def command_type_allows_context(command_type: str, context: str) -> bool:
    if context == "fact":
        return "Fact" in command_type
    if context == "action":
        return "Action" in command_type
    return True


ACTION_SUGGESTIONS_FOR_FACTS = {
    "can-build": "build",
    "can-build-with-escrow": "build",
    "can-research": "research",
    "can-research-with-escrow": "research after releasing escrow, or up-research with an escrow-state goal",
    "can-train": "train",
    "can-train-with-escrow": "train after releasing escrow, or up-train with an escrow-state goal",
    "up-can-build": "up-build",
    "up-can-research": "up-research",
    "up-can-train": "up-train",
}


def role_mismatch_message(symbol: str, command_type: str, context: str) -> str:
    article = "an" if context[:1] in {"a", "e", "i", "o", "u"} else "a"
    message = f"{symbol!r} is documented as {command_type}, but is used in {article} {context} context"
    if context == "action" and symbol in ACTION_SUGGESTIONS_FOR_FACTS:
        message += f"; likely intended action: {ACTION_SUGGESTIONS_FOR_FACTS[symbol]}"
    return message


def lint_command_roles(rule: object) -> list[Finding]:
    findings: list[Finding] = []
    fact_exprs = getattr(rule, "fact_exprs", ())
    action_exprs = getattr(rule, "action_exprs", ())

    def walk_fact(expr: Expression) -> None:
        if expr.head not in FACT_LOGICAL_HEADS:
            command_type = COMMAND_TYPES.get(expr.head)
            if command_type and not command_type_allows_context(command_type, "fact"):
                findings.append(
                    Finding(
                        expr.line,
                        "command-role-mismatch",
                        role_mismatch_message(expr.head, command_type, "fact"),
                        span=expr.head_span,
                    )
                )
        for arg in expr.args:
            if isinstance(arg, Expression):
                walk_fact(arg)

    for expr in fact_exprs:
        walk_fact(expr)

    for expr in action_exprs:
        symbol = expr.head
        command_type = COMMAND_TYPES.get(symbol)
        if command_type and not command_type_allows_context(command_type, "action"):
            findings.append(
                Finding(
                    expr.line,
                    "command-role-mismatch",
                    role_mismatch_message(symbol, command_type, "action"),
                    span=expr.head_span,
                )
            )
    return findings


def lint_logical_operator_arity(rule: object) -> list[Finding]:
    findings: list[Finding] = []
    facts = getattr(rule, "facts", ())
    fact_lines = getattr(rule, "fact_lines", ()) or (getattr(rule, "start_line"),) * len(facts)
    fact_exprs = getattr(rule, "fact_exprs", ())
    expected_counts = {
        "not": 1,
        "and": 2,
        "or": 2,
        "nand": 2,
        "nor": 2,
        "xor": 2,
        "xnor": 2,
    }

    def walk(expr: Expression) -> None:
        if expr.head in expected_counts:
            if count_code_parens(expr.source) != 0:
                return
            child_fact_count = sum(1 for arg in expr.args if isinstance(arg, Expression))
            expected = expected_counts[expr.head]
            if child_fact_count != expected:
                facts_label = "fact" if expected == 1 else "facts"
                findings.append(
                    Finding(
                        expr.line,
                        "logical-operator-arity-mismatch",
                        f"{expr.head} expects {expected} child {facts_label}, got {child_fact_count}",
                        span=expr.head_span,
                    )
                )
        for arg in expr.args:
            if isinstance(arg, Expression):
                walk(arg)

    for expr in fact_exprs:
        walk(expr)

    stack: list[dict[str, object]] = []
    for fact, line in zip(facts, fact_lines):
        symbol = first_symbol(fact)
        balance_delta = count_code_parens(fact)
        opens_logical = symbol in expected_counts and balance_delta > 0
        is_complete_expr = fact.strip().startswith("(") and balance_delta == 0

        if opens_logical:
            if stack:
                stack[-1]["count"] = int(stack[-1]["count"]) + 1
            stack.append(
                {
                    "head": symbol,
                    "line": line,
                    "count": 0,
                    "balance": balance_delta,
                }
            )
            continue

        if is_complete_expr and stack:
            stack[-1]["count"] = int(stack[-1]["count"]) + 1
            continue

        if balance_delta < 0 and stack:
            stack[-1]["balance"] = int(stack[-1]["balance"]) + balance_delta
            while stack and int(stack[-1]["balance"]) <= 0:
                frame = stack.pop()
                head = str(frame["head"])
                expected = expected_counts[head]
                child_fact_count = int(frame["count"])
                if child_fact_count != expected:
                    facts_label = "fact" if expected == 1 else "facts"
                    findings.append(
                        Finding(
                            int(frame["line"]),
                            "logical-operator-arity-mismatch",
                            f"{head} expects {expected} child {facts_label}, got {child_fact_count}",
                        )
                    )
                if stack:
                    stack[-1]["balance"] = int(stack[-1]["balance"]) + int(frame["balance"])
    return findings


def lint_unsafe_set_target_objects(rules: tuple[object, ...]) -> list[Finding]:
    search_ready = {"search-local": False, "search-remote": False}
    findings: list[Finding] = []

    def apply_search_reset(expr: str) -> None:
        nonlocal search_ready
        tokens = expression_tokens(expr)
        if len(tokens) < 5:
            search_ready = {"search-local": False, "search-remote": False}
            return
        if tokens[2] == "1":
            search_ready["search-local"] = False
        if tokens[4] == "1":
            search_ready["search-remote"] = False

    for rule in rules:
        facts = getattr(rule, "facts")
        actions = getattr(rule, "actions")
        fact_lines = getattr(rule, "fact_lines", ()) or (getattr(rule, "start_line"),) * len(facts)
        action_lines = getattr(rule, "action_lines", ()) or (getattr(rule, "start_line"),) * len(actions)

        for fact, _line in expressions_with_lines(facts, fact_lines, getattr(rule, "start_line")):
            symbol = first_symbol(fact)
            tokens = expression_tokens(fact)
            if symbol == "up-full-reset-search":
                search_ready = {"search-local": False, "search-remote": False}
            elif symbol == "up-reset-search":
                apply_search_reset(fact)
            elif symbol == "up-find-local":
                search_ready["search-local"] = True
            elif symbol == "up-find-remote":
                search_ready["search-remote"] = True
            elif symbol == "up-set-group":
                if len(tokens) > 1 and tokens[1] in search_ready:
                    search_ready[tokens[1]] = True
            elif symbol == "up-set-target-object":
                if len(tokens) > 1 and tokens[1] in search_ready:
                    search_ready[tokens[1]] = True

        for action, line in expressions_with_lines(actions, action_lines, getattr(rule, "start_line")):
            symbol = first_symbol(action)
            tokens = expression_tokens(action)
            if symbol == "up-full-reset-search":
                search_ready = {"search-local": False, "search-remote": False}
                continue
            if symbol == "up-reset-search":
                apply_search_reset(action)
                continue
            if symbol == "up-find-local":
                search_ready["search-local"] = True
                continue
            if symbol == "up-find-remote":
                search_ready["search-remote"] = True
                continue
            if symbol == "up-set-group":
                if len(tokens) > 1 and tokens[1] in search_ready:
                    search_ready[tokens[1]] = True
                continue
            if symbol != "up-set-target-object" or len(tokens) < 2:
                continue

            source = tokens[1]
            if source not in search_ready:
                continue
            if not search_ready[source]:
                findings.append(
                    Finding(
                        line,
                        "unsafe-set-target-object",
                        f"{symbol} uses {source} before retained search state has rebuilt that list",
                    )
                )
    return findings


def lint_file(
    path: str | Path,
    extra_constants: set[str] | None = None,
    extra_constant_values: dict[str, int] | None = None,
    *,
    allow_raw_loads: bool = False,
    profile: str = "default",
    suppress_codes: set[str] | None = None,
) -> list[Finding]:
    script_path = Path(path)
    source_suppressions = source_suppression_map(script_path)

    def apply_suppressions(raw_findings: list[Finding]) -> list[Finding]:
        suppressed = set(LINT_PROFILE_SUPPRESSIONS.get(profile, set()))
        if suppress_codes:
            suppressed.update(suppress_codes)
        return [
            finding
            for finding in raw_findings
            if finding.code not in suppressed and not source_suppresses_finding(source_suppressions, finding)
        ]

    line_confidence = {
        source_line.number: source_line.confidence
        for source_line in active_source_lines(script_path)
    }

    def with_line_confidence(raw_findings: list[Finding]) -> list[Finding]:
        return [
            Finding(
                finding.line,
                finding.code,
                finding.message,
                line_confidence.get(finding.line, finding.confidence),
                finding.span,
            )
            for finding in raw_findings
        ]

    if script_path.suffix.lower() == ".xs":
        return apply_suppressions(with_line_confidence(lint_xs_file(script_path)))

    findings: list[Finding] = []
    pre_parse_findings: list[Finding] = []
    pre_parse_findings.extend(
        Finding(
            issue.line,
            issue.code,
            issue.message,
            issue.confidence,
        )
        for issue in preprocessor_issues(script_path)
    )
    pre_parse_findings.extend(with_line_confidence(lint_line_length(script_path)))
    pre_parse_findings.extend(with_line_confidence(lint_malformed_defconst(script_path)))
    pre_parse_findings.extend(with_line_confidence(lint_defconst_numeric_range(script_path)))
    pre_parse_findings.extend(with_line_confidence(lint_malformed_load_directives(script_path)))
    pre_parse_findings.extend(with_line_confidence(lint_malformed_load_random_directives(script_path)))
    pre_parse_findings.extend(with_line_confidence(lint_builtin_defconst_shadow(script_path)))
    pre_parse_findings.extend(with_line_confidence(lint_defconst_conflicts(script_path)))
    pre_parse_findings.extend(with_line_confidence(lint_defconst_alias_cycles(script_path)))
    pre_parse_findings.extend(with_line_confidence(lint_defrule_structure(script_path)))
    pre_parse_findings.extend(with_line_confidence(lint_parenthesis_balance(script_path)))
    fatal_findings = [finding for finding in pre_parse_findings if finding.code in FATAL_PRE_PARSE_CODES]
    if any(finding.code not in RECOVERABLE_STRUCTURE_CODES for finding in fatal_findings):
        findings.extend(pre_parse_findings)
        return apply_suppressions(findings)

    visible_pre_parse_findings = apply_suppressions(pre_parse_findings)
    if profile == "corpus" and pre_parse_findings and not visible_pre_parse_findings:
        return []

    findings.extend(pre_parse_findings)

    script = parse_script(script_path)
    defined_constants = set(script.constant_names)
    if extra_constants:
        defined_constants.update(extra_constants)
    constant_values = dict(script.constants)
    if extra_constant_values:
        constant_values.update(extra_constant_values)

    findings.extend(with_line_confidence(lint_load_random_plus_weight_behavior(script_path)))

    for source_line in active_source_lines(script_path):
        index = source_line.number
        raw_line = source_line.text
        code = strip_comment(raw_line)
        if RAW_LOAD_RE.match(code) and VALID_SOURCE_LOAD_RE.match(code) and not allow_raw_loads:
            findings.append(
                Finding(
                    index,
                    "raw-load-in-per",
                    "#load is not valid inside installed .per files; assemble components before install",
                    source_line.confidence,
                )
            )

    for rule in script.rules:
        rule_confidence = getattr(rule, "confidence", "definite")
        element_count = count_rule_elements(rule)
        if element_count > 32:
            findings.append(
                Finding(
                    rule.start_line,
                    "rule-too-long",
                    f"rule has {element_count} elements; DE allows at most 32 facts/actions/logical operators per rule",
                    rule_confidence,
                )
            )

        if not rule.actions:
            findings.append(
                Finding(
                    rule.start_line,
                    "empty-action",
                    "rule has no actions after =>",
                    rule_confidence,
                )
            )

        if not rule.facts:
            findings.append(
                Finding(
                    rule.start_line,
                    "empty-fact",
                    "rule has no facts before =>",
                    rule_confidence,
                )
            )

        findings.extend(apply_confidence(lint_livestock_point_default(rule), rule_confidence))
        findings.extend(apply_confidence(lint_up_build_place_point_escrow(rule), rule_confidence))
        findings.extend(apply_confidence(lint_command_roles(rule), rule_confidence))
        findings.extend(apply_confidence(lint_logical_operator_arity(rule), rule_confidence))
        findings.extend(apply_confidence(lint_command_schema(rule, defined_constants, constant_values), rule_confidence))

        if not any(action.startswith("(disable-self") for action in rule.actions):
            chat_lines = [
                action_line
                for action, action_line in expressions_with_lines(rule.actions, rule.action_lines, rule.start_line)
                if first_symbol(action) in {"chat-to-all", "chat-to-player"}
            ]
            has_guard = any(
                first_symbol(fact) in {"goal", "timer-triggered", "up-timer-status"}
                for fact in rule.facts
            )
            if chat_lines and not has_guard:
                findings.append(
                    Finding(
                        chat_lines[0],
                        "repeat-chat",
                        "chatting rule should usually disable itself or be guarded",
                        rule_confidence,
                    )
                )

        for action, action_line in expressions_with_lines(rule.actions, rule.action_lines, rule.start_line):
            symbol = first_symbol(action)
            if symbol == "set-goal" and len(action.rstrip(")").split()) < 3:
                findings.append(
                    Finding(
                        action_line,
                        "bad-set-goal",
                        "set-goal requires a goal id and value",
                        rule_confidence,
                    )
                )
            findings.extend(apply_confidence(lint_strategic_number_identifier(action_line, action, defined_constants), rule_confidence))
            findings.extend(apply_confidence(lint_typed_constants(action_line, action, defined_constants), rule_confidence))
            findings.extend(apply_confidence(lint_common_identifier_uses(action_line, action, defined_constants), rule_confidence))
            findings.extend(apply_confidence(lint_multi_goal_writer(action_line, action, constant_values), rule_confidence))
            findings.extend(apply_confidence(lint_up_get_point_position_identifier(action_line, action, defined_constants), rule_confidence))
            findings.extend(apply_confidence(lint_up_can_build_zero_escrow(action_line, action), rule_confidence))
            findings.extend(apply_confidence(lint_split_typed_comparison(action_line, action), rule_confidence))

        for fact, fact_line in expressions_with_lines(rule.facts, rule.fact_lines, rule.start_line):
            findings.extend(apply_confidence(lint_strategic_number_identifier(fact_line, fact, defined_constants), rule_confidence))
            findings.extend(apply_confidence(lint_typed_constants(fact_line, fact, defined_constants), rule_confidence))
            findings.extend(apply_confidence(lint_common_identifier_uses(fact_line, fact, defined_constants), rule_confidence))
            findings.extend(apply_confidence(lint_multi_goal_writer(fact_line, fact, constant_values), rule_confidence))
            findings.extend(apply_confidence(lint_up_get_point_position_identifier(fact_line, fact, defined_constants), rule_confidence))
            findings.extend(apply_confidence(lint_up_can_build_zero_escrow(fact_line, fact), rule_confidence))
            findings.extend(apply_confidence(lint_split_typed_comparison(fact_line, fact), rule_confidence))

    findings.extend(with_line_confidence(lint_unscoped_duc_targets(script.rules)))
    findings.extend(with_line_confidence(lint_unsafe_set_target_objects(script.rules)))

    return apply_suppressions(findings)
    "stone-amount",
    "idle-farm-count",
    "military-population",
    "population",
    "population-cap",
