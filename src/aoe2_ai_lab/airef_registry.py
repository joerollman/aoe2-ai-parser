from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class RegistryEntry:
    kind: str
    entry_id: str
    name: str
    summary: str
    source_urls: tuple[str, ...]
    lookup_terms: tuple[str, ...]
    aliases: tuple[str, ...]
    tags: tuple[str, ...]
    validation_status: str


@dataclass(frozen=True)
class ResolvedReference:
    primary: RegistryEntry | None
    related: tuple[RegistryEntry, ...]
    details: dict[str, Any]


BINARY_KINDS = {"binary-family", "binary-token"}


def default_registry_path() -> Path:
    return Path("docs") / "extracted" / "inventories" / "airef-site-registry.json"


def default_command_inventory_path() -> Path:
    return Path("docs") / "extracted" / "inventories" / "airef-command-inventory.json"


def inventory_path_for(registry_path: Path, name: str) -> Path:
    direct = registry_path.parent / name
    if direct.exists():
        return direct

    nested = registry_path.parent / "inventories" / name
    if nested.exists():
        return nested

    return direct


def load_registry(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    inventory_path = inventory_path_for(path, "airef-command-inventory.json")
    if inventory_path.exists():
        inventory = json.loads(inventory_path.read_text(encoding="utf-8-sig"))
        data["command_inventory"] = inventory.get("commands", [])
        data["command_inventory_metadata"] = inventory.get("metadata", {})
    parameter_inventory_path = inventory_path_for(path, "airef-parameter-inventory.json")
    if parameter_inventory_path.exists():
        inventory = json.loads(parameter_inventory_path.read_text(encoding="utf-8-sig"))
        data["parameter_inventory"] = inventory.get("parameters", [])
        data["parameter_inventory_metadata"] = inventory.get("metadata", {})
    sn_inventory_path = inventory_path_for(path, "airef-strategic-number-inventory.json")
    if sn_inventory_path.exists():
        inventory = json.loads(sn_inventory_path.read_text(encoding="utf-8-sig"))
        data["strategic_number_inventory"] = inventory.get("strategic_numbers", [])
        data["strategic_number_inventory_metadata"] = inventory.get("metadata", {})
    value_inventory_path = inventory_path_for(path, "airef-value-family-inventory.json")
    if value_inventory_path.exists():
        inventory = json.loads(value_inventory_path.read_text(encoding="utf-8-sig"))
        data["value_family_inventory"] = inventory.get("families", [])
        data["value_family_inventory_metadata"] = inventory.get("metadata", {})
    object_inventory_path = inventory_path_for(path, "airef-object-inventory.json")
    if object_inventory_path.exists():
        inventory = json.loads(object_inventory_path.read_text(encoding="utf-8-sig"))
        data["object_inventory"] = inventory.get("objects", [])
        data["object_inventory_metadata"] = inventory.get("metadata", {})
    tech_inventory_path = inventory_path_for(path, "airef-tech-inventory.json")
    if tech_inventory_path.exists():
        inventory = json.loads(tech_inventory_path.read_text(encoding="utf-8-sig"))
        data["tech_inventory"] = inventory.get("techs", [])
        data["tech_inventory_metadata"] = inventory.get("metadata", {})
    xs_inventory_path = inventory_path_for(path, "xs-function-inventory.json")
    if xs_inventory_path.exists():
        inventory = json.loads(xs_inventory_path.read_text(encoding="utf-8-sig"))
        data["xs_function_inventory"] = inventory.get("functions", [])
        data["xs_function_inventory_metadata"] = inventory.get("metadata", {})
    xs_constant_inventory_path = inventory_path_for(path, "xs-constant-inventory.json")
    if xs_constant_inventory_path.exists():
        inventory = json.loads(xs_constant_inventory_path.read_text(encoding="utf-8-sig"))
        data["xs_constant_inventory"] = inventory.get("constants", [])
        data["xs_constant_inventory_metadata"] = inventory.get("metadata", {})
    rms_fixture_path = inventory_path_for(path, "rms-fixture-registry.json")
    if rms_fixture_path.exists():
        inventory = json.loads(rms_fixture_path.read_text(encoding="utf-8-sig"))
        data["rms_fixture_registry"] = inventory.get("fixtures", [])
        data["rms_fixture_registry_metadata"] = inventory.get("metadata", {})
    rms_topic_path = inventory_path_for(path, "rms-topic-inventory.json")
    if rms_topic_path.exists():
        inventory = json.loads(rms_topic_path.read_text(encoding="utf-8-sig"))
        data["rms_topic_inventory"] = inventory.get("topics", [])
        data["rms_topic_inventory_metadata"] = inventory.get("metadata", {})
    local_symbol_notes_path = inventory_path_for(path, "aoe2-ai-parser-local-symbol-notes.json")
    if local_symbol_notes_path.exists():
        inventory = json.loads(local_symbol_notes_path.read_text(encoding="utf-8-sig"))
        data["local_symbol_notes"] = inventory.get("symbols", [])
        data["local_symbol_notes_metadata"] = {
            "schema": inventory.get("schema", ""),
            "description": inventory.get("description", ""),
        }
    return data


def iter_registry_entries(data: dict[str, Any]) -> list[RegistryEntry]:
    entries: list[RegistryEntry] = []

    for concept in data.get("concepts", []):
        entries.append(
            RegistryEntry(
                kind="concept",
                entry_id=concept["id"],
                name=concept["name"],
                summary=concept.get("definition", ""),
                source_urls=tuple(concept.get("source_urls", [])),
                lookup_terms=tuple(concept.get("lookup_terms", [])),
                aliases=tuple(concept.get("aliases", [])),
                tags=tuple(concept.get("tags", [])),
                validation_status=concept.get("validation_status", "documented"),
            )
        )

    for article in data.get("articles", []):
        entries.append(
            RegistryEntry(
                kind="article",
                entry_id=article["id"],
                name=article["name"],
                summary=article.get("summary", ""),
                source_urls=(article["url"],),
                lookup_terms=tuple(article.get("lookup_terms", [])),
                aliases=tuple(article.get("aliases", [])),
                tags=tuple(article.get("tags", [])),
                validation_status=article.get("validation_status", "documented"),
            )
        )

    for command in data.get("validated_commands", []):
        entries.append(
            RegistryEntry(
                kind="validated-command",
                entry_id=command["id"],
                name=command["command_name"],
                summary="; ".join(command.get("validated_patterns", [])),
                source_urls=tuple(command.get("source_urls", [])),
                lookup_terms=tuple(command.get("lookup_terms", [])),
                aliases=tuple(command.get("aliases", [])),
                tags=tuple(
                    value
                    for value in ["validated-command", command.get("family_id", ""), *command.get("tags", [])]
                    if value
                ),
                validation_status=command.get("validation_status", "observed"),
            )
        )

    for command in data.get("project_command_notes", []):
        entries.append(
            RegistryEntry(
                kind="project-command-note",
                entry_id=command["id"],
                name=command["command_name"],
                summary="; ".join(command.get("validated_patterns", [])),
                source_urls=tuple(command.get("source_urls", [])),
                lookup_terms=tuple(command.get("lookup_terms", [])),
                aliases=tuple(command.get("aliases", [])),
                tags=tuple(
                    value
                    for value in ["project-command-note", command.get("family_id", ""), *command.get("tags", [])]
                    if value
                ),
                validation_status=command.get("validation_status", "mixed"),
            )
        )

    for command in data.get("command_inventory", []):
        categories = tuple(command.get("command_category", []))
        command_type = command.get("command_type", "")
        complexity = command.get("complexity", "")
        parameter_names = tuple(
            parameter.get("name", "")
            for parameter in command.get("command_parameters", [])
            if parameter.get("name")
        )
        related_commands = tuple(command.get("related_commands", []))
        entries.append(
            RegistryEntry(
                kind="command-inventory",
                entry_id=f"airef-command::{command['name']}",
                name=command["name"],
                summary=command.get("description", "") or command.get("short_description", ""),
                source_urls=tuple(url for url in [command.get("url", "")] if url),
                lookup_terms=(
                    command["name"],
                    command.get("syntax", ""),
                    command_type,
                    complexity,
                    *categories,
                    *parameter_names,
                    *related_commands,
                ),
                aliases=tuple(),
                tags=tuple(
                    value
                    for value in [
                        "command-inventory",
                        "airef-imported",
                        command_type,
                        complexity,
                        *categories,
                    ]
                    if value
                ),
                validation_status="airef-imported",
            )
        )

    for parameter in data.get("parameter_inventory", []):
        entries.append(
            RegistryEntry(
                kind="parameter-inventory",
                entry_id=f"airef-parameter::{parameter['name']}",
                name=parameter["name"],
                summary=parameter.get("description", "") or parameter.get("short_description", ""),
                source_urls=tuple(url for url in [parameter.get("url", "")] if url),
                lookup_terms=(
                    parameter["name"],
                    parameter.get("es_param_name", ""),
                    parameter.get("range", ""),
                    parameter.get("version", ""),
                    *parameter.get("related_parameters", []),
                    *parameter.get("used_in_commands", []),
                ),
                aliases=tuple(value for value in [parameter.get("es_param_name", "")] if value),
                tags=tuple(
                    value
                    for value in [
                        "parameter-inventory",
                        "airef-imported",
                        parameter.get("version", ""),
                    ]
                    if value
                ),
                validation_status="airef-imported",
            )
        )

    for strategic_number in data.get("strategic_number_inventory", []):
        status = strategic_number.get("status", "airef-imported")
        source_prefix = "binary-strategic-number" if status == "binary-only" else "airef-strategic-number"
        entries.append(
            RegistryEntry(
                kind="strategic-number-inventory",
                entry_id=f"{source_prefix}::{strategic_number['name']}",
                name=strategic_number["name"],
                summary=strategic_number.get("description", "") or strategic_number.get("short_description", ""),
                source_urls=tuple(url for url in [strategic_number.get("url", "")] if url),
                lookup_terms=(
                    strategic_number["name"],
                    str(strategic_number.get("sn_id", "")),
                    strategic_number.get("category", ""),
                    strategic_number.get("version", ""),
                    strategic_number.get("required_range", ""),
                    strategic_number.get("allowable_range", ""),
                    *strategic_number.get("supported_versions", []),
                    *strategic_number.get("linked_sns", []),
                    *strategic_number.get("related_sns", []),
                ),
                aliases=tuple(value for value in [strategic_number.get("aoe1_name", "")] if value),
                tags=tuple(
                    value
                    for value in [
                        "strategic-number-inventory",
                        status,
                        strategic_number.get("category", ""),
                        strategic_number.get("version", ""),
                        *strategic_number.get("supported_versions", []),
                    ]
                    if value
                ),
                validation_status=status,
            )
        )

    for family in data.get("value_family_inventory", []):
        family_id = f"airef-value-family::{family['parameter_name']}::{family['family_type']}"
        entries.append(
            RegistryEntry(
                kind="value-family",
                entry_id=family_id,
                name=f"{family['parameter_name']} {family['family_type']}",
                summary=family.get("description", ""),
                source_urls=(f"https://airef.github.io/parameters/parameters-details.html#{family['parameter_name']}",),
                lookup_terms=(family["parameter_name"], family["family_type"]),
                aliases=tuple(),
                tags=("value-family", "airef-imported", family["parameter_name"], family["family_type"]),
                validation_status="airef-imported",
            )
        )
        for item in family.get("entries", []):
            aliases = tuple(item.get("aliases", [])) if isinstance(item.get("aliases", []), list) else tuple()
            entries.append(
                RegistryEntry(
                    kind="value-entry",
                    entry_id=f"{family_id}::{item.get('name', '')}",
                    name=str(item.get("name", "")),
                    summary=str(item.get("description", "")),
                    source_urls=(f"https://airef.github.io/parameters/parameters-details.html#{family['parameter_name']}",),
                    lookup_terms=tuple(
                        str(value)
                        for value in [
                            item.get("name", ""),
                            item.get("id", ""),
                            item.get("de_id", ""),
                            item.get("parameter", ""),
                            item.get("players", ""),
                            family["parameter_name"],
                            family["family_type"],
                        ]
                        if str(value)
                    ),
                    aliases=aliases,
                    tags=("value-entry", "airef-imported", family["parameter_name"], family["family_type"]),
                    validation_status="airef-imported",
                )
            )

    for obj in data.get("object_inventory", []):
        entries.append(
            RegistryEntry(
                kind="object-inventory",
                entry_id=f"airef-object::{obj['name']}::{obj['object_id']}",
                name=obj["name"],
                summary=f"{obj.get('ai_name', '')} {obj.get('object_class', '')} {obj.get('building', '')}".strip(),
                source_urls=("https://airef.github.io/tables/objects.html",),
                lookup_terms=tuple(
                    str(value)
                    for value in [
                        obj.get("name", ""),
                        obj.get("ai_name", ""),
                        obj.get("object_id", ""),
                        obj.get("object_class", ""),
                        obj.get("cmd_id", ""),
                        obj.get("building", ""),
                        obj.get("group_name", ""),
                        obj.get("line", ""),
                        obj.get("dataset", ""),
                    ]
                    if str(value)
                ),
                aliases=tuple(value for value in [obj.get("ai_name", ""), obj.get("line", "")] if value),
                tags=("object-inventory", "airef-imported", obj.get("building", ""), obj.get("cmd_id", "")),
                validation_status="airef-imported",
            )
        )

    for tech in data.get("tech_inventory", []):
        entries.append(
            RegistryEntry(
                kind="tech-inventory",
                entry_id=f"airef-tech::{tech['name']}::{tech['tech_id']}",
                name=tech["name"],
                summary=f"{tech.get('ai_name', '')} {tech.get('building', '')} civ:{tech.get('civilization', '')}".strip(),
                source_urls=("https://airef.github.io/tables/techs.html",),
                lookup_terms=tuple(
                    str(value)
                    for value in [
                        tech.get("name", ""),
                        tech.get("ai_name", ""),
                        tech.get("tech_id", ""),
                        tech.get("building", ""),
                        tech.get("group_name", ""),
                        tech.get("civilization", ""),
                        tech.get("dataset", ""),
                    ]
                    if str(value)
                ),
                aliases=tuple(value for value in [tech.get("ai_name", "")] if value),
                tags=("tech-inventory", "airef-imported", tech.get("building", "")),
                validation_status="airef-imported",
            )
        )

    for function in data.get("xs_function_inventory", []):
        entries.append(
            RegistryEntry(
                kind="xs-function-inventory",
                entry_id=f"xs-function::{function['name']}",
                name=function["name"],
                summary=function.get("description", "") or function.get("notes", ""),
                source_urls=tuple(url for url in [function.get("source", "")] if url),
                lookup_terms=tuple(
                    str(value)
                    for value in [
                        function.get("name", ""),
                        function.get("signature", ""),
                        function.get("prototype", ""),
                        function.get("return_type", ""),
                        function.get("category", ""),
                        function.get("ai_context_status", ""),
                        *function.get("parameters", []),
                        *function.get("contexts", []),
                    ]
                    if str(value)
                ),
                aliases=tuple(),
                tags=tuple(
                    value
                    for value in [
                        "xs-function-inventory",
                        function.get("category", ""),
                        function.get("ai_context_status", ""),
                    ]
                    if value
                ),
                validation_status=function.get("ai_context_status", "documented"),
            )
        )

    for constant in data.get("xs_constant_inventory", []):
        entries.append(
            RegistryEntry(
                kind="xs-constant-inventory",
                entry_id=f"xs-constant::{constant['name']}",
                name=constant["name"],
                summary=constant.get("description", ""),
                source_urls=tuple(url for url in [constant.get("source", "")] if url),
                lookup_terms=tuple(
                    str(value)
                    for value in [
                        constant.get("name", ""),
                        constant.get("category", ""),
                        constant.get("value_type", ""),
                        constant.get("value", ""),
                    ]
                    if str(value)
                ),
                aliases=tuple(),
                tags=tuple(
                    value
                    for value in [
                        "xs-constant-inventory",
                        constant.get("category", ""),
                        constant.get("value_type", ""),
                    ]
                    if value
                ),
                validation_status="ugc-imported",
            )
        )

    for fixture in data.get("rms_fixture_registry", []):
        entries.append(
            RegistryEntry(
                kind="rms-fixture",
                entry_id=f"rms-fixture::{fixture['name']}",
                name=fixture["name"],
                summary=fixture.get("summary", ""),
                source_urls=tuple(),
                lookup_terms=tuple(
                    str(value)
                    for value in [
                        fixture.get("name", ""),
                        fixture.get("title", ""),
                        fixture.get("map_type", ""),
                        fixture.get("recommended_probe", ""),
                        *fixture.get("create_objects", []),
                        *fixture.get("sections", []),
                        *fixture.get("tags", []),
                        *fixture.get("use_cases", []),
                    ]
                    if str(value)
                ),
                aliases=tuple(),
                tags=tuple(value for value in ["rms-fixture", *fixture.get("tags", [])] if value),
                validation_status="project-fixture",
            )
        )

    for topic in data.get("rms_topic_inventory", []):
        entries.append(
            RegistryEntry(
                kind="rms-topic-inventory",
                entry_id=f"rms-topic::{ ' > '.join(topic.get('path', [topic['name']])) }",
                name=topic["name"],
                summary=topic.get("summary", ""),
                source_urls=tuple(url for url in [topic.get("source", "")] if url),
                lookup_terms=tuple(
                    str(value)
                    for value in [
                        topic.get("name", ""),
                        *topic.get("path", []),
                    ]
                    if str(value)
                ),
                aliases=tuple(),
                tags=tuple(
                    value
                    for value in [
                        "rms-topic-inventory",
                        f"level-{topic.get('level', '')}",
                    ]
                    if value
                ),
                validation_status="guide-imported",
            )
        )

    for symbol in data.get("local_symbol_notes", []):
        notes = symbol.get("notes", [])
        if isinstance(notes, list):
            summary = " ".join(str(note) for note in notes)
        else:
            summary = str(notes)
        entries.append(
            RegistryEntry(
                kind="local-symbol-note",
                entry_id=f"local-symbol::{symbol['name']}",
                name=symbol["name"],
                summary=summary,
                source_urls=tuple(),
                lookup_terms=tuple(
                    str(value)
                    for value in [
                        symbol.get("name", ""),
                        symbol.get("kind", ""),
                        symbol.get("id", ""),
                        symbol.get("requires_defconst", ""),
                        symbol.get("builtin_train_target", ""),
                    ]
                    if str(value)
                ),
                aliases=tuple(symbol.get("aliases", [])) if isinstance(symbol.get("aliases", []), list) else tuple(),
                tags=tuple(
                    value
                    for value in [
                        "local-symbol-note",
                        symbol.get("kind", ""),
                        "requires-defconst" if symbol.get("requires_defconst") else "",
                        "builtin-train-target" if symbol.get("builtin_train_target") else "",
                    ]
                    if value
                ),
                validation_status=symbol.get("validation_status", "project-observed"),
            )
        )

    for family in data.get("local_binary_inventory", {}).get("families", []):
        entries.append(
            RegistryEntry(
                kind="binary-family",
                entry_id=family["id"],
                name=family["name"],
                summary=f"Local binary inventory family with {len(family.get('entries', []))} entries.",
                source_urls=tuple(),
                lookup_terms=tuple(family.get("entries", [])),
                aliases=tuple(),
                tags=tuple(
                    value
                    for value in ["binary-inventory", family.get("kind", "")]
                    if value
                ),
                validation_status="binary-sourced",
            )
        )
        for token in family.get("entries", []):
            entries.append(
                RegistryEntry(
                    kind="binary-token",
                    entry_id=f"{family['id']}::{token}",
                    name=token,
                    summary=f"Binary-sourced token from {family['name']}.",
                    source_urls=tuple(),
                    lookup_terms=(token, family["name"], family["id"]),
                    aliases=tuple(),
                    tags=tuple(
                        value
                        for value in [
                            "binary-inventory",
                            "binary-token",
                            family.get("kind", ""),
                            family["id"],
                        ]
                        if value
                    ),
                    validation_status="binary-sourced",
                )
            )

    taxonomies = data.get("taxonomies", {})
    for category in taxonomies.get("command_categories", []):
        entries.append(
            RegistryEntry(
                kind="command-category",
                entry_id=category["id"],
                name=category["name"],
                summary=category.get("definition", ""),
                source_urls=tuple(category.get("source_urls", [])),
                lookup_terms=tuple(category.get("lookup_terms", [])),
                aliases=tuple(category.get("aliases", [])),
                tags=tuple(category.get("tags", [])),
                validation_status=category.get("validation_status", "documented"),
            )
        )
    for category in taxonomies.get("command_types", []):
        entries.append(
            RegistryEntry(
                kind="command-type",
                entry_id=category["id"],
                name=category["name"],
                summary=category.get("definition", ""),
                source_urls=tuple(category.get("source_urls", [])),
                lookup_terms=tuple(category.get("lookup_terms", [])),
                aliases=tuple(category.get("aliases", [])),
                tags=tuple(category.get("tags", [])),
                validation_status=category.get("validation_status", "documented"),
            )
        )
    for category in taxonomies.get("command_complexities", []):
        entries.append(
            RegistryEntry(
                kind="command-complexity",
                entry_id=category["id"],
                name=category["name"],
                summary=category.get("definition", ""),
                source_urls=tuple(category.get("source_urls", [])),
                lookup_terms=tuple(category.get("lookup_terms", [])),
                aliases=tuple(category.get("aliases", [])),
                tags=tuple(category.get("tags", [])),
                validation_status=category.get("validation_status", "documented"),
            )
        )

    return entries


def search_registry(
    data: dict[str, Any],
    query: str,
    *,
    kinds: set[str] | None = None,
    limit: int = 20,
) -> list[RegistryEntry]:
    needle = query.casefold()
    matches: list[tuple[int, RegistryEntry]] = []
    include_binary = bool(kinds and kinds & BINARY_KINDS)

    for entry in iter_registry_entries(data):
        if kinds and entry.kind not in kinds:
            continue
        if entry.kind in BINARY_KINDS and not include_binary:
            continue

        haystacks = [
            entry.name,
            entry.entry_id,
            entry.summary,
            *entry.lookup_terms,
            *entry.aliases,
            *entry.tags,
        ]
        joined = " ".join(value.casefold() for value in haystacks if value)
        if needle not in joined:
            continue

        score = 0
        if needle == entry.entry_id.casefold():
            score += 100
        if needle == entry.name.casefold():
            score += 80
        if entry.kind == "validated-command":
            score += 35
        elif entry.kind == "command-inventory":
            score += 22
        elif entry.kind in {"parameter-inventory", "strategic-number-inventory", "value-entry", "object-inventory", "tech-inventory", "xs-function-inventory", "xs-constant-inventory", "rms-fixture", "rms-topic-inventory", "local-symbol-note"}:
            score += 20
        elif entry.kind == "value-family":
            score += 14
        elif entry.kind == "project-command-note":
            score += 12
        if needle in entry.name.casefold():
            score += 40
        if needle in entry.entry_id.casefold():
            score += 30
        score += sum(20 for term in entry.lookup_terms if needle == term.casefold())
        score += sum(10 for term in entry.lookup_terms if needle in term.casefold())
        score += sum(24 for alias in entry.aliases if needle == alias.casefold())
        score += sum(12 for alias in entry.aliases if needle in alias.casefold())
        score += sum(4 for tag in entry.tags if needle in tag.casefold())
        if needle in entry.summary.casefold():
            score += 5
        if (needle.startswith("up-") or needle.startswith("action-")) and entry.kind == "concept":
            if "duc" in entry.tags or entry.entry_id.startswith("duc-"):
                score += 15
            if entry.entry_id.startswith("duc-family-"):
                score += 20
        matches.append((score, entry))

    matches.sort(key=lambda item: (-item[0], item[1].kind, item[1].name.casefold()))
    return [entry for _, entry in matches[:limit]]


def _find_command_inventory(data: dict[str, Any], name: str) -> dict[str, Any] | None:
    return next((item for item in data.get("command_inventory", []) if item.get("name") == name), None)


def _find_parameter_inventory(data: dict[str, Any], name: str) -> dict[str, Any] | None:
    return next((item for item in data.get("parameter_inventory", []) if item.get("name") == name), None)


def _find_sn_inventory(data: dict[str, Any], name: str) -> dict[str, Any] | None:
    return next((item for item in data.get("strategic_number_inventory", []) if item.get("name") == name), None)


def _find_value_entry(data: dict[str, Any], entry_id: str) -> tuple[dict[str, Any], dict[str, Any]] | None:
    parts = entry_id.split("::")
    if len(parts) < 4:
        return None
    parameter_name = parts[1]
    family_type = parts[2]
    item_name = "::".join(parts[3:])
    for family in data.get("value_family_inventory", []):
        if family.get("parameter_name") == parameter_name and family.get("family_type") == family_type:
            for item in family.get("entries", []):
                if str(item.get("name", "")) == item_name:
                    return family, item
    return None


def _find_object_inventory(data: dict[str, Any], entry_id: str) -> dict[str, Any] | None:
    parts = entry_id.split("::")
    if len(parts) < 3:
        return None
    name = parts[1]
    object_id = parts[2]
    return next(
        (
            item
            for item in data.get("object_inventory", [])
            if item.get("name") == name and str(item.get("object_id")) == object_id
        ),
        None,
    )


def _find_tech_inventory(data: dict[str, Any], entry_id: str) -> dict[str, Any] | None:
    parts = entry_id.split("::")
    if len(parts) < 3:
        return None
    name = parts[1]
    tech_id = parts[2]
    return next(
        (
            item
            for item in data.get("tech_inventory", [])
            if item.get("name") == name and str(item.get("tech_id")) == tech_id
        ),
        None,
    )


def _find_xs_function_inventory(data: dict[str, Any], name: str) -> dict[str, Any] | None:
    return next((item for item in data.get("xs_function_inventory", []) if item.get("name") == name), None)


def _find_xs_constant_inventory(data: dict[str, Any], name: str) -> dict[str, Any] | None:
    return next((item for item in data.get("xs_constant_inventory", []) if item.get("name") == name), None)


def _find_rms_fixture(data: dict[str, Any], name: str) -> dict[str, Any] | None:
    return next((item for item in data.get("rms_fixture_registry", []) if item.get("name") == name), None)


def _find_rms_topic(data: dict[str, Any], entry_id: str) -> dict[str, Any] | None:
    path = entry_id.split("::", 1)[1] if "::" in entry_id else ""
    return next(
        (
            item
            for item in data.get("rms_topic_inventory", [])
            if " > ".join(item.get("path", [item.get("name", "")])) == path
        ),
        None,
    )


def _find_local_symbol_note(data: dict[str, Any], name: str) -> dict[str, Any] | None:
    return next((item for item in data.get("local_symbol_notes", []) if item.get("name") == name), None)


def entry_details(data: dict[str, Any], entry: RegistryEntry) -> dict[str, Any]:
    if entry.kind == "command-inventory":
        item = _find_command_inventory(data, entry.name)
        if not item:
            return {}
        return {
            "syntax": item.get("syntax", ""),
            "command_type": item.get("command_type", ""),
            "complexity": item.get("complexity", ""),
            "categories": item.get("command_category", []),
            "parameters": [param.get("name", "") for param in item.get("command_parameters", []) if param.get("name")],
            "related_commands": item.get("related_commands", []),
            "related_strategic_numbers": item.get("related_strategic_numbers", []),
        }
    if entry.kind == "parameter-inventory":
        item = _find_parameter_inventory(data, entry.name)
        if not item:
            return {}
        return {
            "range": item.get("range", ""),
            "version": item.get("version", ""),
            "es_param_name": item.get("es_param_name", ""),
            "related_parameters": item.get("related_parameters", []),
            "used_in_commands": item.get("used_in_commands", []),
        }
    if entry.kind == "strategic-number-inventory":
        item = _find_sn_inventory(data, entry.name)
        if not item:
            return {}
        return {
            "sn_id": item.get("sn_id", ""),
            "default_value": item.get("default_value", ""),
            "required_range": item.get("required_range", ""),
            "allowable_range": item.get("allowable_range", ""),
            "category": item.get("category", ""),
            "version": item.get("version", ""),
            "linked_sns": item.get("linked_sns", []),
            "related_sns": item.get("related_sns", []),
        }
    if entry.kind == "value-entry":
        resolved = _find_value_entry(data, entry.entry_id)
        if not resolved:
            return {}
        family, item = resolved
        return {
            "parameter_name": family.get("parameter_name", ""),
            "family_type": family.get("family_type", ""),
            "id": item.get("id", ""),
            "legacy_id": item.get("legacy_id", ""),
            "de_id": item.get("de_id", ""),
            "id_source": item.get("id_source", ""),
            "aliases": item.get("aliases", []),
            "parameter": item.get("parameter", ""),
            "players": item.get("players", ""),
        }
    if entry.kind == "object-inventory":
        item = _find_object_inventory(data, entry.entry_id)
        if not item:
            return {}
        return {
            "object_id": item.get("object_id", ""),
            "ai_name": item.get("ai_name", ""),
            "line": item.get("line", ""),
            "object_class": item.get("object_class", ""),
            "cmd_id": item.get("cmd_id", ""),
            "building": item.get("building", ""),
            "group_name": item.get("group_name", ""),
            "age": item.get("age", ""),
            "dataset": item.get("dataset", ""),
        }
    if entry.kind == "tech-inventory":
        item = _find_tech_inventory(data, entry.entry_id)
        if not item:
            return {}
        return {
            "tech_id": item.get("tech_id", ""),
            "ai_name": item.get("ai_name", ""),
            "building": item.get("building", ""),
            "group_name": item.get("group_name", ""),
            "age": item.get("age", ""),
            "civilization": item.get("civilization", ""),
            "cost": item.get("cost", ""),
            "time": item.get("time", ""),
            "dataset": item.get("dataset", ""),
        }
    if entry.kind == "xs-function-inventory":
        item = _find_xs_function_inventory(data, entry.name)
        if not item:
            return {}
        return {
            "signature": item.get("signature", ""),
            "prototype": item.get("prototype", ""),
            "return_type": item.get("return_type", ""),
            "parameters": item.get("parameters", []),
            "category": item.get("category", ""),
            "ai_context_status": item.get("ai_context_status", ""),
            "offset": item.get("offset", ""),
            "notes": item.get("notes", ""),
            "contexts": item.get("contexts", []),
            "examples": item.get("examples", []),
            "secondary_sources": item.get("secondary_sources", []),
        }
    if entry.kind == "xs-constant-inventory":
        item = _find_xs_constant_inventory(data, entry.name)
        if not item:
            return {}
        return {
            "category": item.get("category", ""),
            "value_type": item.get("value_type", ""),
            "value": item.get("value", ""),
        }
    if entry.kind == "rms-fixture":
        item = _find_rms_fixture(data, entry.name)
        if not item:
            return {}
        return {
            "path": item.get("path", ""),
            "title": item.get("title", ""),
            "map_type": item.get("map_type", ""),
            "recommended_probe": item.get("recommended_probe", ""),
            "create_objects": item.get("create_objects", []),
            "sections": item.get("sections", []),
            "use_cases": item.get("use_cases", []),
        }
    if entry.kind == "rms-topic-inventory":
        item = _find_rms_topic(data, entry.entry_id)
        if not item:
            return {}
        return {
            "path": item.get("path", []),
            "level": item.get("level", ""),
        }
    if entry.kind == "local-symbol-note":
        item = _find_local_symbol_note(data, entry.name)
        if not item:
            return {}
        return {
            "kind": item.get("kind", ""),
            "id": item.get("id", ""),
            "requires_defconst": item.get("requires_defconst", ""),
            "builtin_train_target": item.get("builtin_train_target", ""),
            "notes": item.get("notes", []),
        }
    return {}


def resolve_reference(
    data: dict[str, Any],
    query: str,
    *,
    limit: int = 6,
    kinds: set[str] | None = None,
) -> ResolvedReference:
    matches = search_registry(data, query, kinds=kinds, limit=max(limit + 6, 12))
    if not matches and kinds is None:
        matches = search_registry(data, query, kinds=BINARY_KINDS, limit=max(limit + 6, 12))
    primary = matches[0] if matches else None
    if primary is None:
        return ResolvedReference(primary=None, related=tuple(), details={})
    related = tuple(
        entry
        for entry in matches[1:]
        if entry.entry_id != primary.entry_id
    )[:limit]
    return ResolvedReference(
        primary=primary,
        related=related,
        details=entry_details(data, primary),
    )
