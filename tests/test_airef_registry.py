from __future__ import annotations

import json
from pathlib import Path
import unittest
from uuid import uuid4

from aoe2_ai_lab.airef_registry import (
    iter_registry_entries,
    load_registry,
    resolve_reference,
    search_registry,
)


class WorkspaceTempDir:
    def __enter__(self) -> Path:
        self.path = Path("tests") / ".tmp" / uuid4().hex
        self.path.mkdir(parents=True, exist_ok=False)
        return self.path

    def __exit__(self, exc_type, exc, tb) -> None:
        for child in sorted(self.path.rglob("*"), reverse=True):
            if child.is_file():
                child.unlink()
            elif child.is_dir():
                child.rmdir()
        self.path.rmdir()


class AirefRegistryTests(unittest.TestCase):
    def test_search_registry_matches_concepts_and_articles(self) -> None:
        registry = {
            "concepts": [
                {
                    "id": "compare-op",
                    "name": "compareOp",
                    "definition": "Comparison operators.",
                    "source_urls": ["https://example.test/compare"],
                    "lookup_terms": ["g:>", "s:>"],
                    "aliases": ["comparison operator"],
                    "tags": ["operator", "parameter"],
                    "validation_status": "documented",
                }
            ],
            "articles": [
                {
                    "id": "intro-to-commands",
                    "name": "Intro to Commands",
                    "summary": "Command syntax primer.",
                    "url": "https://example.test/intro",
                    "lookup_terms": ["syntax"],
                    "aliases": ["command primer"],
                    "tags": ["guide"],
                }
            ],
            "taxonomies": {},
        }

        compare_matches = search_registry(registry, "compare")
        self.assertEqual(compare_matches[0].entry_id, "compare-op")

        alias_matches = search_registry(registry, "comparison")
        self.assertEqual(alias_matches[0].entry_id, "compare-op")

        syntax_matches = search_registry(registry, "syntax", kinds={"article"})
        self.assertEqual([match.entry_id for match in syntax_matches], ["intro-to-commands"])

    def test_load_registry_and_iter_entries_support_taxonomies(self) -> None:
        registry = {
            "concepts": [],
            "articles": [],
            "taxonomies": {
                "command_categories": [
                    {
                        "id": "economy",
                        "name": "Economy",
                        "definition": "Economy commands.",
                        "source_urls": ["https://example.test/economy"],
                        "lookup_terms": ["villager", "gather"],
                        "aliases": ["eco"],
                        "tags": ["command-taxonomy"],
                    }
                ],
                "command_types": [],
                "command_complexities": [],
            },
        }

        with WorkspaceTempDir() as tmp:
            path = tmp / "registry.json"
            path.write_text(json.dumps(registry), encoding="utf-8")

            loaded = load_registry(path)
            entries = iter_registry_entries(loaded)

        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].kind, "command-category")
        self.assertEqual(entries[0].entry_id, "economy")
        self.assertEqual(entries[0].aliases, ("eco",))

    def test_search_registry_prefers_exact_lookup_term_for_duc_command(self) -> None:
        registry = {
            "concepts": [
                {
                    "id": "performance-benchmarks",
                    "name": "Performance Benchmarks",
                    "definition": "Mentions up-target-point in broader notes.",
                    "source_urls": ["https://example.test/perf"],
                    "lookup_terms": ["up-target-point"],
                },
                {
                    "id": "duc-family-point-targeting",
                    "name": "DUC Point Targeting",
                    "definition": "Point targeting family.",
                    "source_urls": ["https://example.test/point"],
                    "lookup_terms": ["up-target-point", "action-move"],
                    "tags": ["duc", "point"],
                },
            ],
            "articles": [],
            "taxonomies": {},
        }

        matches = search_registry(registry, "up-target-point")
        self.assertEqual(matches[0].entry_id, "duc-family-point-targeting")

    def test_search_registry_separates_validated_and_project_note_commands(self) -> None:
        registry = {
            "concepts": [],
            "articles": [],
            "validated_commands": [],
            "project_command_notes": [
                {
                    "id": "cmd-up-target-point",
                    "command_name": "up-target-point",
                    "family_id": "duc-family-point-targeting",
                    "validated_patterns": ["Use a rebuilt local list before point movement."],
                    "lookup_terms": ["up-target-point", "action-move"],
                    "validation_status": "mixed",
                }
            ],
            "taxonomies": {},
        }

        validated_matches = search_registry(registry, "up-target-point", kinds={"validated-command"})
        self.assertEqual(validated_matches, [])

        note_matches = search_registry(registry, "up-target-point", kinds={"project-command-note"})
        self.assertEqual(note_matches[0].entry_id, "cmd-up-target-point")

    def test_search_registry_emits_binary_tokens(self) -> None:
        registry = {
            "concepts": [],
            "articles": [],
            "validated_commands": [],
            "local_binary_inventory": {
                "families": [
                    {
                        "id": "binary-target-actions",
                        "name": "Target Actions",
                        "kind": "binary-action-family",
                        "entries": ["action-garrison", "action-move"],
                    }
                ]
            },
            "taxonomies": {},
        }

        matches = search_registry(registry, "action-garrison", kinds={"binary-token"})
        self.assertEqual(matches[0].name, "action-garrison")

    def test_binary_tokens_are_hidden_from_default_search_but_resolve_as_fallback(self) -> None:
        registry = {
            "concepts": [],
            "articles": [],
            "validated_commands": [],
            "local_binary_inventory": {
                "families": [
                    {
                        "id": "binary-target-actions",
                        "name": "Target Actions",
                        "kind": "binary-action-family",
                        "entries": ["binary-only-action"],
                    }
                ]
            },
            "taxonomies": {},
        }

        self.assertEqual(search_registry(registry, "binary-only-action"), [])

        resolved = resolve_reference(registry, "binary-only-action")
        self.assertEqual(resolved.primary.kind, "binary-token")
        self.assertEqual(resolved.primary.name, "binary-only-action")

    def test_load_registry_includes_command_inventory_when_present(self) -> None:
        registry = {
            "concepts": [],
            "articles": [],
            "taxonomies": {},
        }
        inventory = {
            "metadata": {"command_count": 1},
            "commands": [
                {
                    "name": "up-target-point",
                    "url": "https://airef.github.io/commands/commands-details.html#up-target-point",
                    "description": "Direct local search results to a specific point on the map.",
                    "syntax": "(up-target-point <Point> <DUCAction>)",
                    "command_type": "Action",
                    "complexity": "Very High",
                    "command_category": ["DUC", "Points"],
                    "command_parameters": [{"name": "Point"}, {"name": "DUCAction"}],
                    "related_commands": ["up-target-objects"],
                }
            ],
        }

        with WorkspaceTempDir() as tmp:
            path = tmp / "airef-site-registry.json"
            inventory_path = tmp / "airef-command-inventory.json"
            path.write_text(json.dumps(registry), encoding="utf-8")
            inventory_path.write_text(json.dumps(inventory), encoding="utf-8")

            loaded = load_registry(path)
            matches = search_registry(loaded, "up-target-point", kinds={"command-inventory"})

        self.assertEqual(matches[0].entry_id, "airef-command::up-target-point")
        self.assertEqual(matches[0].validation_status, "airef-imported")

    def test_search_registry_prefers_validated_command_over_imported_inventory(self) -> None:
        registry = {
            "concepts": [],
            "articles": [],
            "validated_commands": [
                {
                    "id": "cmd-up-target-point",
                    "command_name": "up-target-point",
                    "validated_patterns": ["Observed point targeting path."],
                    "lookup_terms": ["up-target-point"],
                    "validation_status": "observed",
                }
            ],
            "command_inventory": [
                {
                    "name": "up-target-point",
                    "url": "https://airef.github.io/commands/commands-details.html#up-target-point",
                    "description": "Direct local search results to a specific point on the map.",
                    "syntax": "(up-target-point <Point> <DUCAction>)",
                    "command_type": "Action",
                    "complexity": "Very High",
                    "command_category": ["DUC", "Points"],
                    "command_parameters": [{"name": "Point"}, {"name": "DUCAction"}],
                    "related_commands": ["up-target-objects"],
                }
            ],
            "taxonomies": {},
        }

        matches = search_registry(registry, "up-target-point")
        self.assertEqual(matches[0].kind, "validated-command")

    def test_search_registry_supports_parameter_and_sn_inventory(self) -> None:
        registry = {
            "concepts": [],
            "articles": [],
            "parameter_inventory": [
                {
                    "name": "BuildingId",
                    "url": "https://airef.github.io/parameters/parameters-details.html#BuildingId",
                    "description": "A building object.",
                    "short_description": "A building object.",
                    "range": "A valid building ID.",
                    "version": "AoC",
                    "es_param_name": "<building>",
                    "related_parameters": ["UnitId"],
                    "used_in_commands": ["build"],
                }
            ],
            "strategic_number_inventory": [
                {
                    "name": "sn-target-point-adjustment",
                    "url": "https://airef.github.io/strategic-numbers/sn-details.html#sn-target-point-adjustment",
                    "description": "Adjusts target points.",
                    "short_description": "Adjusts target points.",
                    "sn_id": 292,
                    "category": "Other",
                    "version": "UP",
                    "required_range": "0 to 6",
                    "allowable_range": "Min to Max",
                    "linked_sns": [],
                    "related_sns": [],
                    "aoe1_name": "",
                }
            ],
            "taxonomies": {},
        }

        parameter_matches = search_registry(registry, "BuildingId", kinds={"parameter-inventory"})
        sn_matches = search_registry(registry, "sn-target-point-adjustment", kinds={"strategic-number-inventory"})

        self.assertEqual(parameter_matches[0].entry_id, "airef-parameter::BuildingId")
        self.assertEqual(sn_matches[0].entry_id, "airef-strategic-number::sn-target-point-adjustment")

    def test_resolve_reference_returns_primary_details_and_related(self) -> None:
        registry = {
            "validated_commands": [
                {
                    "id": "cmd-up-target-point",
                    "command_name": "up-target-point",
                    "validated_patterns": ["Observed point targeting path."],
                    "lookup_terms": ["up-target-point"],
                    "validation_status": "observed",
                }
            ],
            "command_inventory": [
                {
                    "name": "up-target-point",
                    "url": "https://airef.github.io/commands/commands-details.html#up-target-point",
                    "description": "Direct local search results to a specific point on the map.",
                    "syntax": "(up-target-point <Point> <DUCAction>)",
                    "command_type": "Action",
                    "complexity": "Very High",
                    "command_category": ["DUC", "Points"],
                    "command_parameters": [{"name": "Point"}, {"name": "DUCAction"}],
                    "related_commands": ["up-target-objects"],
                    "related_strategic_numbers": ["sn-target-point-adjustment"],
                }
            ],
            "project_command_notes": [
                {
                    "id": "note-up-target-point",
                    "command_name": "up-target-point",
                    "validated_patterns": ["Mixed point movement notes."],
                    "lookup_terms": ["up-target-point"],
                    "validation_status": "mixed",
                }
            ],
            "concepts": [],
            "articles": [],
            "taxonomies": {},
        }

        resolved = resolve_reference(registry, "up-target-point")
        self.assertEqual(resolved.primary.kind, "validated-command")
        self.assertEqual(resolved.related[0].kind, "command-inventory")

        inventory_only = resolve_reference(registry, "up-target-point", kinds={"command-inventory"})
        self.assertEqual(inventory_only.primary.kind, "command-inventory")
        self.assertEqual(inventory_only.details["syntax"], "(up-target-point <Point> <DUCAction>)")

    def test_search_registry_supports_value_object_and_tech_inventory(self) -> None:
        registry = {
            "value_family_inventory": [
                {
                    "parameter_name": "DUCAction",
                    "family_type": "value-list",
                    "description": "DUC actions.",
                    "entries": [{"name": "action-garrison", "id": 7, "description": "Garrison units."}],
                }
            ],
            "object_inventory": [
                {
                    "name": "Archer",
                    "ai_name": "archer",
                    "object_id": 4,
                    "object_class": "archery-class (900)",
                    "cmd_id": "cmdid-military",
                    "building": "Archery Range",
                    "group_name": "Archery Range",
                    "line": "-291",
                }
            ],
            "tech_inventory": [
                {
                    "name": "Fletching",
                    "ai_name": "fletching",
                    "tech_id": 199,
                    "building": "Blacksmith",
                    "group_name": "Blacksmith",
                    "civilization": "",
                }
            ],
            "taxonomies": {},
        }
        action_matches = search_registry(registry, "action-garrison", kinds={"value-entry"})
        object_matches = search_registry(registry, "Archer", kinds={"object-inventory"})
        tech_matches = search_registry(registry, "Fletching", kinds={"tech-inventory"})
        self.assertEqual(action_matches[0].kind, "value-entry")
        self.assertEqual(object_matches[0].entry_id, "airef-object::Archer::4")
        self.assertEqual(tech_matches[0].entry_id, "airef-tech::Fletching::199")

    def test_search_registry_supports_xs_and_rms_inventories(self) -> None:
        registry = {
            "xs_function_inventory": [
                {
                    "name": "xsChatData",
                    "signature": "void xsChatData(const char* text, int32_t value)",
                    "return_type": "void",
                    "parameters": ["const char* text", "int32_t value"],
                    "description": "Send debug chat.",
                    "category": "debug",
                    "ai_context_status": "observed-working-in-ai-context",
                    "source": "docs/extracted/raw/aoe2de/aoe2de-xs-function-signatures.txt",
                    "notes": "Observed working from AI XS.",
                }
            ],
            "xs_constant_inventory": [
                {
                    "name": "cNomad",
                    "category": "Map Types",
                    "value_type": "int",
                    "value": "33",
                    "description": "Nomad map type.",
                    "source": "https://ugc.aoe2.rocks/general/xs/constants/constants/#112-cnomad",
                }
            ],
            "rms_fixture_registry": [
                {
                    "name": "rms_test_tc_transport.rms",
                    "title": "rms_test_tc_transport",
                    "summary": "Minimal TC garrison fixture.",
                    "map_type": "ARABIA",
                    "create_objects": ["TOWN_CENTER", "VILLAGER"],
                    "sections": ["PLAYER_SETUP", "OBJECTS_GENERATION"],
                    "tags": ["tc-transport", "villager", "fixture"],
                    "use_cases": ["villager-to-TC garrison"],
                    "recommended_probe": "ai/tc_transport_probe",
                }
            ],
            "rms_topic_inventory": [
                {
                    "name": "Conditionals",
                    "level": 2,
                    "path": ["Syntax Overview", "Conditionals"],
                    "summary": "Conditional logic reference.",
                    "source": "docs/extracted/raw/rms/rms-reference-google-doc.txt",
                }
            ],
            "taxonomies": {},
        }
        xs_matches = search_registry(registry, "xsChatData", kinds={"xs-function-inventory"})
        xs_constant_matches = search_registry(registry, "cNomad", kinds={"xs-constant-inventory"})
        rms_matches = search_registry(registry, "tc-transport", kinds={"rms-fixture"})
        rms_topic_matches = search_registry(registry, "Conditionals", kinds={"rms-topic-inventory"})
        self.assertEqual(xs_matches[0].entry_id, "xs-function::xsChatData")
        self.assertEqual(xs_constant_matches[0].entry_id, "xs-constant::cNomad")
        self.assertEqual(rms_matches[0].entry_id, "rms-fixture::rms_test_tc_transport.rms")
        self.assertEqual(rms_topic_matches[0].entry_id, "rms-topic::Syntax Overview > Conditionals")


if __name__ == "__main__":
    unittest.main()
