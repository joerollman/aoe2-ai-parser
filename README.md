# AOE2 AI Parser

Parser, linter, local reference data, and VS Code/Cursor extension support for
Age of Empires II: Definitive Edition AI scripts.

The project has two main entry points:

- a Python CLI for parsing, linting, package validation, and local reference
  lookup
- a VS Code/Cursor extension that bundles the same parser and reference data for
  editor diagnostics, hover docs, autocomplete, semantic coloring, and reports

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

## Requirements

- Python 3.12+
- Node.js and npm, only needed for extension packaging and JavaScript smoke tests
- VS Code or Cursor, only needed for the editor extension

The CLI currently runs from a checkout by setting `PYTHONPATH=src`. A packaged
Python distribution can be added later.

## Quick Start

Clone the repo, then run commands from the repo root:

```powershell
git clone https://github.com/joerollman/aoe2-ai-parser.git
cd aoe2-ai-parser
$env:PYTHONPATH='src'
python -m aoe2_ai_lab --help
```

Lint one `.per` file:

```powershell
python -m aoe2_ai_lab lint path\to\your-file.per
```

Lint an AI package directory containing `.ai` roots and loaded `.per` files:

```powershell
python -m aoe2_ai_lab lint-package path\to\your-ai-package --summary
```

Generate machine-readable package output for agents or CI:

```powershell
python -m aoe2_ai_lab lint-package path\to\your-ai-package --json
```

Generate a Markdown report:

```powershell
python -m aoe2_ai_lab lint-package path\to\your-ai-package --report .tmp\lint-package\report.md
```

Use `--profile corpus` when reviewing imported/community AI packages where some
legacy-compatible patterns should be informational instead of noisy warnings:

```powershell
python -m aoe2_ai_lab lint-package path\to\community-ai --profile corpus --json
```

Look up command, strategic number, object, class, value, RMS, or XS reference
data locally:

```powershell
python -m aoe2_ai_lab resolve-reference up-target-point
python -m aoe2_ai_lab resolve-reference sn-target-point-adjustment
python -m aoe2_ai_lab resolve-reference villager-class --kind value-entry
python -m aoe2_ai_lab resolve-reference xsChatData --kind xs-function-inventory
```

Search when you do not know the exact token:

```powershell
python -m aoe2_ai_lab search-registry garrison
```

## Understanding Validator Output

`lint-package --json` is the most complete interface. Start with:

- `issue_groups`: grouped errors, warnings, and info findings with explanations
  and examples
- `roots`: each `.ai` root and the reachable `.per` files loaded by it
- `integrity`: package-level issues such as stale `.ai` roots, duplicate root
  targets, and unreachable `.per` files

Severity means:

- `error`: likely syntax, load, command-role, or command-schema failure
- `warning`: suspicious or fragile pattern that may still appear in working AIs
- `info`: package hygiene or compatibility signal

The validator is conservative. Treat warnings as review prompts unless the
category explanation or project policy says otherwise.

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

## Development Commands

Run from the repo root:

```powershell
$env:PYTHONPATH='src'
python -m pytest tests -p no:cacheprovider
node scripts\verify-cursor-extension.mjs
npm run package:editor-extension
```

The extension package build may need dependencies installed in the extension
folder first:

```powershell
cd extensions\aoe2-aiscript-cursor-local-lab
npm install
cd ..\..
npm run package:editor-extension
```

## Editor Extension

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

Useful extension commands:

- `AoE2: Lint Current File`
- `AoE2: Lint Package`
- `AoE2: Generate Package Report`
- `AoE2: Open Latest Package Report`
- `AoE2: Open Symbol Docs Preview`

## More Documentation

- [AI package validator workflow](docs/workflows/ai-package-validator.md)
- [Editor extension workflow](docs/workflows/cursor-extension.md)
- [Diagnostic code registry](docs/workflows/validator-diagnostic-codes.md)
- [Offline reference map](docs/extracted/offline-reference-map.md)
