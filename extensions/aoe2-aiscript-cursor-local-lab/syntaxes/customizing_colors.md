# Defining Custom Colors - Tutorial

This is a very short description of how to define your own custom colors for AI scripting.


## How the groups are defined:

The individual components are defined using a set of regular expressions that capture some text. This text is then associated with a very specific "scope". Below is a table that identifies the defined scopes that are currently defined. Most of these will be compatible with most color themes.

| scope name                                     | Description 
|------------------------------------------------|-------------
| comment.line.semicolon                         | comments
| string.quoted.double.aoe2aiscript              | strings (outside of comments)
| entity.name.function.aoe2aiscript.fact         | commands in the facts section (before `=>`)
| entity.name.function.aoe2aiscript.action       | commands in the actions section (after `=>`)
| support.type.aoe2aiscript.yields               | `=>`
| storage.type.aoe2aiscript.def                  | `defrule`, `defconst` (for more control see below)
| keyword.control.aoe2aiscript.defact            | `disable-self`, `do-nothing` (for more control see below)
| variable.other.aoe2aiscript.resource           | `food`, `wood`, `stone`, `gold`
| constant.numeric.aoe2aiscript                  | Numbers (0, 1, 2, etc...)
| keyword.control.aoe2aiscript.load              | `#load-if-defined`, `#load-if-not-defined`, `#else`, `#end-if`, `load`, `load-random` (for more control see below)
| keyword.control.aoe2aiscript.control           | `and`, `nand`, `nor`, `not`, `or`
| constant.language.aoe2aiscript.truefalse       | `true`, `false`


## Finer grained control
The following are not specially colored by default, but have been made available. This allows either highlighting something that wouldn't otherwise be highlighted, or applying a special color to a command subset.

| scope                                           | Description 
|-------------------------------------------------|-------------
| aoe2aiscript.age                                | `dark-age`, `feudal-age`, `castle-age`, `imperial-age`
| aoe2aiscript.tech                               | `ri-X` tags
| storage.type.aoe2aiscript.def.rule              | `defrule`
| storage.type.aoe2aiscript.def.const             | `defconst`
| entity.name.function.aoe2aiscript.action.jump   | `up-jump-X` tags
| keyword.control.aoe2aiscript.defact.disableself | `disable-self`
| keyword.control.aoe2aiscript.defact.donothing   | `do-nothing`
| keyword.control.aoe2aiscript.load.if            | `#load-if-defined`, `#load-if-not-defined`
| keyword.control.aoe2aiscript.load.elseend       | `#else`, `#end-if`
| keyword.control.aoe2aiscript.load.file          | `load`, `load-random`


## How to customize parser colors

Parser semantic colors are configured through extension-owned settings. Run
`AoE2: Write Semantic Color Settings` from the command palette to write the
editable `Dark`, `Light`, and `Custom` presets into your settings file.

The generated settings use this shape:

```json
{
  "aoe2_AiScript.enableSemanticColors": true,
  "aoe2_AiScript.semanticColors.theme": "auto",
  "aoe2_AiScript.semanticColors.byTheme": {
    "Dark": {
      "action": "#5DADEC",
      "fact": "#C69CFF",
      "strategicNumber": "#4CC2FF"
    },
    "Light": {
      "action": "#0550AE",
      "fact": "#6F42C1",
      "strategicNumber": "#0A7EA4"
    },
    "Custom": {
      "action": "#569CD6",
      "fact": "#C586C0",
      "strategicNumber": "#4BA3FF"
    }
  }
}
```

`auto` selects `Light` for light-named editor themes and `Dark` otherwise.
Set `aoe2_AiScript.semanticColors.theme` to `custom` to force the `Custom`
preset.
