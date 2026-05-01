# AOE2 AI Parser

Editor diagnostics, reference lookup, autocomplete, hovers, semantic coloring,
and package reports for Age of Empires II: Definitive Edition AI scripts.

Most users should install the extension from an extension marketplace and use it
inside VS Code or Cursor. You do not need to clone this repository for normal
editor use.

## Using The Extension

After installing `AOE2 AI Parser`, open a folder that contains your `.ai` and
`.per` files.

The extension provides:

- Syntax highlighting for `.per` and `.ai` files.
- Autocomplete for commands, facts, strategic numbers, objects, techs, classes,
  DUC actions, operators, and known values.
- Hover documentation and go-to-reference for known symbols.
- Go to definition for local `defconst`s and load targets.
- Package-aware diagnostics for reachable `.per` files.
- Markdown package reports for AI package triage.
- Optional `AOE2 AI Parser Dark` color theme tuned for the extension's semantic
  token categories.

Python must be available on your PATH because the extension runs the bundled
validator with Python. If Python is installed somewhere else, set:

```json
{
  "aoe2_AiScript.pythonPath": "C:/path/to/python.exe"
}
```

Useful command palette actions:

- `AoE2: Lint Current File`
- `AoE2: Lint Package`
- `AoE2: Generate Package Report`
- `AoE2: Open Latest Package Report`
- `AoE2: Open Symbol Docs Preview`
- `AoE2: Open Diagnostic Docs Preview`

For the most distinct syntax colors, select `AOE2 AI Parser Dark` with
`Preferences: Color Theme`.

Diagnostics run on save by default. To include info-level package findings in
package commands and package-aware diagnostics, add this to workspace settings:

```json
{
  "aoe2_AiScript.packageFailLevel": "info"
}
```

The marketplace extension identity is:

```text
aoe2-ai-scripters.aoe2-ai-parser
```

## Reading Diagnostics

The validator uses three severities:

- `error`: likely syntax, load, command-role, or command-schema failure.
- `warning`: suspicious or fragile pattern that may still appear in working AIs.
- `info`: package hygiene or compatibility signal.

The validator is intentionally conservative. Treat warnings as review prompts
unless the diagnostic explanation says the pattern is known-bad.

For imported or older community AIs, some compatibility patterns are expected.
The extension and CLI support a `corpus` profile for that kind of review.

## CLI And Repository Use

Clone this repo only if you want to run the parser CLI directly, develop the
extension, update reference data, or contribute validator changes.

```powershell
git clone https://github.com/joerollman/aoe2-ai-parser.git
cd aoe2-ai-parser
$env:PYTHONPATH='src'
python -m aoe2_ai_lab --help
```

Lint one `.per` file:

```powershell
python -m aoe2_ai_lab lint path\to\your-file.per --profile default
```

Single-file lint prints every finding it detects, including `info` findings,
and exits non-zero if any finding is present.

Lint an AI package directory containing `.ai` roots and loaded `.per` files:

```powershell
python -m aoe2_ai_lab lint-package path\to\your-ai-package --summary
```

Package lint defaults to failing on `error`. To include `info` findings in
summary output and the exit threshold:

```powershell
python -m aoe2_ai_lab lint-package path\to\your-ai-package --summary --profile default --fail-level info
```

Generate machine-readable package output for agents or CI:

```powershell
python -m aoe2_ai_lab lint-package path\to\your-ai-package --json
```

Generate a Markdown report:

```powershell
python -m aoe2_ai_lab lint-package path\to\your-ai-package --report .tmp\lint-package\report.md
```

Use `--profile corpus` when reviewing imported/community AI packages where
legacy-compatible patterns should be suppressed:

```powershell
python -m aoe2_ai_lab lint-package path\to\community-ai --profile corpus --json
```

Look up local reference data:

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

## Development

Repository layout:

- `src/aoe2_ai_lab/`: Python parser, linter, package validator, and reference
  tooling.
- `tests/`: automated tests.
- `docs/extracted/inventories/`: local JSON reference inventories.
- `docs/reference/`: shared scripting references and generated symbol docs.
- `docs/workflows/`: validator, extension, release, and generation workflows.
- `extensions/aoe2-aiscript-cursor-local-lab/`: publishable VS Code/Cursor
  extension package.
- `scripts/`: generation, verification, packaging, and publishing scripts.

Run focused checks while editing and the full suite before release:

```powershell
$env:PYTHONPATH='src'
python -m pytest tests -p no:cacheprovider
node scripts\verify-cursor-extension.mjs
npm run package:editor-extension
```

Packaging creates a VSIX under:

```text
extensions/aoe2-aiscript-cursor-local-lab/aoe2-ai-parser-<version>.vsix
```

The VSIX bundles the parser runtime and local reference data. Users need Python
available, but they do not need this checkout for normal diagnostics.

## Attribution

This extension is based on the open source AoE2 AiScript extension by Jvinniec:

```text
https://github.com/Jvinniec/aoe2-aiscript
```

AOE2 AI Parser keeps the original GPL-3.0-or-later license and adds the local
reference registry, parser/linter integration, package validator diagnostics,
generated documentation navigation, semantic coloring, and bundled validator
runtime.

## License

AOE2 AI Parser is distributed under GPL-3.0-or-later. See [LICENSE](LICENSE).

## More Documentation

- [AI package validator workflow](docs/workflows/ai-package-validator.md)
- [Editor extension workflow](docs/workflows/cursor-extension.md)
- [Diagnostic code registry](docs/workflows/validator-diagnostic-codes.md)
- [Offline reference map](docs/extracted/offline-reference-map.md)
