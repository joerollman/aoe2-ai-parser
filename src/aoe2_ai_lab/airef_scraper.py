from __future__ import annotations

from dataclasses import asdict, dataclass, replace
import html
import json
from pathlib import Path
import re
import shutil
import time


COMMANDS_INDEX_URL = "https://airef.github.io/commands/commands-index.html"
COMMANDS_DETAILS_URL = "https://airef.github.io/commands/commands-details.html"
PARAMETERS_DETAILS_URL = "https://airef.github.io/parameters/parameters-details.html"
STRATEGIC_NUMBERS_DETAILS_URL = "https://airef.github.io/strategic-numbers/sn-details.html"
EXTRACTED_DIR = Path("docs") / "extracted"
INVENTORY_DIR = EXTRACTED_DIR / "inventories"
RAW_DIR = EXTRACTED_DIR / "raw"
SOURCE_DIR = EXTRACTED_DIR / "sources"
DEFAULT_SOURCE_DIR = SOURCE_DIR / "airef-source"
RAW_AOE2DE_DIR = RAW_DIR / "aoe2de"
RAW_XS_DIR = RAW_DIR / "xs"
RAW_RMS_DIR = RAW_DIR / "rms"

LOCAL_DE_STRATEGIC_NUMBER_SUPPLEMENTS = [
    "sn-minimum-tasked-units",
    "sn-maximum-tasked-units",
]
NON_DE_SN_REPLACEMENT = "archived-non-de-strategic-number"


@dataclass(frozen=True)
class ScrapedXsFunction:
    name: str
    offset: int | None
    signature: str
    return_type: str
    parameters: list[str]
    description: str
    category: str
    ai_context_status: str
    source: str
    notes: str
    contexts: list[str]
    examples: list[str]
    secondary_sources: list[str]
    prototype: str


@dataclass(frozen=True)
class ScrapedRmsFixture:
    name: str
    path: str
    title: str
    summary: str
    map_type: str
    create_objects: list[str]
    sections: list[str]
    tags: list[str]
    use_cases: list[str]
    recommended_probe: str


@dataclass(frozen=True)
class ScrapedXsConstant:
    name: str
    category: str
    value_type: str
    value: str
    description: str
    source: str


@dataclass(frozen=True)
class ScrapedRmsTopic:
    name: str
    level: int
    path: list[str]
    summary: str
    source: str


