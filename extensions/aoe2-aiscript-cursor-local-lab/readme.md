# AOE2 AI Parser

VS Code and Cursor support for Age of Empires II AI scripts.

## Features

- Syntax highlighting for `.per` and `.ai` files.
- Registry-backed completion, hover, and signature help for commands,
  strategic numbers, objects, techs, classes, DUC actions, operators, and other
  values.
- Semantic coloring that distinguishes actions, facts, strategic numbers,
  objects, techs, values, and local constants.
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

Contributors can set `aoe2_AiScript.labPath` to a local `aoe2-ai-lab` checkout
to test parser or reference-data changes without repackaging the extension.

## Commands

- `AoE2: Lint Current File`
- `AoE2: Lint Package`
- `AoE2: Generate Package Report`
- `AoE2: Open Latest Package Report`
- `AoE2: Open Symbol Docs Preview`
- `AoE2: Open Diagnostic Docs Preview`

## Settings

- `aoe2_AiScript.useLabLinter`: use bundled AOE2 AI Parser diagnostics.
- `aoe2_AiScript.usePackageLint`: prefer package-aware diagnostics.
- `aoe2_AiScript.labPath`: optional development checkout override.
- `aoe2_AiScript.pythonPath`: Python executable.
- `aoe2_AiScript.updateErrorsWhen`: validate on save, on change, or never.

## Attribution

This extension is based on the open source AoE2 AiScript extension by Jvinniec
and keeps the original GPL-3.0-or-later license. AOE2 AI Parser adds the local
reference registry, parser/linter integration, package validator diagnostics,
generated documentation navigation, semantic coloring, and marketplace-friendly
bundled validator runtime.
