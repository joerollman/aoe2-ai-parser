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
- Optional `AOE2 AI Parser Dark`, `AOE2 AI Parser Light`, and
  `AOE2 AiScript Classic` color themes. The classic theme follows the original
  extension's TextMate scope model.

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
- `AoE2: Lint Current AI`
- `AoE2: Lint Current Folder`
- `AoE2: Lint Recursive Folder`
- `AoE2: Generate Package Report`
- `AoE2: Open Latest Package Report`
- `AoE2: AutoFormat Current File`
- `AoE2: AutoFormat Current AI`
- `AoE2: AutoFormat Current Folder`
- `AoE2: AutoFormat Recursive Folder`
- `AoE2: Format Then Lint Current File`
- `AoE2: Format Then Lint Current AI`
- `AoE2: Format Then Lint Current Folder`
- `AoE2: Format Then Lint Recursive Folder`
- `AoE2: Open Symbol Docs Preview`
- `AoE2: Open Diagnostic Docs Preview`

For the most distinct parser syntax colors, select `AOE2 AI Parser Dark` or
`AOE2 AI Parser Light` with `Preferences: Color Theme`. For coloring closer to
the original AoE2 AiScript extension, select `AOE2 AiScript Classic`.

The extension does not switch your editor theme. Parser-specific semantic
colors are opt-in so users keep their existing color scheme by default:

```json
{
  "aoe2_AiScript.enableSemanticColors": true
}
```

`Lint Current File` validates only the active file. `Lint Current AI` validates
the selected `.ai` root beside the active file plus its reachable `.per` loads.
`Lint Package` starts from the nearest `.ai` package root for the active file.
`Lint Current Folder` validates `.ai` roots directly inside the active file's
folder only. `Lint Recursive Folder` validates every `.ai` root below that
folder, which is useful when the selected folder is a whole AI package or mod
tree.
Package-report commands open the generated Markdown report in a side preview
after the linter finishes.
The output panel starts with a `Lint trace` tree for package/folder linting so
users can see the input path, resolved `.ai` roots, root `.per` files, every
reachable `.per`, included `.xs` files, and load/include edges that were
validated. Package and folder lint commands also stream a simpler live trace
while linting is still running.

`AoE2: AutoFormat Current File` formats only the active `.per` or `.ai` file.
Formatting is manual by default; enable opt-in save-time formatting with:

```json
{
  "aoe2_AiScript.formatOnSave": true
}
```

The formatter enforces final newlines for `.per` files, empty `.ai` entry
files, comment wrapping up to `aoe2_AiScript.formatMaxLineLength` (maximum
255), load path separator normalization, and conservative one-expression-per-
line splitting for facts/actions. Chat lines are skipped by default; set
`aoe2_AiScript.formatChat` only when you explicitly want chat lines formatted.
`AoE2: AutoFormat Current AI` formats the selected `.ai` root beside the active
file plus reachable `.per` loads. `AutoFormat Current Folder` formats direct
`.ai`/`.per` children only. `AutoFormat Recursive Folder` formats every
`.ai`/`.per` below the active file's folder. The `Format Then Lint` commands
run the corresponding formatter first and then lint the same scope when
formatting succeeds.

For local symbol docs, VS Code's built-in definition gesture is `Ctrl+Click`.
Cursor also supports its own side-definition gestures such as `Ctrl+Alt+Click`.
Use the hover link, right-click `AoE2: Open Symbol Docs Preview`, or the command
palette action when you want the rendered Markdown Preview beside the script.

Diagnostics run on save by default. Live diagnostics validate the active file
by default; package-aware live diagnostics are opt-in because large AI packages
can make open/save validation CPU-heavy. Use `AoE2: Lint Package` when you want
explicit package validation, or enable package-aware live diagnostics with:

```json
{
  "aoe2_AiScript.usePackageLint": true
}
```

Package commands surface info-level findings by default. To make package lint
less strict, change the fail level in workspace settings:

```json
{
  "aoe2_AiScript.packageFailLevel": "warning"
}
```

Syntax colors can be customized with normal VS Code/Cursor settings. The
extension contributes semantic token names such as `aoe2Action`,
`aoe2Fact`, `aoe2StrategicNumber`, `aoe2Object`, and `aoe2LocalConstant`;
override them through `editor.semanticTokenColorCustomizations`.

You can override individual parser colors globally or only for one contributed
theme. The extension also contributes these parser-theme defaults so the keys
are discoverable from settings JSON and can be edited directly:

```json
{
  "editor.semanticTokenColorCustomizations": {
    "[AOE2 AI Parser Dark]": {
      "enabled": true,
      "rules": {
        "aoe2Action:aoe2aiscript": "#5DADEC",
        "aoe2StrategicNumber:aoe2aiscript": "#4CC2FF",
        "aoe2LocalConstant:aoe2aiscript": "#57D68D"
      }
    },
    "[AOE2 AI Parser Light]": {
      "enabled": true,
      "rules": {
        "aoe2Action:aoe2aiscript": "#0550AE",
        "aoe2StrategicNumber:aoe2aiscript": "#0A7EA4",
        "aoe2LocalConstant:aoe2aiscript": "#116329"
      }
    }
  }
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
You can suppress a reviewed finding inline:

```lisp
(defconst villager-class 904) ; aoe2-ai-parser-disable-line redundant-built-in-defconst
; aoe2-ai-parser-disable-next-line repeat-chat
(chat-to-all "debug")
```

Editor diagnostics include a quick fix to insert the line suppression. The CLI
can also insert it:

```powershell
python -m aoe2_ai_lab suppress-finding path\to\your-file.per 42 repeat-chat
```

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

Package lint defaults to failing on `error` in the CLI. To include `info`
findings in summary output and the exit threshold:

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

Format one file, a current folder, or a recursive folder of `.ai`/`.per` files:

```powershell
python -m aoe2_ai_lab format path\to\your-ai-package --check
python -m aoe2_ai_lab format path\to\your-ai-package --write --max-line-length 220
python -m aoe2_ai_lab format path\to\your-ai-folder --write --no-recursive
```

The CLI formatter leaves `chat-to-all` and `chat-to-player` lines alone unless
you pass `--format-chat`. Use `--include-loads` when the path is a `.ai` or
`.per` root and you want the formatter to include reachable loaded `.per` files.

Use `--profile corpus` when reviewing imported/community AI packages where
legacy-compatible patterns should be suppressed:

```powershell
python -m aoe2_ai_lab lint-package path\to\community-ai --profile corpus --json
```

Suppress a known noisy code for one run:

```powershell
python -m aoe2_ai_lab lint-package path\to\community-ai --suppress-code repeat-chat
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