def collapse_ws(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug or "item"


def js_unquote(text: str) -> str:
    return bytes(text, "utf-8").decode("unicode_escape")


def split_top_level(text: str, delimiter: str = "+") -> list[str]:
    parts: list[str] = []
    start = 0
    depth_paren = 0
    depth_bracket = 0
    depth_brace = 0
    in_string = False
    escaped = False
    for index, char in enumerate(text):
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
            continue
        if char == "(":
            depth_paren += 1
        elif char == ")":
            depth_paren -= 1
        elif char == "[":
            depth_bracket += 1
        elif char == "]":
            depth_bracket -= 1
        elif char == "{":
            depth_brace += 1
        elif char == "}":
            depth_brace -= 1
        elif (
            char == delimiter
            and depth_paren == 0
            and depth_bracket == 0
            and depth_brace == 0
        ):
            parts.append(text[start:index].strip())
            start = index + 1
    parts.append(text[start:].strip())
    return [part for part in parts if part]


def split_js_array_items(text: str) -> list[str]:
    items: list[str] = []
    start = 0
    depth_paren = 0
    depth_bracket = 0
    depth_brace = 0
    in_string = False
    escaped = False
    for index, char in enumerate(text):
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
            continue
        if char == "(":
            depth_paren += 1
        elif char == ")":
            depth_paren -= 1
        elif char == "[":
            depth_bracket += 1
        elif char == "]":
            depth_bracket -= 1
        elif char == "{":
            depth_brace += 1
        elif char == "}":
            depth_brace -= 1
        elif (
            char == ","
            and depth_paren == 0
            and depth_bracket == 0
            and depth_brace == 0
        ):
            items.append(text[start:index].strip())
            start = index + 1
    tail = text[start:].strip()
    if tail:
        items.append(tail)
    return items


def parse_assignment_value(source: str, prefix: str) -> str | None:
    marker = f"{prefix} = "
    start = source.find(marker)
    if start == -1:
        return None
    index = start + len(marker)
    depth_paren = 0
    depth_bracket = 0
    depth_brace = 0
    in_string = False
    escaped = False
    while index < len(source):
        char = source[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            index += 1
            continue
        if char == '"':
            in_string = True
        elif char == "(":
            depth_paren += 1
        elif char == ")":
            depth_paren -= 1
        elif char == "[":
            depth_bracket += 1
        elif char == "]":
            depth_bracket -= 1
        elif char == "{":
            depth_brace += 1
        elif char == "}":
            depth_brace -= 1
        elif char in ";," and depth_paren == 0 and depth_bracket == 0 and depth_brace == 0:
            lookahead = index + 1
            while lookahead < len(source) and source[lookahead].isspace():
                lookahead += 1
            if char == ";" or lookahead >= len(source) or source[lookahead] in "/ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_":
                return source[start + len(marker):index].strip()
        elif char in "\r\n" and depth_paren == 0 and depth_bracket == 0 and depth_brace == 0:
            lookahead = index + 1
            while lookahead < len(source) and source[lookahead].isspace():
                lookahead += 1
            if re.match(r"[A-Za-z_]\w*\.", source[lookahead:]):
                return source[start + len(marker):index].strip()
        index += 1
    return None


def resolve_symbol_name(symbol: str, command_names: dict[str, str]) -> str:
    if symbol in command_names:
        return command_names[symbol]
    return symbol


def evaluate_js_expression(expr: str, command_names: dict[str, str]) -> str:
    parts = split_top_level(expr, "+")
    resolved: list[str] = []
    for part in parts:
        item = part.strip()
        if not item:
            continue
        if item.startswith('"') and item.endswith('"'):
            resolved.append(js_unquote(item[1:-1]))
            continue
        match = re.fullmatch(r"([A-Za-z_]\w*)\.getLink\((.*?)\)", item)
        if match:
            resolved.append(resolve_symbol_name(match.group(1), command_names))
            continue
        resolved.append(resolve_symbol_name(item, command_names))
    return collapse_ws("".join(resolved))


def parse_string_array(expr: str, command_names: dict[str, str]) -> list[str]:
    body = expr.strip()
    if body.startswith("[") and body.endswith("]"):
        body = body[1:-1].strip()
    if not body:
        return []
    items = split_js_array_items(body)
    values: list[str] = []
    for item in items:
        clean = item.strip()
        if clean.startswith('"') and clean.endswith('"'):
            values.append(js_unquote(clean[1:-1]))
        else:
            values.append(resolve_symbol_name(clean, command_names))
    return values


def parse_object_array(expr: str, command_names: dict[str, str]) -> list[dict[str, str]]:
    body = expr.strip()
    if body.startswith("[") and body.endswith("]"):
        body = body[1:-1].strip()
    if not body:
        return []
    objects = re.findall(r"\{(.*?)\}", body, re.DOTALL)
    parsed: list[dict[str, str]] = []
    for obj in objects:
        entry: dict[str, str] = {}
        for match in re.finditer(r"(\w+)\s*:\s*(.*?)(?:,\s*(?=\w+\s*:)|$)", obj, re.DOTALL):
            key = match.group(1)
            value = match.group(2).strip()
            if key == "name":
                if value.startswith('"') and value.endswith('"'):
                    entry[key] = js_unquote(value[1:-1])
                else:
                    entry[key] = evaluate_js_expression(value, command_names)
            else:
                entry[key] = evaluate_js_expression(value, command_names)
        if entry:
            parsed.append(entry)
    return parsed


def build_syntax(command_name: str, command_type: str, parameters: list[dict[str, str]]) -> str:
    if command_type == "Other" and command_name in {
        "#load-if-defined",
        "#load-if-not-defined",
        "#else",
        "#end-if",
    }:
        if parameters:
            return f"{command_name} " + " ".join(f"<{param['name']}>" for param in parameters)
        return command_name
    joined = " ".join(f"<{param['name']}>" for param in parameters)
    return f"({command_name}{(' ' + joined) if joined else ''})"


def strip_html(text: str) -> str:
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</p>\s*<p>", "\n\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    return collapse_ws(text)


@dataclass(frozen=True)
class ScrapedCommand:
    name: str
    url: str
    source_link_text: str
    slug: str
    description: str
    syntax: str
    info_table: dict[str, str]
    headings: list[dict[str, str]]
    code_blocks: list[str]
    status: str
    short_description: str
    command_parameters: list[dict[str, str]]
    examples: list[dict[str, str]]
    command_category: list[str]
    related_commands: list[str]
    related_strategic_numbers: list[str]
    command_type: str
    command_version: str
    complexity: str
    html_path: str | None = None


@dataclass(frozen=True)
class ScrapedParameter:
    name: str
    url: str
    slug: str
    description: str
    short_description: str
    range: str
    version: str
    es_param_name: str
    related_parameters: list[str]
    prefix_types: list[dict[str, str]]
    operator_types: list[dict[str, str]]
    value_list: list[dict[str, str]]
    wildcard_parameters: list[dict[str, str]]
    rule_variables: list[dict[str, str]]
    used_in_commands: list[str]
    status: str


@dataclass(frozen=True)
class ScrapedStrategicNumber:
    name: str
    url: str
    slug: str
    description: str
    short_description: str
    sn_id: int | str
    default_value: int | str
    required_range: str
    allowable_range: str
    category: str
    effective: int | str
    network: int | str
    defined: int | str
    available: int | str
    version: str
    supported_versions: list[str]
    aoe: int | str
    aoc: int | str
    up: int | str
    de: int | str
    aoe1_name: str
    linked_sns: list[str]
    related_sns: list[str]
    status: str


@dataclass(frozen=True)
class ValueFamily:
    parameter_name: str
    family_type: str
    entry_count: int
    description: str
    entries: list[dict[str, object]]


@dataclass(frozen=True)
class ScrapedObject:
    name: str
    ai_name: str
    line: str
    object_id: int | str
    object_class: str
    cmd_id: str
    building: str
    group_name: str
    age: int | str
    dead_unit: str
    projectile: str
    versions: dict[str, int]
    dataset: str
    notes: str
    status: str


@dataclass(frozen=True)
class ScrapedTech:
    name: str
    ai_name: str
    tech_id: int | str
    building: str
    group_name: str
    age: int | str
    civilization: str
    cost: str
    time: int | str
    description: str
    versions: dict[str, int]
    dataset: str
    notes: str
    status: str


def parse_commands_js(source: str) -> list[ScrapedCommand]:
    constructor_matches = list(
        re.finditer(
            r'var\s+(\w+)\s*=\s*new\s+Command\("([^"]+)","([^"]+)","([^"]+)"\);',
            source,
        )
    )
    command_names = {match.group(1): match.group(2) for match in constructor_matches}
    commands: list[ScrapedCommand] = []

    for match in constructor_matches:
        symbol = match.group(1)
        name = match.group(2)
        command_type = match.group(3)
        command_version = match.group(4)
        short_description_expr = parse_assignment_value(source, f"{symbol}.shortDescription")
        description_expr = parse_assignment_value(source, f"{symbol}.description")
        parameters_expr = parse_assignment_value(source, f"{symbol}.commandParameters")
        examples_expr = parse_assignment_value(source, f"{symbol}.example")
        category_expr = parse_assignment_value(source, f"{symbol}.commandCategory")
        related_commands_expr = parse_assignment_value(source, f"{symbol}.relatedCommands")
        related_sns_expr = parse_assignment_value(source, f"{symbol}.relatedSNs")
        complexity_expr = parse_assignment_value(source, f"{symbol}.complexity")

        short_description = (
            evaluate_js_expression(short_description_expr, command_names)
            if short_description_expr
            else ""
        )
        raw_description = (
            evaluate_js_expression(description_expr, command_names)
            if description_expr
            else short_description
        )
        description = strip_html(raw_description)
        parameters = parse_object_array(parameters_expr, command_names) if parameters_expr else []
        examples = parse_object_array(examples_expr, command_names) if examples_expr else []
        command_category = parse_string_array(category_expr, command_names) if category_expr else []
        related_commands = (
            parse_string_array(related_commands_expr, command_names) if related_commands_expr else []
        )
        related_sns = parse_string_array(related_sns_expr, command_names) if related_sns_expr else []
        complexity = (
            evaluate_js_expression(complexity_expr, command_names).strip('"')
            if complexity_expr
            else ""
        )
        syntax = build_syntax(name, command_type, parameters)
        info_table = {
            "Command Type": command_type,
            "Version Introduced": command_version,
            "Complexity": complexity,
        }
        if command_category:
            info_table["Category"] = ", ".join(command_category)
        if related_commands:
            info_table["Related Commands"] = ", ".join(related_commands)
        if related_sns:
            info_table["Related Strategic Numbers"] = ", ".join(related_sns)

        commands.append(
            ScrapedCommand(
                name=name,
                url=f"{COMMANDS_DETAILS_URL}#{name}",
                source_link_text=name,
                slug=slugify(name),
                description=description,
                syntax=syntax,
                info_table=info_table,
                headings=[
                    {"level": "h3", "text": "Syntax"},
                    {"level": "h3", "text": "Description"},
                    {"level": "h3", "text": "Info"},
                ],
                code_blocks=[example.get("data", "") for example in examples if example.get("data")][:12],
                status="scraped",
                short_description=short_description,
                command_parameters=parameters,
                examples=examples,
                command_category=command_category,
                related_commands=related_commands,
                related_strategic_numbers=related_sns,
                command_type=command_type,
                command_version=command_version,
                complexity=complexity,
            )
        )
    return commands


def parse_parameters_js(source: str) -> list[ScrapedParameter]:
    constructor_matches = list(
        re.finditer(
            r'var\s+(p\w+)\s*=\s*new\s+Parameter\("([^"]+)","([^"]*)"(?:,"([^"]*)")?\);',
            source,
        )
    )
    parameter_symbols = {match.group(1): match.group(2) for match in constructor_matches}
    command_symbols = {
        match.group(1): match.group(2)
        for match in re.finditer(r'var\s+(\w+)\s*=\s*new\s+Command\("([^"]+)"', source)
    }
    symbol_names = {**command_symbols, **parameter_symbols}

    parameters: list[ScrapedParameter] = []
    for match in constructor_matches:
        symbol = match.group(1)
        name = match.group(2)
        version = match.group(3)
        es_param_name = html.unescape(js_unquote(match.group(4) or ""))
        short_expr = parse_assignment_value(source, f"{symbol}.shortDescription")
        desc_expr = parse_assignment_value(source, f"{symbol}.description")
        range_expr = parse_assignment_value(source, f"{symbol}.range")
        related_expr = parse_assignment_value(source, f"{symbol}.relatedParams")
        prefix_expr = parse_assignment_value(source, f"{symbol}.prefixTypes")
        operator_expr = parse_assignment_value(source, f"{symbol}.operatorTypes")
        value_list_expr = parse_assignment_value(source, f"{symbol}.valueList")
        wildcard_expr = parse_assignment_value(source, f"{symbol}.wildcardParam")
        rule_vars_expr = parse_assignment_value(source, f"{symbol}.ruleVariables")

        short_description = evaluate_js_expression(short_expr, symbol_names) if short_expr else ""
        description = strip_html(evaluate_js_expression(desc_expr, symbol_names)) if desc_expr else short_description
        value_range = evaluate_js_expression(range_expr, symbol_names) if range_expr else ""
        related_params = parse_string_array(related_expr, symbol_names) if related_expr else []
        prefix_types = parse_object_array(prefix_expr, symbol_names) if prefix_expr else []
        operator_types = parse_object_array(operator_expr, symbol_names) if operator_expr else []
        value_list = parse_object_array(value_list_expr, symbol_names) if value_list_expr else []
        wildcard_parameters = parse_object_array(wildcard_expr, symbol_names) if wildcard_expr else []
        rule_variables = parse_object_array(rule_vars_expr, symbol_names) if rule_vars_expr else []

        used_in_commands: list[str] = []
        needle = f"nameLink: {symbol}.getLink()"
        for command_match in re.finditer(r'var\s+(\w+)\s*=\s*new\s+Command\("([^"]+)"', source):
            command_symbol = command_match.group(1)
            params_expr = parse_assignment_value(source, f"{command_symbol}.commandParameters")
            if params_expr and needle in params_expr:
                used_in_commands.append(command_match.group(2))

        parameters.append(
            ScrapedParameter(
                name=name,
                url=f"{PARAMETERS_DETAILS_URL}#{name}",
                slug=slugify(name),
                description=description,
                short_description=short_description,
                range=value_range,
                version=version,
                es_param_name=es_param_name,
                related_parameters=related_params,
                prefix_types=prefix_types,
                operator_types=operator_types,
                value_list=value_list,
                wildcard_parameters=wildcard_parameters,
                rule_variables=rule_variables,
                used_in_commands=used_in_commands,
                status="scraped",
            )
        )
    return parameters


def parse_strategic_numbers_js(source: str) -> list[ScrapedStrategicNumber]:
    constructor_matches = list(
        re.finditer(r'var\s+(sn\w+)\s*=\s*new\s+StrategicNumber\("([^"]+)"\);', source)
    )
    command_symbols = {
        match.group(1): match.group(2)
        for match in re.finditer(r'var\s+(\w+)\s*=\s*new\s+Command\("([^"]+)"', source)
    }
    sn_symbols = {match.group(1): match.group(2) for match in constructor_matches}
    symbol_names = {**command_symbols, **sn_symbols}

    def prop(symbol: str, key: str) -> str | None:
        return parse_assignment_value(source, f"{symbol}.{key}")

    def scalar(symbol: str, key: str) -> str:
        value = prop(symbol, key)
        if not value:
            return ""
        if value.startswith('"') and value.endswith('"'):
            return js_unquote(value[1:-1])
        return evaluate_js_expression(value, symbol_names)

    def scalar_int(symbol: str, key: str) -> int | str:
        value = scalar(symbol, key)
        return int(value) if value.lstrip("-").isdigit() else value

    def supported_versions(symbol: str) -> list[str]:
        versions: list[str] = []
        for field, label in (("aoe", "AoE1"), ("aoc", "AoC"), ("up", "UP"), ("de", "DE")):
            if scalar(symbol, field) == "1":
                versions.append(label)
        return versions

    strategic_numbers: list[ScrapedStrategicNumber] = []
    id_to_name: dict[int, str] = {}
    raw_linked: dict[str, list[str]] = {}
    raw_related: dict[str, list[str]] = {}

    for match in constructor_matches:
        symbol = match.group(1)
        sn_id_value = scalar(symbol, "id")
        try:
            id_to_name[int(sn_id_value)] = scalar(symbol, "snName") or match.group(2)
        except ValueError:
            pass
        raw_linked[symbol] = parse_string_array(prop(symbol, "linked") or "[]", symbol_names)
        raw_related[symbol] = parse_string_array(prop(symbol, "related") or "[]", symbol_names)

    for match in constructor_matches:
        symbol = match.group(1)
        name = scalar(symbol, "snName") or match.group(2)
        linked_names = [
            id_to_name.get(int(value), value) if str(value).lstrip("-").isdigit() else value
            for value in raw_linked[symbol]
        ]
        related_names = [
            id_to_name.get(int(value), value) if str(value).lstrip("-").isdigit() else value
            for value in raw_related[symbol]
        ]
        strategic_numbers.append(
            ScrapedStrategicNumber(
                name=name,
                url=f"{STRATEGIC_NUMBERS_DETAILS_URL}#{name}",
                slug=slugify(name),
                description=strip_html(
                    evaluate_js_expression(prop(symbol, "description"), symbol_names)
                    if prop(symbol, "description")
                    else scalar(symbol, "shortDescription")
                ),
                short_description=scalar(symbol, "shortDescription"),
                sn_id=scalar_int(symbol, "id"),
                default_value=scalar_int(symbol, "default"),
                required_range=f"{scalar(symbol, 'rmin')} to {scalar(symbol, 'rmax')}",
                allowable_range=f"{scalar(symbol, 'min')} to {scalar(symbol, 'max')}",
                category=scalar(symbol, "category"),
                effective=scalar_int(symbol, "effective"),
                network=scalar_int(symbol, "network"),
                defined=scalar_int(symbol, "defined"),
                available=scalar_int(symbol, "available"),
                version=scalar(symbol, "version"),
                supported_versions=supported_versions(symbol),
                aoe=scalar_int(symbol, "aoe"),
                aoc=scalar_int(symbol, "aoc"),
                up=scalar_int(symbol, "up"),
                de=scalar_int(symbol, "de"),
                aoe1_name=scalar(symbol, "snNameAoE1"),
                linked_sns=linked_names,
                related_sns=related_names,
                status="scraped",
            )
        )
    return strategic_numbers


def parse_value_families_from_parameters(parameters: list[ScrapedParameter]) -> list[ValueFamily]:
    families: list[ValueFamily] = []
    for parameter in parameters:
        if parameter.operator_types:
            entries: list[dict[str, object]] = []
            for item in parameter.operator_types:
                operators = item.get("operator", "")
                if isinstance(operators, str):
                    if operators.strip().startswith("[") and operators.strip().endswith("]"):
                        operators_list = [
                            html.unescape(js_unquote(part.strip()[1:-1]))
                            for part in split_js_array_items(operators.strip()[1:-1])
                            if part.strip().startswith('"') and part.strip().endswith('"')
                        ]
                    else:
                        operators_list = [html.unescape(operators)]
                else:
                    operators_list = list(operators)
                de_id = item.get("deId", "")
                legacy_id = item.get("id", "")
                entries.append(
                    {
                        "name": operators_list[0] if operators_list else "",
                        "aliases": operators_list[1:],
                        "id": de_id or legacy_id,
                        "legacy_id": legacy_id,
                        "de_id": de_id,
                        "id_source": "de_id" if de_id else "id",
                        "description": item.get("description", ""),
                    }
                )
            families.append(
                ValueFamily(
                    parameter_name=parameter.name,
                    family_type="operator-types",
                    entry_count=len(entries),
                    description=parameter.short_description or parameter.description,
                    entries=entries,
                )
            )
        if parameter.value_list:
            entries = [
                {
                    "name": item.get("name", ""),
                    "id": item.get("id", ""),
                    "description": item.get("description", ""),
                    "parameter": item.get("parameter", ""),
                    "players": item.get("players", ""),
                }
                for item in parameter.value_list
            ]
            families.append(
                ValueFamily(
                    parameter_name=parameter.name,
                    family_type="value-list",
                    entry_count=len(entries),
                    description=parameter.short_description or parameter.description,
                    entries=entries,
                )
            )
        if parameter.wildcard_parameters:
            entries = [
                {
                    "name": item.get("name", ""),
                    "id": item.get("id", ""),
                    "de_id": item.get("deId", ""),
                    "description": item.get("description", ""),
                }
                for item in parameter.wildcard_parameters
            ]
            families.append(
                ValueFamily(
                    parameter_name=parameter.name,
                    family_type="wildcard-parameters",
                    entry_count=len(entries),
                    description=parameter.short_description or parameter.description,
                    entries=entries,
                )
            )
        if parameter.prefix_types:
            entries = [
                {
                    "name": item.get("prefix", ""),
                    "description": item.get("description", ""),
                }
                for item in parameter.prefix_types
            ]
            families.append(
                ValueFamily(
                    parameter_name=parameter.name,
                    family_type="prefix-types",
                    entry_count=len(entries),
                    description=parameter.short_description or parameter.description,
                    entries=entries,
                )
            )
    return families


def parse_named_array(source: str, array_name: str) -> str | None:
    return parse_assignment_value(source, array_name)


def _parse_objects_dataset(source: str, groups_array_name: str, names_array_name: str, dataset: str) -> list[ScrapedObject]:
    group_names_expr = parse_named_array(source, names_array_name) or "[]"
    groups_expr = parse_named_array(source, groups_array_name) or "[]"
    group_names = parse_string_array(group_names_expr, {})
    group_symbols = parse_string_array(groups_expr, {})

    objects: list[ScrapedObject] = []
    for group_name, group_symbol in zip(group_names, group_symbols):
        group_expr = parse_named_array(source, group_symbol)
        if not group_expr:
            continue
        for item in parse_object_array(group_expr, {}):
            versions = {
                "aok": int(item.get("aok", 0)) if str(item.get("aok", "")).isdigit() else 0,
                "tc": int(item.get("tc", 0)) if str(item.get("tc", "")).isdigit() else 0,
                "wk": int(item.get("wk", 0)) if str(item.get("wk", "")).isdigit() else 0,
                "de": int(item.get("de", 0)) if str(item.get("de", "")).isdigit() else 0,
            }
            objects.append(
                ScrapedObject(
                    name=item.get("name", ""),
                    ai_name=item.get("aiName", ""),
                    line=item.get("line", ""),
                    object_id=int(item.get("id")) if str(item.get("id", "")).lstrip("-").isdigit() else item.get("id", ""),
                    object_class=item.get("class", ""),
                    cmd_id=item.get("cmdId", ""),
                    building=item.get("building", ""),
                    group_name=group_name,
                    age=int(item.get("age")) if str(item.get("age", "")).lstrip("-").isdigit() else item.get("age", ""),
                    dead_unit=item.get("deadUnit", ""),
                    projectile=item.get("projectile", ""),
                    versions=versions,
                    dataset=dataset,
                    notes=item.get("notes", ""),
                    status="scraped",
                )
            )
    return objects


def parse_offset_name_lines(text: str) -> dict[str, dict[str, str | int]]:
    results: dict[str, dict[str, str | int]] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        match = re.match(r"^(\d+):([A-Za-z_]\w*)$", line)
        if not match:
            continue
        offset = int(match.group(1))
        name = match.group(2)
        results[name] = {"offset": offset, "name": name}
    return results


def strip_html_fragment(text: str) -> str:
    no_scripts = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", text, flags=re.S | re.I)
    with_breaks = re.sub(r"<br\s*/?>", "\n", no_scripts, flags=re.I)
    without_tags = re.sub(r"<[^>]+>", " ", with_breaks)
    return collapse_ws(html.unescape(without_tags).replace("\xa0", " "))


def normalize_numbered_heading(text: str) -> str:
    return collapse_ws(re.sub(r"^\d+(?:\.\d+)*\.?\s*", "", text))


def parse_xs_signature_lines(text: str) -> dict[str, dict[str, str]]:
    results: dict[str, dict[str, str]] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        match = re.match(r"^\d+:(.+)$", line)
        if not match:
            continue
        payload = collapse_ws(match.group(1))
        func_match = re.match(
            r"^(?:(?P<return>[A-Za-z_][\w\s\*]*)\s+)?(?P<name>[A-Za-z_]\w*)\((?P<params>[^)]*)\)(?::\s*(?P<desc>.*))?$",
            payload,
        )
        if not func_match:
            continue
        name = func_match.group("name")
        return_type = collapse_ws(func_match.group("return") or "")
        params_raw = collapse_ws(func_match.group("params") or "")
        params = [collapse_ws(part) for part in params_raw.split(",")] if params_raw and params_raw != "void" else []
        description = collapse_ws(func_match.group("desc") or "")
        results[name] = {
            "signature": payload,
            "return_type": return_type,
            "parameters_raw": params_raw,
            "description": description,
            "parameters_json": json.dumps(params),
        }
    return results


def parse_ugc_xs_functions_html(text: str) -> dict[str, dict[str, object]]:
    data: dict[str, dict[str, object]] = {}
    category_matches = list(
        re.finditer(r'<h2 id="[^"]+">(.*?)<a class="headerlink"', text, flags=re.S | re.I)
    )
    section_bounds: list[tuple[int, int, str]] = []
    for index, match in enumerate(category_matches):
        title = normalize_numbered_heading(strip_html_fragment(match.group(1)))
        start = match.end()
        end = category_matches[index + 1].start() if index + 1 < len(category_matches) else len(text)
        section_bounds.append((start, end, title))
    for start, end, category_title in section_bounds:
        section = text[start:end]
        function_matches = list(
            re.finditer(r'<h3 id="([^"]+)">(.*?)<a class="headerlink"', section, flags=re.S | re.I)
        )
        for index, match in enumerate(function_matches):
            block_start = match.end()
            block_end = function_matches[index + 1].start() if index + 1 < len(function_matches) else len(section)
            block = section[block_start:block_end]
            title_text = strip_html_fragment(match.group(2))
            name_match = re.search(r"\b(xs[A-Za-z0-9_]+|bitCastToFloat|bitCastToInt)\b", title_text)
            if not name_match:
                continue
            name = name_match.group(1)
            anchor = match.group(1)
            return_match = re.search(r"Returning Type:\s*<code[^>]*>(.*?)</code>", block, flags=re.S | re.I)
            prototype_match = re.search(r"Prototype:\s*<code[^>]*>(.*?)</code>", block, flags=re.S | re.I)
            parameters: list[str] = []
            params_match = re.search(r"<p>Parameters:</p>\s*<ol>(.*?)</ol>", block, flags=re.S | re.I)
            if params_match:
                parameters = [
                    strip_html_fragment(item)
                    for item in re.findall(r"<li>(.*?)</li>", params_match.group(1), flags=re.S | re.I)
                    if strip_html_fragment(item)
                ]
            examples = [
                strip_html_fragment(item)
                for item in re.findall(r"<pre[^>]*><code>(.*?)</code></pre>", block, flags=re.S | re.I)
                if strip_html_fragment(item)
            ]
            paragraphs = [strip_html_fragment(item) for item in re.findall(r"<p>(.*?)</p>", block, flags=re.S | re.I)]
            description_parts = [
                paragraph
                for paragraph in paragraphs
                if paragraph
                and not paragraph.startswith("Returning Type:")
                and not paragraph.startswith("Prototype:")
                and paragraph != "Parameters:"
                and not paragraph.startswith("See also:")
            ]
            description = description_parts[-1] if description_parts else ""
            data[name] = {
                "name": name,
                "category": category_title,
                "return_type": strip_html_fragment(return_match.group(1)) if return_match else "",
                "prototype": strip_html_fragment(prototype_match.group(1)) if prototype_match else "",
                "parameters": parameters,
                "description": description,
                "examples": examples[:3],
                "url": f"https://ugc.aoe2.rocks/general/xs/functions/functions/#{anchor}",
                "source": "ugc-xs-functions",
            }
    return data


def parse_fe_xs_reference_html(text: str) -> dict[str, dict[str, object]]:
    results: dict[str, dict[str, object]] = {}
    section_matches = list(
        re.finditer(r'<h1 id="[^"]+">(.*?)</h1>', text, flags=re.S | re.I)
    )
    for index, match in enumerate(section_matches):
        section_title = strip_html_fragment(match.group(1))
        start = match.end()
        end = section_matches[index + 1].start() if index + 1 < len(section_matches) else len(text)
        section = text[start:end]
        for row in re.findall(r"<tr[^>]*>(.*?)</tr>", section, flags=re.S | re.I):
            cells = re.findall(r"<td[^>]*>(.*?)</td>", row, flags=re.S | re.I)
            if len(cells) < 2:
                continue
            name = strip_html_fragment(cells[0])
            if not re.fullmatch(r"(xs[A-Za-z0-9_]+|bitCastToFloat|bitCastToInt)", name):
                continue
            desc_cell = cells[1]
            example_cell = cells[2] if len(cells) >= 3 else ""
            syntax_match = re.search(r"<code>(.*?)</code>", desc_cell, flags=re.S | re.I)
            examples = [strip_html_fragment(item) for item in re.findall(r"<code>(.*?)</code>", example_cell, flags=re.S | re.I)]
            paragraphs = [strip_html_fragment(item) for item in re.findall(r"<p[^>]*>(.*?)</p>", desc_cell, flags=re.S | re.I)]
            description_parts = [
                paragraph
                for paragraph in paragraphs
                if paragraph and paragraph != "Syntax:" and not paragraph.startswith(name + "(")
            ]
            results[name] = {
                "name": name,
                "context": section_title,
                "syntax": strip_html_fragment(syntax_match.group(1)) if syntax_match else "",
                "description": description_parts[0] if description_parts else "",
                "examples": examples[:3],
                "url": "https://www.forgottenempires.net/age-of-empires-ii-definitive-edition/xs-scripting-in-age-of-empires-ii-definitive-edition",
                "source": "forgotten-empires-xs",
            }
    return results


def parse_ugc_xs_constants_html(text: str) -> list[ScrapedXsConstant]:
    constants: list[ScrapedXsConstant] = []
    category_matches = list(
        re.finditer(r'<h2 id="([^"]+)">(.*?)<a class="headerlink"[^>]*>', text, flags=re.S | re.I)
    )
    for index, match in enumerate(category_matches):
        category_title = normalize_numbered_heading(strip_html_fragment(match.group(2)))
        start = match.end()
        end = category_matches[index + 1].start() if index + 1 < len(category_matches) else len(text)
        section = text[start:end]
        item_matches = list(
            re.finditer(r'<h3 id="([^"]+)">(.*?)<a class="headerlink"[^>]*>', section, flags=re.S | re.I)
        )
        for item_index, item_match in enumerate(item_matches):
            item_start = item_match.end()
            item_end = item_matches[item_index + 1].start() if item_index + 1 < len(item_matches) else len(section)
            block = section[item_start:item_end]
            anchor_id = item_match.group(1)
            name = normalize_numbered_heading(strip_html_fragment(item_match.group(2)))
            if not re.fullmatch(r"[A-Za-z_]\w*", name):
                continue
            value_match = re.search(r"Value:\s*<code[^>]*>(.*?)</code>", block, flags=re.S | re.I)
            value_text = strip_html_fragment(value_match.group(1)) if value_match else ""
            value_type = ""
            value = value_text
            type_match = re.match(r"([A-Za-z_][\w]*)\s+(.*)", value_text)
            if type_match:
                value_type = type_match.group(1)
                value = type_match.group(2)
            paragraphs = [strip_html_fragment(item) for item in re.findall(r"<p[^>]*>(.*?)</p>", block, flags=re.S | re.I)]
            description_parts = [
                paragraph
                for paragraph in paragraphs
                if paragraph and not paragraph.startswith("Value:")
            ]
            constants.append(
                ScrapedXsConstant(
                    name=name,
                    category=category_title,
                    value_type=value_type,
                    value=value,
                    description=description_parts[0] if description_parts else "",
                    source=f"https://ugc.aoe2.rocks/general/xs/constants/constants/#{anchor_id}",
                )
            )
    return constants


def _is_rms_toc_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    if stripped == "Table of Contents":
        return False
    if stripped == "Foreword":
        return False
    if stripped.endswith(":"):
        return False
    return True


def _looks_like_heading(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    if len(stripped) > 80:
        return False
    if stripped.endswith("."):
        return False
    if stripped.startswith("*") or stripped.startswith("-"):
        return False
    return stripped == stripped.title() or stripped.isupper() or "?" in stripped


def parse_rms_guide_topics(text: str) -> list[ScrapedRmsTopic]:
    lines = text.splitlines()
    try:
        toc_start = lines.index("Table of Contents") + 1
    except ValueError:
        return []
    toc_lines: list[str] = []
    toc_end = toc_start
    for index in range(toc_start, len(lines)):
        line = lines[index]
        if line.strip() == "Foreword" and toc_lines:
            toc_end = index
            break
        if _is_rms_toc_line(line):
            toc_lines.append(line.rstrip())
    body_lines = lines[toc_end:]
    topics: list[ScrapedRmsTopic] = []
    stack: list[str] = []
    for raw in toc_lines:
        stripped = raw.strip()
        indent = len(raw) - len(raw.lstrip(" "))
        level = 2 if indent > 0 else 1
        if level == 1:
            stack = [stripped]
        else:
            stack = stack[:1] + [stripped]
        summary = ""
        for body_index, body_line in enumerate(body_lines):
            if body_line.strip() != stripped:
                continue
            for follow in body_lines[body_index + 1 : body_index + 8]:
                candidate = follow.strip()
                if not candidate or candidate == stripped or _looks_like_heading(candidate):
                    continue
                summary = collapse_ws(candidate)
                break
            break
        topics.append(
            ScrapedRmsTopic(
                name=stripped,
                level=level,
                path=list(stack),
                summary=summary,
                source="docs/extracted/raw/rms/rms-reference-google-doc.txt",
            )
        )
    return topics


def classify_xs_function(name: str) -> str:
    if name.startswith("xsArray"):
        return "arrays"
    if name.startswith("xsVector"):
        return "vector"
    if name in {"xsGetGoal", "xsSetGoal", "xsGetStrategicNumber", "xsSetStrategicNumber"}:
        return "ai-state"
    if name.startswith("xsEnableRule") or name.startswith("xsDisableRule") or name.startswith("xsIsRule") or name.startswith("xsSetRule"):
        return "rules"
    if name in {"xsGetContextPlayer", "xsSetContextPlayer"}:
        return "context"
    if name.startswith("xsCreateFile") or name.startswith("xsOpenFile") or name.startswith("xsWrite") or name.startswith("xsRead") or name.startswith("xsSetFilePosition") or name.startswith("xsOffsetFilePosition") or name.startswith("xsCloseFile"):
        return "file-io"
    if name == "xsChatData":
        return "debug"
    if name.startswith("xsTriggerVariable") or name.startswith("xsSetTriggerVariable"):
        return "scenario-trigger"
    if name.startswith("xsTask") or name.startswith("xsRemoveTask") or name.startswith("xsModify") or name.startswith("xsResetTaskAmount") or name.startswith("xsGetTaskAmount") or name.startswith("xsObjectTaskAmount") or name.startswith("xsUnitTaskAmount"):
        return "tasks"
    if name.startswith("xsPlayer") or name.startswith("xsGetPlayer") or name.startswith("xsSetPlayer") or name.startswith("xsGetMap") or name.startswith("xsGetVictory") or name.startswith("xsGetGame") or name.startswith("xsGetDifficulty") or name.startswith("xsGetColorMood") or name.startswith("xsSetColorMood") or name.startswith("xsGetWorldPlayerId"):
        return "game-state"
    if name.startswith("xsResearchTechnology") or name.startswith("xsEffectAmount"):
        return "tech-effects"
    if name.startswith("xsGetObject") or name.startswith("xsGetUnit") or name.startswith("xsSetUnit") or name.startswith("xsDoesUnitExist") or name.startswith("xsCreateUnit") or name.startswith("xsRemoveUnit") or name.startswith("xsIsObjectAvailable") or name.startswith("xsGetGarrisoned"):
        return "unit-object"
    if name.startswith("xsGetDiplomacy") or name.startswith("xsSetDiplomacy"):
        return "diplomacy"
    if name.startswith("bitCast"):
        return "bitcast"
    if name.startswith("xsGetRandom") or name in {"xsGetTime", "xsCeilToInt", "xsBreakPoint"}:
        return "runtime"
    return "misc"


def xs_ai_context_status(name: str) -> tuple[str, str]:
    observed_working = {
        "xsChatData": "Observed working from AI XS in sample_ai debugging.",
        "xsSetContextPlayer": "Required by project notes before AI XS file I/O attempts.",
    }
    context_sensitive = {
        "xsCreateFile": "Observed to fail from AI xs-script-call without setting XS context player first.",
        "xsOpenFile": "Treat file I/O as AI-context-sensitive until tested with context-player handling.",
        "xsWriteString": "Treat file I/O as AI-context-sensitive until tested with context-player handling.",
        "xsWriteInt": "Treat file I/O as AI-context-sensitive until tested with context-player handling.",
        "xsWriteFloat": "Treat file I/O as AI-context-sensitive until tested with context-player handling.",
        "xsWriteVector": "Treat file I/O as AI-context-sensitive until tested with context-player handling.",
        "xsReadString": "Treat file I/O as AI-context-sensitive until tested with context-player handling.",
        "xsReadInt": "Treat file I/O as AI-context-sensitive until tested with context-player handling.",
        "xsReadFloat": "Treat file I/O as AI-context-sensitive until tested with context-player handling.",
        "xsReadVector": "Treat file I/O as AI-context-sensitive until tested with context-player handling.",
        "xsCloseFile": "Treat file I/O as AI-context-sensitive until tested with context-player handling.",
    }
    if name in observed_working:
        return "observed-working-in-ai-context", observed_working[name]
    if name in context_sensitive:
        return "context-sensitive-in-ai", context_sensitive[name]
    return "unvalidated-in-ai-context", "Documented or binary-extracted XS function. Validate in AI context before relying on it."


def parse_xs_function_inventory(
    *,
    signatures_text: str,
    names_text: str,
    strings_text: str,
    ugc_functions_html: str = "",
    fe_reference_html: str = "",
) -> list[ScrapedXsFunction]:
    names = parse_offset_name_lines(names_text)
    signatures = parse_xs_signature_lines(signatures_text)
    fallback_signatures = parse_xs_signature_lines(strings_text)
    ugc_data = parse_ugc_xs_functions_html(ugc_functions_html) if ugc_functions_html else {}
    fe_data = parse_fe_xs_reference_html(fe_reference_html) if fe_reference_html else {}
    functions: list[ScrapedXsFunction] = []
    all_names = sorted(
        {
            *[name for name in names if name.startswith("xs") or name.startswith("bitCast")],
            *ugc_data.keys(),
            *fe_data.keys(),
        },
        key=str.casefold,
    )
    for name in all_names:
        meta = names.get(name, {})
        if not (name.startswith("xs") or name.startswith("bitCast")):
            continue
        detail = signatures.get(name) or fallback_signatures.get(name) or {}
        ugc = ugc_data.get(name, {})
        fe = fe_data.get(name, {})
        params = list(ugc.get("parameters", [])) or (json.loads(detail.get("parameters_json", "[]")) if detail else [])
        ai_context_status, notes = xs_ai_context_status(name)
        if name not in names and ugc:
            ai_context_status = "documented-not-in-local-binary"
            notes = "Documented in UGC function reference but not found in the current local binary extract."
        source = str(ugc.get("url") or fe.get("url") or ("docs/extracted/raw/aoe2de/aoe2de-xs-function-signatures.txt" if name in signatures else "docs/extracted/raw/aoe2de/aoe2de-xs-strings.txt"))
        secondary_sources = [
            value
            for value in [
                "docs/extracted/raw/aoe2de/aoe2de-xs-function-signatures.txt" if name in signatures else "",
                "docs/extracted/raw/aoe2de/aoe2de-xs-strings.txt" if name in fallback_signatures else "",
                str(fe.get("url", "")),
                str(ugc.get("url", "")),
            ]
            if value and value != source
        ]
        merged_examples = list(dict.fromkeys([*ugc.get("examples", []), *fe.get("examples", [])]))[:4]
        contexts = list(dict.fromkeys([str(fe.get("context", ""))] if fe.get("context") else []))
        functions.append(
            ScrapedXsFunction(
                name=name,
                offset=int(meta.get("offset")) if meta.get("offset") is not None else None,
                signature=str(ugc.get("prototype") or fe.get("syntax") or detail.get("signature", f"{name}()")),
                return_type=str(ugc.get("return_type") or detail.get("return_type", "")),
                parameters=params,
                description=str(ugc.get("description") or fe.get("description") or detail.get("description", "")),
                category=str(ugc.get("category") or classify_xs_function(name)),
                ai_context_status=ai_context_status,
                source=source,
                notes=notes,
                contexts=contexts,
                examples=merged_examples,
                secondary_sources=secondary_sources,
                prototype=str(ugc.get("prototype") or fe.get("syntax") or detail.get("signature", "")),
            )
        )
    return functions


RMS_FIXTURE_OVERRIDES: dict[str, dict[str, object]] = {
    "rms_test_blank_units.rms": {
        "summary": "Basic-unit fixture for initial DUC, point, scout, and gather probes.",
        "tags": ["duc", "scout", "villager", "sheep", "baseline"],
        "use_cases": ["object search", "point reads", "scout movement", "owned vs gaia herdables"],
        "recommended_probe": "ai/basic_command_probe",
    },
    "rms_test_front_back.rms": {
        "summary": "Front/back geometry fixture for directional opening heuristics.",
        "tags": ["front-back", "geometry", "scout", "herdables"],
        "use_cases": ["front-vs-back herdable classification", "distance heuristics"],
        "recommended_probe": "extension samples",
    },
    "rms_test_house_placement.rms": {
        "summary": "House-placement isolation fixture with TC and starting villagers only.",
        "tags": ["houses", "builders", "placement", "opening"],
        "use_cases": ["house point math", "builder assignment", "TC distance guard"],
        "recommended_probe": "ai/house_placement_probe",
    },
    "rms_test_no_visible_sheep.rms": {
        "summary": "Fallback opener fixture with no owned visible herdable.",
        "tags": ["fallback", "gaia-herdables", "fog-search", "opening"],
        "use_cases": ["villager fallback collection", "scout/villager herdable search"],
        "recommended_probe": "extension samples",
    },
    "rms_test_opening_sheep.rms": {
        "summary": "Integrated opening fixture with houses, owned sheep, gaia sheep, berries, and stragglers.",
        "tags": ["opening", "sheep", "houses", "berries", "integration"],
        "use_cases": ["opening integration", "house plus herdable sequencing", "staged collection"],
        "recommended_probe": "extension samples",
    },
    "rms_test_precise_scout.rms": {
        "summary": "Precise-point fixture with a scout only.",
        "tags": ["precise-point", "scout", "movement"],
        "use_cases": ["precise coordinate movement", "object-data-precise-* inspection"],
        "recommended_probe": "extension samples",
    },
    "rms_test_single_sheep.rms": {
        "summary": "Primary hard-isolation fixture for one owned sheep and no villagers.",
        "tags": ["single-sheep", "isolation", "duc", "movement"],
        "use_cases": ["single livestock movement", "TC-side sheep target point"],
        "recommended_probe": "ai/basic_command_probe",
    },
    "rms_test_tc_rally.rms": {
        "summary": "TC rally probe fixture with trainable villager and sheep noise.",
        "tags": ["tc-rally", "villager", "rally"],
        "use_cases": ["TC gather-point behavior", "new villager rally destination"],
        "recommended_probe": "ai/tc_rally_probe",
    },
    "rms_test_tc_rally_nosheep.rms": {
        "summary": "TC rally probe fixture without sheep to avoid rally ambiguity.",
        "tags": ["tc-rally", "nosheep", "villager", "rally"],
        "use_cases": ["point-rally validation without economic noise"],
        "recommended_probe": "ai/tc_rally_probe",
    },
    "rms_test_tc_transport.rms": {
        "summary": "Minimal TC garrison and ungarrison transport fixture.",
        "tags": ["tc-transport", "garrison", "ungarrison", "villager"],
        "use_cases": ["villager-to-TC garrison", "post-garrison unload behavior"],
        "recommended_probe": "ai/tc_transport_probe",
    },
    "rms_test_two_sheep.rms": {
        "summary": "Two-owned-sheep targeting fixture.",
        "tags": ["two-sheep", "duc", "selection", "movement"],
        "use_cases": ["move exactly one sheep", "spare sheep stop logic"],
        "recommended_probe": "ai/basic_command_probe",
    },
    "rms_test_two_sheep_one_villager.rms": {
        "summary": "Two-sheep plus one-villager fixture for activation after positioning.",
        "tags": ["two-sheep", "villager", "activation", "gather"],
        "use_cases": ["wait-before-gather behavior", "active sheep readiness checks"],
        "recommended_probe": "ai/basic_command_probe",
    },
    "rms_test_two_sheep_separate.rms": {
        "summary": "Diagnostic fixture with sheep from separate RMS create_object blocks.",
        "tags": ["two-sheep", "diagnostic", "rms-grouping"],
        "use_cases": ["check whether RMS grouping influences two-sheep movement"],
        "recommended_probe": "ai/basic_command_probe",
    },
}


def parse_rms_fixture(path: Path) -> ScrapedRmsFixture:
    text = path.read_text(encoding="utf-8")
    first_comment = re.search(r"/\*\s*([^\r\n*]+)", text)
    title = collapse_ws(first_comment.group(1)) if first_comment else path.stem
    map_type_match = re.search(r"ai_info_map_type\s+([A-Z0-9_]+)", text)
    map_type = map_type_match.group(1) if map_type_match else ""
    create_objects = re.findall(r"create_object\s+([A-Z0-9_]+)", text)
    sections = re.findall(r"<([A-Z_]+)>", text)
    override = RMS_FIXTURE_OVERRIDES.get(path.name, {})
    summary = str(override.get("summary", title))
    tags = list(override.get("tags", []))
    use_cases = list(override.get("use_cases", []))
    recommended_probe = str(override.get("recommended_probe", ""))
    if "fixture" not in tags:
        tags.append("fixture")
    if map_type:
        tags.append(map_type.lower())
    return ScrapedRmsFixture(
        name=path.name,
        path=str(path.as_posix()),
        title=title,
        summary=summary,
        map_type=map_type,
        create_objects=create_objects,
        sections=sections,
        tags=sorted(dict.fromkeys(tags)),
        use_cases=use_cases,
        recommended_probe=recommended_probe,
    )


def scrape_xs_functions(
    *,
    output_path: Path,
    signatures_path: Path = RAW_AOE2DE_DIR / "aoe2de-xs-function-signatures.txt",
    names_path: Path = RAW_AOE2DE_DIR / "aoe2de-xs-function-names.txt",
    strings_path: Path = RAW_AOE2DE_DIR / "aoe2de-xs-strings.txt",
    ugc_functions_path: Path | None = RAW_XS_DIR / "ugc-xs-functions-root.html",
    fe_reference_path: Path | None = RAW_XS_DIR / "fe-xs.html",
) -> dict[str, object]:
    functions = parse_xs_function_inventory(
        signatures_text=signatures_path.read_text(encoding="utf-8"),
        names_text=names_path.read_text(encoding="utf-8"),
        strings_text=strings_path.read_text(encoding="utf-8"),
        ugc_functions_html=ugc_functions_path.read_text(encoding="utf-8") if ugc_functions_path and ugc_functions_path.exists() else "",
        fe_reference_html=fe_reference_path.read_text(encoding="utf-8") if fe_reference_path and fe_reference_path.exists() else "",
    )
    payload: dict[str, object] = {
        "metadata": {
            "source": "merged-local-binary-and-xs-docs",
            "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "function_count": len(functions),
            "signatures_path": str(signatures_path),
            "names_path": str(names_path),
            "strings_path": str(strings_path),
            "ugc_functions_path": str(ugc_functions_path) if ugc_functions_path else "",
            "fe_reference_path": str(fe_reference_path) if fe_reference_path else "",
        },
        "functions": [asdict(item) for item in functions],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")
    return payload


def scrape_rms_fixtures(
    *,
    output_path: Path,
    rms_dir: Path = Path("rms"),
) -> dict[str, object]:
    fixtures = [parse_rms_fixture(path) for path in sorted(rms_dir.glob("*.rms"))]
    payload: dict[str, object] = {
        "metadata": {
            "source": str(rms_dir),
            "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "fixture_count": len(fixtures),
        },
        "fixtures": [asdict(item) for item in fixtures],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")
    return payload


def scrape_xs_constants(
    *,
    output_path: Path,
    ugc_constants_path: Path = RAW_XS_DIR / "ugc-xs-constants.html",
) -> dict[str, object]:
    constants = parse_ugc_xs_constants_html(ugc_constants_path.read_text(encoding="utf-8"))
    payload: dict[str, object] = {
        "metadata": {
            "source": "https://ugc.aoe2.rocks/general/xs/constants/constants/",
            "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "constant_count": len(constants),
            "ugc_constants_path": str(ugc_constants_path),
        },
        "constants": [asdict(item) for item in constants],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")
    return payload


def scrape_rms_topics(
    *,
    output_path: Path,
    guide_path: Path = RAW_RMS_DIR / "rms-reference-google-doc.txt",
) -> dict[str, object]:
    topics = parse_rms_guide_topics(guide_path.read_text(encoding="utf-8"))
    payload: dict[str, object] = {
        "metadata": {
            "source": "https://docs.google.com/document/d/1jnhZXoeL9mkRUJxcGlKnO98fIwFKStP_OBozpr0CHXo/edit",
            "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "topic_count": len(topics),
            "guide_path": str(guide_path),
        },
        "topics": [asdict(item) for item in topics],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")
    return payload


def parse_objects_js(source: str) -> list[ScrapedObject]:
    objects: list[ScrapedObject] = []
    objects.extend(_parse_objects_dataset(source, "objectsArray", "objectsBuildingNamesArray", "standard"))
    objects.extend(_parse_objects_dataset(source, "objectsArrayROR", "objectsBuildingNamesArrayROR", "ror"))
    objects.extend(_parse_objects_dataset(source, "objectsArrayChr", "objectsBuildingNamesArrayChr", "chronicles"))
    return objects


def _parse_techs_dataset(source: str, groups_array_name: str, names_array_name: str, dataset: str) -> list[ScrapedTech]:
    group_names_expr = parse_named_array(source, names_array_name) or "[]"
    groups_expr = parse_named_array(source, groups_array_name) or "[]"
    group_names = parse_string_array(group_names_expr, {})
    group_symbols = parse_string_array(groups_expr, {})

    techs: list[ScrapedTech] = []
    for group_name, group_symbol in zip(group_names, group_symbols):
        group_expr = parse_named_array(source, group_symbol)
        if not group_expr:
            continue
        for item in parse_object_array(group_expr, {}):
            versions = {
                "aok": int(item.get("aok", 0)) if str(item.get("aok", "")).isdigit() else 0,
                "tc": int(item.get("tc", 0)) if str(item.get("tc", "")).isdigit() else 0,
                "wk": int(item.get("wk", 0)) if str(item.get("wk", "")).isdigit() else 0,
                "de": int(item.get("de", 0)) if str(item.get("de", "")).isdigit() else 0,
            }
            techs.append(
                ScrapedTech(
                    name=item.get("name", ""),
                    ai_name=item.get("aiName", ""),
                    tech_id=int(item.get("id")) if str(item.get("id", "")).lstrip("-").isdigit() else item.get("id", ""),
                    building=item.get("building", ""),
                    group_name=group_name,
                    age=int(item.get("age")) if str(item.get("age", "")).lstrip("-").isdigit() else item.get("age", ""),
                    civilization=item.get("civ", ""),
                    cost=item.get("cost", ""),
                    time=int(item.get("time")) if str(item.get("time", "")).lstrip("-").isdigit() else item.get("time", ""),
                    description=item.get("description", ""),
                    versions=versions,
                    dataset=dataset,
                    notes=item.get("notes", ""),
                    status="scraped",
                )
            )
    return techs


def parse_techs_js(source: str) -> list[ScrapedTech]:
    techs: list[ScrapedTech] = []
    techs.extend(_parse_techs_dataset(source, "techsArray", "techsBuildingsArray", "standard"))
    techs.extend(_parse_techs_dataset(source, "techsArrayROR", "techsBuildingsArrayROR", "ror"))
    techs.extend(_parse_techs_dataset(source, "techsArrayChr", "techsBuildingsArrayChr", "chronicles"))
    return techs


def scrape_airef_commands(
    *,
    index_url: str = COMMANDS_INDEX_URL,
    output_path: Path,
    cache_dir: Path | None = None,
    delay_seconds: float = 0.0,
    limit: int | None = None,
    source_dir: Path = DEFAULT_SOURCE_DIR,
) -> dict[str, object]:
    commands_js_path = source_dir / "js" / "commands.js"
    details_html_path = source_dir / "commands" / "commands-details.html"
    source = commands_js_path.read_text(encoding="utf-8")
    commands = parse_commands_js(source)
    if limit is not None:
        commands = commands[:limit]
    if delay_seconds:
        time.sleep(min(delay_seconds, 0.01))

    cache_dir_str: str | None = None
    if cache_dir is not None:
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache_dir_str = str(cache_dir)
        shutil.copy2(commands_js_path, cache_dir / "commands.js")
        shutil.copy2(details_html_path, cache_dir / "commands-details.html")

    payload: dict[str, object] = {
        "metadata": {
            "source": index_url,
            "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "command_count": len(commands),
            "failure_count": 0,
            "cache_dir": cache_dir_str,
            "scrape_method": "Local AIRef source parse from js/commands.js and commands/commands-details.html",
            "source_dir": str(source_dir),
        },
        "commands": [asdict(command) for command in commands],
        "failures": [],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")
    return payload


def scrape_airef_parameters(*, output_path: Path, source_dir: Path = DEFAULT_SOURCE_DIR) -> dict[str, object]:
    source = (source_dir / "js" / "commands.js").read_text(encoding="utf-8")
    parameters = parse_parameters_js(source)
    payload: dict[str, object] = {
        "metadata": {
            "source": PARAMETERS_DETAILS_URL,
            "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "parameter_count": len(parameters),
            "scrape_method": "Local AIRef source parse from js/commands.js and parameters/parameters-details.html",
            "source_dir": str(source_dir),
        },
        "parameters": [asdict(parameter) for parameter in parameters],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")
    return payload


def scrape_airef_strategic_numbers(*, output_path: Path, source_dir: Path = DEFAULT_SOURCE_DIR) -> dict[str, object]:
    source = (source_dir / "js" / "commands.js").read_text(encoding="utf-8")
    all_strategic_numbers = parse_strategic_numbers_js(source)
    strategic_numbers = [sn for sn in all_strategic_numbers if sn.de == 1]
    existing_names = {sn.name for sn in strategic_numbers}
    for name in LOCAL_DE_STRATEGIC_NUMBER_SUPPLEMENTS:
        if name in existing_names:
            continue
        strategic_numbers.append(
            ScrapedStrategicNumber(
                name=name,
                url=str(RAW_AOE2DE_DIR / "aoe2de-strategic-number-strings.txt"),
                slug=slugify(name),
                description="Found in the local AoE2DE executable strategic-number string dump, but not documented by AIRef.",
                short_description="Local AoE2DE binary-only strategic number.",
                sn_id="",
                default_value="",
                required_range="",
                allowable_range="",
                category="Other",
                effective="unknown",
                network="unknown",
                defined="unknown",
                available="unknown",
                version="DE",
                supported_versions=["DE"],
                aoe=0,
                aoc=0,
                up=0,
                de=1,
                aoe1_name="",
                linked_sns=[],
                related_sns=[],
                status="binary-only",
            )
        )
    allowed_names = {sn.name for sn in strategic_numbers}

    def scrub_non_de_sn_references(text: str) -> str:
        return re.sub(
            r"\bsn-[a-z0-9-]+\b",
            lambda match: match.group(0) if match.group(0) in allowed_names else NON_DE_SN_REPLACEMENT,
            text,
        )

    strategic_numbers = [
        replace(
            sn,
            description=scrub_non_de_sn_references(sn.description),
            short_description=scrub_non_de_sn_references(sn.short_description),
            linked_sns=[name for name in sn.linked_sns if name in allowed_names],
            related_sns=[name for name in sn.related_sns if name in allowed_names],
        )
        for sn in strategic_numbers
    ]
    payload: dict[str, object] = {
        "metadata": {
            "source": STRATEGIC_NUMBERS_DETAILS_URL,
            "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "strategic_number_count": len(strategic_numbers),
            "unfiltered_strategic_number_count": len(all_strategic_numbers),
            "version_filter": "de == 1",
            "local_supplement_count": len([sn for sn in strategic_numbers if sn.status == "binary-only"]),
            "scrape_method": "Local AIRef source parse from js/commands.js and strategic-numbers/sn-details.html",
            "source_dir": str(source_dir),
        },
        "strategic_numbers": [asdict(sn) for sn in strategic_numbers],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")
    return payload


def scrape_airef_value_families(*, output_path: Path, source_dir: Path = DEFAULT_SOURCE_DIR) -> dict[str, object]:
    source = (source_dir / "js" / "commands.js").read_text(encoding="utf-8")
    parameters = parse_parameters_js(source)
    families = parse_value_families_from_parameters(parameters)
    payload: dict[str, object] = {
        "metadata": {
            "source": PARAMETERS_DETAILS_URL,
            "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "family_count": len(families),
            "scrape_method": "Derived local inventory from AIRef parameter value lists and operator lists",
            "source_dir": str(source_dir),
        },
        "families": [asdict(family) for family in families],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")
    return payload


def scrape_airef_objects(*, output_path: Path, source_dir: Path = DEFAULT_SOURCE_DIR) -> dict[str, object]:
    source = (source_dir / "js" / "commands.js").read_text(encoding="utf-8")
    all_objects = parse_objects_js(source)
    objects = [item for item in all_objects if item.versions.get("de") == 1]
    payload: dict[str, object] = {
        "metadata": {
            "source": "https://airef.github.io/tables/objects.html",
            "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "object_count": len(objects),
            "unfiltered_object_count": len(all_objects),
            "version_filter": "versions.de == 1",
            "scrape_method": "Local AIRef source parse from js/commands.js and tables/objects.html",
            "source_dir": str(source_dir),
        },
        "objects": [asdict(item) for item in objects],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")
    return payload


def scrape_airef_techs(*, output_path: Path, source_dir: Path = DEFAULT_SOURCE_DIR) -> dict[str, object]:
    source = (source_dir / "js" / "commands.js").read_text(encoding="utf-8")
    all_techs = parse_techs_js(source)
    techs = [item for item in all_techs if item.versions.get("de") == 1]
    payload: dict[str, object] = {
        "metadata": {
            "source": "https://airef.github.io/tables/techs.html",
            "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "tech_count": len(techs),
            "unfiltered_tech_count": len(all_techs),
            "version_filter": "versions.de == 1",
            "scrape_method": "Local AIRef source parse from js/commands.js and tables/techs.html",
            "source_dir": str(source_dir),
        },
        "techs": [asdict(item) for item in techs],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")
    return payload
