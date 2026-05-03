# AOE2 AI Parser

VS Code and Cursor support for Age of Empires II: Definitive Edition AI
scripts. Install the extension, open a folder containing `.ai` and `.per` files,
and use the AoE2 command palette actions for linting and package reports.

## Features

- Syntax highlighting for `.per` and `.ai` files.
- Registry-backed completion, hover, and signature help for commands,
  strategic numbers, objects, techs, classes, DUC actions, operators, and other
  values.
- Semantic coloring that distinguishes actions, facts, strategic numbers,
  objects, techs, values, and local constants.
- Optional `AOE2 AI Parser Dark` and `AOE2 AI Parser Light` themes with tuned
  colors for the extension's custom semantic tokens and TextMate fallback
  scopes.
- Go to definition for local `defconst` declarations, `.ai` load targets, and
  generated local Markdown reference docs.
- Package-aware diagnostics from the bundled parser/linter.
- Command palette actions for linting the current file, linting an AI package,
  and generating package reports.
- Compact package graph output for reachable `.per` loads and `.xs` includes.
- Quick fixes and diagnostic documentation actions for common validator
  diagnostics.

## Requirements

The extension bundles the AOE2 AI Parser validator and reference data, so users do
not need to clone the tooling repository for normal editor diagnostics.

Python must be available. Configure `aoe2_AiScript.pythonPath` if `python` is
not on PATH.

Contributors can set `aoe2_AiScript.labPath` to a local AOE2 AI Parser
checkout to test parser or reference-data changes without repackaging the
extension.

## Commands

- `AoE2: Lint Current File`
- `AoE2: Lint Package`
- `AoE2: Lint Folder`
- `AoE2: Generate Package Report`
- `AoE2: Open Latest Package Report`
- `AoE2: Open Symbol Docs Preview`
- `AoE2: Open Diagnostic Docs Preview`

## Theme

For the most distinct token colors, choose `AOE2 AI Parser Dark` or
`AOE2 AI Parser Light` from `Preferences: Color Theme`. Both themes use neutral
editor surfaces, restrained contrast, and moderately saturated syntax colors so
command categories remain readable in long AI files.

## Settings

- `aoe2_AiScript.useLabLinter`: use bundled AOE2 AI Parser diagnostics.
- `aoe2_AiScript.usePackageLint`: prefer package-aware diagnostics.
- `aoe2_AiScript.packageFailLevel`: minimum package-lint severity surfaced by
  package commands and package-aware diagnostics (`error`, `warning`, or
  `info`). Default is `info`.
- `aoe2_AiScript.labPath`: optional development checkout override.
- `aoe2_AiScript.pythonPath`: Python executable.
- `aoe2_AiScript.updateErrorsWhen`: validate on save, on change, or never.

`Lint Current File` validates only the active file. `Lint Package` uses the
nearest `.ai` package root for the active file. `Lint Folder` validates the
folder containing the active file, which is useful when a mod folder is too broad
to treat as one package.
`Lint Package`, `Lint Folder`, and package-report commands write a Markdown
summary under `.tmp/lint-package/` and open it in a side Markdown Preview when
the linter finishes.

For local symbol docs, VS Code's built-in definition gesture is `Ctrl+Click`.
Cursor also supports its own side-definition gestures such as `Ctrl+Alt+Click`.
Use the hover link, right-click `AoE2: Open Symbol Docs Preview`, or the command
palette action when you want rendered Markdown Preview beside the script.

Reviewed findings can be suppressed inline with comments:

```lisp
; aoe2-ai-parser-disable-next-line repeat-chat
(chat-to-all "debug")
```

Diagnostics expose a quick fix named `Suppress <code> on this line`, which
inserts `; aoe2-ai-parser-disable-line <code>`.

You can customize parser-specific colors with standard VS Code/Cursor
`editor.semanticTokenColorCustomizations` settings. The main semantic token
names are `aoe2Action`, `aoe2Fact`, `aoe2FactAction`, `aoe2Command`,
`aoe2StrategicNumber`, `aoe2Object`, `aoe2Tech`, `aoe2Value`, and
`aoe2LocalConstant`.

The extension contributes parser-theme defaults for these keys. Theme-scoped
overrides let each individual parser color be changed without affecting other
themes:

```json
{
  "editor.semanticTokenColorCustomizations": {
    "[AOE2 AI Parser Dark]": {
      "rules": {
        "aoe2Action:aoe2aiscript": "#5DADEC",
        "aoe2StrategicNumber:aoe2aiscript": "#4CC2FF"
      }
    },
    "[AOE2 AI Parser Light]": {
      "rules": {
        "aoe2Action:aoe2aiscript": "#0550AE",
        "aoe2StrategicNumber:aoe2aiscript": "#0A7EA4"
      }
    }
  }
}
```

## Attribution

This extension is based on the open source AoE2 AiScript extension by Jvinniec:

https://github.com/Jvinniec/aoe2-aiscript

It keeps the original GPL-3.0-or-later license. AOE2 AI Parser adds the local
reference registry, parser/linter integration, package validator diagnostics,
generated documentation navigation, semantic coloring, and marketplace-friendly
bundled validator runtime.
