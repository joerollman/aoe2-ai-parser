# AOE2 AI Parser

Parser, linter, local reference data, and VS Code/Cursor extension support for
Age of Empires II: Definitive Edition AI scripts.

## What Is Included

- Python parser/linter for `.per`, `.ai`, and AI package validation.
- Offline command, object, tech, strategic-number, value, RMS, and XS reference
  inventories.
- Generated Markdown symbol reference for editor navigation.
- VS Code/Cursor extension with syntax highlighting, autocomplete, hover docs,
  semantic coloring, diagnostics, quick fixes, and package reports.
- Tests for parser, linter, package validation, reference generation, and
  extension integration.

This public repo intentionally excludes personal AI packages, downloaded
community AI corpora, local RMS probes, logs, generated VSIX artifacts, and
machine-specific game paths.

## Layout

- `src/aoe2_ai_lab/`: Python parser, linter, package validator, and reference
  tooling.
- `tests/`: automated tests.
- `docs/extracted/inventories/`: local JSON reference inventories.
- `docs/reference/`: shared scripting references and generated symbol docs.
- `docs/workflows/`: validator, extension, release, and generation workflows.
- `extensions/aoe2-aiscript-cursor-local-lab/`: publishable VS Code/Cursor
  extension package.
- `scripts/`: generation, verification, packaging, and publishing scripts.

## Common Commands

Run from the repo root:

```powershell
$env:PYTHONPATH='src'
python -m aoe2_ai_lab resolve-reference up-target-point
python -m aoe2_ai_lab lint extensions\aoe2-aiscript-cursor-local-lab\samples\lab_diagnostics_sample.per
python -m pytest tests -p no:cacheprovider
npm run package:editor-extension
```

## Extension

The extension package identity is:

```text
aoe2-ai-scripters.aoe2-ai-parser
```

Packaging creates a VSIX under:

```text
extensions/aoe2-aiscript-cursor-local-lab/aoe2-ai-parser-<version>.vsix
```

The VSIX bundles the parser runtime and local reference data. Users need Python
available, but they do not need to clone this repo for normal editor
diagnostics.
