# AGENTS.md

Guidance for coding agents working in this public tooling repository.

## Project Scope

This repo is for AoE2 DE AI-script parsing, validation, local reference data,
and editor support. It is not an in-game AI package repo.

## Read This First

For a fresh session, start here:

1. `docs/README.md`
2. `docs/extracted/offline-reference-map.md`
3. `docs/workflows/README.md`

Then go directly to the relevant task surface:

- command semantics: `docs/reference/command-reference.md`
- package validation: `docs/workflows/ai-package-validator.md`
- editor extension: `docs/workflows/cursor-extension.md`
- offline extracted references: `docs/extracted/README.md`

## Repository Layout

- `src/aoe2_ai_lab/`: Python tooling
- `tests/`: tooling tests
- `docs/extracted/`: offline reference inventories
- `docs/reference/`: shared scripting references and generated symbol docs
- `docs/workflows/`: tooling, release, and editor workflows
- `extensions/aoe2-aiscript-cursor-local-lab/`: VS Code/Cursor extension
- `scripts/`: generation, verification, packaging, and publishing scripts

## Working Rules

- Resolve tokens locally before guessing:
  - `python -m aoe2_ai_lab resolve-reference <token>`
- Before adding a new `defconst`, check whether a built-in constant already
  exists in the local inventories. Prefer the built-in name.
- Keep personal AI packages, game logs, downloaded community corpora, and local
  probe maps out of this public repo.
- Keep task-specific rules out of this file. Put them in workflow docs.

## Verification

Use focused checks while editing, then run the full suite before release:

```powershell
$env:PYTHONPATH='src'; python -m pytest tests -p no:cacheprovider
node scripts\verify-cursor-extension.mjs
npm run package:editor-extension
```
