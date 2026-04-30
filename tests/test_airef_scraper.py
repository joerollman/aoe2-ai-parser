from __future__ import annotations

from pathlib import Path
import unittest
from uuid import uuid4

from aoe2_ai_lab.airef_scraper import (
    parse_rms_fixture,
    parse_rms_guide_topics,
    parse_objects_js,
    parse_commands_js,
    parse_parameters_js,
    parse_strategic_numbers_js,
    parse_techs_js,
    parse_ugc_xs_constants_html,
    parse_value_families_from_parameters,
    parse_xs_function_inventory,
)
from aoe2_ai_lab.airef_registry import search_registry


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


class AirefScraperTests(unittest.TestCase):
    def test_parse_commands_js_extracts_command_metadata(self) -> None:
        source = r'''
        var cBuild = new Command("build","Action","AoC");
        var cUpTargetPoint = new Command("up-target-point","Action","UP");
        cBuild.shortDescription = "Builds the given building.";
        cBuild.description = "Builds the given building if " + cUpTargetPoint.getLink() + " is not needed.";
        cBuild.commandParameters = [ {
            nameLink: pBuildingId.getLink(),
            name: "BuildingId",
            type: "Const",
            dir: "in",
            range: "A BuildingId.",
            note: "The building that will be constructed."
        } ];
        cBuild.example = [ {
            title: "Basic example",
            data: "(build house)"
        } ];
        cBuild.commandCategory = ["Buildings"];
        cBuild.relatedCommands = [cUpTargetPoint];
        cBuild.relatedSNs = [snMaximumTownSize];
        cBuild.complexity = "Low";
        '''

        commands = parse_commands_js(source)
        self.assertEqual(len(commands), 2)

        build = next(command for command in commands if command.name == "build")
        self.assertEqual(build.short_description, "Builds the given building.")
        self.assertIn("up-target-point", build.description)
        self.assertEqual(build.command_parameters[0]["name"], "BuildingId")
        self.assertEqual(build.command_category, ["Buildings"])
        self.assertEqual(build.related_commands, ["up-target-point"])
        self.assertEqual(build.related_strategic_numbers, ["snMaximumTownSize"])
        self.assertEqual(build.complexity, "Low")
        self.assertEqual(build.syntax, "(build <BuildingId>)")
        self.assertEqual(build.code_blocks, ["(build house)"])

    def test_parse_parameters_js_extracts_parameter_metadata(self) -> None:
        source = r'''
        class Parameter {}
        var cBuild = new Command("build","Action","AoC");
        var pBuildingId = new Parameter("BuildingId","AoC","&#60;building&#62;");
        pBuildingId.description = "A building object.";
        pBuildingId.shortDescription = "A building object.";
        pBuildingId.range = "A valid building ID.";
        pBuildingId.relatedParams = [pUnitId, pObjectId];
        pBuildingId.valueList = [ { name: "house", id: 70, description: "House." } ];
        pBuildingId.wildcardParam = [ { name: "watch-tower-line", id: -398, description: "Tower line." } ];
        cBuild.commandParameters = [ {
            nameLink: pBuildingId.getLink(),
            name: "BuildingId",
            type: "Const",
            dir: "in",
            range: "A BuildingId.",
            note: "The building."
        } ];
        '''
        parameters = parse_parameters_js(source)
        building_id = next(parameter for parameter in parameters if parameter.name == "BuildingId")
        self.assertEqual(building_id.es_param_name, "<building>")
        self.assertEqual(building_id.used_in_commands, ["build"])
        self.assertEqual(building_id.value_list[0]["name"], "house")
        self.assertEqual(building_id.wildcard_parameters[0]["name"], "watch-tower-line")

    def test_parse_strategic_numbers_js_extracts_sn_metadata(self) -> None:
        source = r'''
        var cUpTargetPoint = new Command("up-target-point","Action","UP");
        var snTargetPointAdjustment = new StrategicNumber("unused");
        snTargetPointAdjustment.id = 292;
        snTargetPointAdjustment.snName = "sn-target-point-adjustment";
        snTargetPointAdjustment.snNameAoE1 = "";
        snTargetPointAdjustment.default = 0;
        snTargetPointAdjustment.category = "Other";
        snTargetPointAdjustment.min = "Min";
        snTargetPointAdjustment.max = "Max";
        snTargetPointAdjustment.rmin = 0;
        snTargetPointAdjustment.rmax = 6;
        snTargetPointAdjustment.network = 0;
        snTargetPointAdjustment.defined = 1;
        snTargetPointAdjustment.available = 0;
        snTargetPointAdjustment.effective = 1;
        snTargetPointAdjustment.version = "UP";
        snTargetPointAdjustment.aoe = 0;
        snTargetPointAdjustment.aoc = 0;
        snTargetPointAdjustment.up = 1;
        snTargetPointAdjustment.de = 1;
        snTargetPointAdjustment.linked = [];
        snTargetPointAdjustment.related = [];
        snTargetPointAdjustment.shortDescription = "Adjusts target points.";
        snTargetPointAdjustment.description = "Adjusts " + cUpTargetPoint.getLink() + " target points.";
        '''
        strategic_numbers = parse_strategic_numbers_js(source)
        sn = strategic_numbers[0]
        self.assertEqual(sn.name, "sn-target-point-adjustment")
        self.assertEqual(sn.sn_id, 292)
        self.assertEqual(sn.required_range, "0 to 6")
        self.assertEqual(sn.version, "UP")
        self.assertEqual(sn.supported_versions, ["UP", "DE"])
        self.assertEqual(sn.de, 1)
        self.assertIn("up-target-point", sn.description)

    def test_parse_value_families_derives_operator_and_value_entries(self) -> None:
        source = r'''
        var pCompareOp = new Parameter("compareOp","AoC","&#60;rel-op&#62;");
        pCompareOp.shortDescription = "Comparison operators.";
        pCompareOp.operatorTypes = [ {
            operator: ["c:&#60;", "&#60;", "less-than"],
            id: 0,
            deId: "0,18",
            description: "Less than."
        } ];
        var pDUCAction = new Parameter("DUCAction","UP");
        pDUCAction.shortDescription = "DUC actions.";
        pDUCAction.valueList = [ {
            name: "action-garrison",
            id: 7,
            description: "Garrison units."
        } ];
        '''
        parameters = parse_parameters_js(source)
        families = parse_value_families_from_parameters(parameters)
        self.assertEqual(len(families), 2)
        compare_family = next(family for family in families if family.parameter_name == "compareOp")
        duc_family = next(family for family in families if family.parameter_name == "DUCAction")
        self.assertEqual(compare_family.entries[0]["name"], "c:<")
        self.assertEqual(compare_family.entries[0]["id"], "0,18")
        self.assertEqual(compare_family.entries[0]["legacy_id"], "0")
        self.assertEqual(compare_family.entries[0]["de_id"], "0,18")
        self.assertEqual(compare_family.entries[0]["id_source"], "de_id")
        self.assertEqual(duc_family.entries[0]["name"], "action-garrison")

    def test_parse_objects_and_techs_js_extracts_flattened_entries(self) -> None:
        source = r'''
        rangeTechsArray = [ {
            name: "Fletching",
            id: 199,
            aiName: "fletching",
            building: "Archery Range",
            age: 2,
            civ: "",
            aok: 1,
            tc: 1,
            wk: 1,
            de: 1,
            notes: ""
        } ];
        techsArray = [rangeTechsArray];
        techsBuildingsArray = ["Archery Range"];

        objectsRangeArray = [ {
            name: "Archer",
            aiName: "archer",
            line: "-291",
            id: 4,
            class: "archery-class (900)",
            cmdId: "cmdid-military",
            building: "Archery Range",
            age: 2,
            deadUnit: "5",
            projectile: "6",
            aok: 1,
            tc: 1,
            wk: 1,
            de: 1,
            notes: ""
        } ];
        objectsArray = [objectsRangeArray];
        objectsBuildingNamesArray = ["Archery Range"];
        '''
        objects = parse_objects_js(source)
        techs = parse_techs_js(source)
        self.assertEqual(objects[0].name, "Archer")
        self.assertEqual(objects[0].group_name, "Archery Range")
        self.assertEqual(techs[0].name, "Fletching")
        self.assertEqual(techs[0].group_name, "Archery Range")

    def test_parse_xs_function_inventory_extracts_signature_and_status(self) -> None:
        names = "100:xsChatData\n200:xsCreateFile\n"
        signatures = "100:void xsChatData(const char* text, int32_t value): Sends chat.\n"
        strings = "200:xsCreateFile()\n"
        ugc_html = """
<h2 id="9-debug">9. Debug<a class="headerlink" href="#9-debug"></a></h2>
<h3 id="91-xschatdata">9.1. xsChatData<a class="headerlink" href="#91-xschatdata"></a></h3>
<p>Returning Type: <code class="highlight"><span class="kt">void</span></code></p>
<p>Prototype: <code class="highlight"><span class="kt">void</span> <span class="nf">xsChatData</span><span class="p">(</span><span class="kt">string</span> <span class="n">text</span><span class="p">,</span> <span class="kt">int</span> <span class="n">value</span><span class="p">)</span></code></p>
<p>Parameters:</p>
<ol><li><code>string text</code>: Label</li><li><code>int value</code>: Payload</li></ol>
<p>Sends debug chat.</p>
"""
        fe_html = """
<h1 id="XSScriptingReference-SharedFunctions">Shared Functions</h1>
<table><tr><td>xsCreateFile</td><td><p>Opens a file for writing.</p><p><code>bool xsCreateFile(bool append)</code></p></td><td><code>xsCreateFile(false);</code></td></tr></table>
"""
        functions = parse_xs_function_inventory(
            signatures_text=signatures,
            names_text=names,
            strings_text=strings,
            ugc_functions_html=ugc_html,
            fe_reference_html=fe_html,
        )
        self.assertEqual([function.name for function in functions], ["xsChatData", "xsCreateFile"])
        chat = functions[0]
        create = functions[1]
        self.assertEqual(chat.category, "Debug")
        self.assertEqual(chat.ai_context_status, "observed-working-in-ai-context")
        self.assertEqual(chat.source, "https://ugc.aoe2.rocks/general/xs/functions/functions/#91-xschatdata")
        self.assertEqual(chat.prototype, "void xsChatData ( string text , int value )")
        self.assertEqual(create.category, "file-io")
        self.assertEqual(create.ai_context_status, "context-sensitive-in-ai")
        self.assertIn("Shared Functions", create.contexts)

    def test_parse_rms_fixture_extracts_objects_sections_and_override(self) -> None:
        with WorkspaceTempDir() as tmp:
            path = tmp / "rms_test_tc_transport.rms"
            path.write_text(
                """/* rms_test_tc_transport
   Minimal fixture for villager TC garrison/ungarrison testing. */

<PLAYER_SETUP>
ai_info_map_type ARABIA 0 0 0
<OBJECTS_GENERATION>
create_object TOWN_CENTER
{
}
create_object VILLAGER
{
}
""",
                encoding="utf-8",
            )
            fixture = parse_rms_fixture(path)
        self.assertEqual(fixture.map_type, "ARABIA")
        self.assertEqual(fixture.create_objects, ["TOWN_CENTER", "VILLAGER"])
        self.assertIn("tc-transport", fixture.tags)
        self.assertEqual(fixture.recommended_probe, "ai/tc_transport_probe")

    def test_parse_ugc_xs_constants_extracts_category_value_and_description(self) -> None:
        html = """
<h2 id="11-map-types">11. Map Types<a class="headerlink" href="#11-map-types"></a></h2>
<h3 id="111-canarabia">11.1. cAnArabia<a class="headerlink" href="#111-canarabia"></a></h3>
<p>Value: <code class="highlight"><span class="kt">int</span> 9</code></p>
<p>The Arabia map type constant.</p>
<h3 id="112-cnomad">11.2. cNomad<a class="headerlink" href="#112-cnomad"></a></h3>
<p>Value: <code class="highlight"><span class="kt">int</span> 33</code></p>
<p>Nomad map type.</p>
"""
        constants = parse_ugc_xs_constants_html(html)
        self.assertEqual([item.name for item in constants], ["cAnArabia", "cNomad"])
        self.assertEqual(constants[0].category, "Map Types")
        self.assertEqual(constants[0].value_type, "int")
        self.assertEqual(constants[0].value, "9")
        self.assertEqual(constants[0].description, "The Arabia map type constant.")
        self.assertEqual(
            constants[0].source,
            "https://ugc.aoe2.rocks/general/xs/constants/constants/#111-canarabia",
        )

    def test_parse_rms_guide_topics_extracts_toc_hierarchy(self) -> None:
        text = """Age of Empires II
Definitive Random Map Scripting Guide
Table of Contents
Introduction
Syntax Overview
        Conditionals
        Math Expressions
Constant Reference
        Objects
Foreword
This guide is a comprehensive documentation of random map scripting.
Introduction
Overview text.
Syntax Overview
Each section has different commands.
Conditionals
Conditional logic description.
Math Expressions
Math section description.
Constant Reference
Reference overview.
Objects
Object constant description.
"""
        topics = parse_rms_guide_topics(text)
        self.assertEqual([topic.name for topic in topics[:5]], ["Introduction", "Syntax Overview", "Conditionals", "Math Expressions", "Constant Reference"])
        self.assertEqual(topics[2].path, ["Syntax Overview", "Conditionals"])
        self.assertEqual(topics[2].summary, "Conditional logic description.")


class AirefRegistryStructureTests(unittest.TestCase):
    def test_validated_and_project_note_layers_are_separate(self) -> None:
        registry = {
            "concepts": [],
            "articles": [],
            "validated_commands": [
                {
                    "id": "cmd-up-build-line",
                    "command_name": "up-build-line",
                    "validated_patterns": ["Observed good path."],
                    "lookup_terms": ["up-build-line"],
                    "validation_status": "observed",
                }
            ],
            "project_command_notes": [
                {
                    "id": "cmd-up-build-place-point",
                    "command_name": "up-build place-point",
                    "validated_patterns": ["Mixed behavior."],
                    "lookup_terms": ["up-build place-point"],
                    "validation_status": "mixed",
                }
            ],
            "taxonomies": {},
        }

        validated = search_registry(registry, "up-build-line", kinds={"validated-command"})
        notes = search_registry(registry, "up-build place-point", kinds={"project-command-note"})

        self.assertEqual(validated[0].name, "up-build-line")
        self.assertEqual(notes[0].name, "up-build place-point")


if __name__ == "__main__":
    unittest.main()
