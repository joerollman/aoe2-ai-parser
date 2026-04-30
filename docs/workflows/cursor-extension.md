# Editor Extension Workflow

The patched local VS Code/Cursor extension lives at
`extensions/aoe2-aiscript-cursor-local-lab`.

It is a local fork of the AoE2 AiScript extension with aoe2-ai-lab integration.
The folder name is historical; the packaged extension is editor-neutral and can
be installed in VS Code or Cursor.
Patch the compiled JavaScript files directly unless the TypeScript source is
also updated and rebuilt.

## Installed Extension

Preferred Cursor install path:

```powershell
npm run install:cursor-extension
```

This removes stale local VSIX artifacts, packages the current local extension,
installs it into Cursor, and verifies the installed `extension.js` contains the
expected `lint-package --json` and `issue_groups` formatter hooks.
Before packaging, it also runs the diagnostic-registry sync check and the Cursor
extension verifier, then syncs a bundled copy of the Python validator and local
reference data. That bundled runtime lets marketplace users run diagnostics
without cloning this repo.

Preferred VS Code install path:

```powershell
npm run install:vscode-extension
```

Package without installing:

```powershell
npm run package:editor-extension
```

When installing after extension code changes, prefer the patch-bump install:

```powershell
npm run install:cursor-extension:bump
```

This increments
`extensions/aoe2-aiscript-cursor-local-lab/package.json`, packages the new
version, installs it in Cursor, and verifies the installed source. Commit the
version bump with the extension change. For VS Code, use:

```powershell
npm run install:vscode-extension:bump
```

If Cursor or VS Code has the previous same-version extension folder locked, use
the relevant bump install or close the editor and retry the normal install.

Manual fallback:

```powershell
Push-Location extensions\aoe2-aiscript-cursor-local-lab
npx @vscode/vsce package
Pop-Location
cursor --install-extension extensions\aoe2-aiscript-cursor-local-lab\aoe2-ai-parser-<version>.vsix --force
# or
code --install-extension extensions\aoe2-aiscript-cursor-local-lab\aoe2-ai-parser-<version>.vsix --force
```

Verify the active extension:

```powershell
cursor --list-extensions --show-versions | Select-String -Pattern 'aoe2|aiscript'
code --list-extensions --show-versions | Select-String -Pattern 'aoe2|aiscript'
```

Expected active extension, with the current local version:

```text
aoe2-ai-scripters.aoe2-ai-parser@<version>
```

Reload Cursor or VS Code after installing a new VSIX.

## Settings

Important settings:

- `aoe2_AiScript.useLabLinter`: default `true`.
- `aoe2_AiScript.usePackageLint`: default `true`.
- `aoe2_AiScript.labPath`: optional path to a development checkout of this
  repo. Empty means use the validator/reference runtime bundled with the
  extension.
- `aoe2_AiScript.pythonPath`: Python executable, default `python`.

If Python, the bundled runtime, `labPath`, or import setup fails, the extension reports an
`aoe2-ai-lab-setup` diagnostic with the exact command, `pythonPath`, and
`labPath`.

## Sharing

For a small community release, publish the generated VSIX and installation
instructions first. Marketplace publishing uses the same VSIX after publisher
tokens are configured.

Recommended pre-release checklist:

```powershell
npm run package:editor-extension
$env:PYTHONPATH='src'; python -m pytest tests -p no:cacheprovider
```

The package command writes:

```text
extensions/aoe2-aiscript-cursor-local-lab/aoe2-ai-parser-<version>.vsix
```

Users can install the same VSIX in either editor:

```powershell
code --install-extension aoe2-ai-parser-<version>.vsix --force
cursor --install-extension aoe2-ai-parser-<version>.vsix --force
```

Diagnostics use the validator bundled in the extension when `labPath` is empty.
Users only need to set `labPath` when they are developing against a local
checkout of this repo:

```json
"aoe2_AiScript.labPath": "C:/path/to/aoe2-ai-lab",
"aoe2_AiScript.pythonPath": "python"
```

Distribution options:

- GitHub Release: attach the VSIX and link to this workflow. This is the
  lowest-friction first release path.
- Open VSX Registry: useful for editor ecosystems that read Open VSX directly.
- Visual Studio Marketplace: best for broad VS Code distribution, but requires
  a publisher account/token and stable extension branding.

Before Marketplace/Open VSX publishing, verify the `publisher`, `name`,
`displayName`, `license`, `repository`, and `author` fields in
`extensions/aoe2-aiscript-cursor-local-lab/package.json`.

Marketplace publish commands:

```powershell
npm run publish:vscode-extension
npm run publish:openvsx-extension
```

`publish:vscode-extension` requires Visual Studio Marketplace publisher setup
and a `vsce` token. `publish:openvsx-extension` requires an Open VSX namespace
and token for `ovsx`.

See [release-and-repo-split.md](./release-and-repo-split.md) before publishing
or moving `extensions\aoe2-aiscript-cursor-local-lab\samples` into a separate AI package repo.

## Diagnostics

The extension supports `.per` and `.ai` files.

For `.per` files:

- Prefer package-aware diagnostics by running `lint-package --json` against the
  nearest folder containing an `.ai` root.
- Fall back to `lint <file>` when the current file is not reachable from that
  package.
- Show visible severity in messages, for example
  `[warning] repeat-chat: ...`.
- Prefer structured `span` data from `lint --json` and `lint-package --json`
  for token-level squiggles. Parser-backed command diagnostics now provide
  exact command-head or argument spans when the linter can identify the bad
  token.
- Fall back to local range heuristics when a finding has no structured span:
  quoted identifiers, chat commands, or the command token.

For `.ai` files:

- Use package manifest data from `lint-package --json`.
- Report unresolved load roots as `missing-load-target`.
- Report stale roots as `stale-ai-root`.
- Report zero/negative-weight `load-random` manifest entries as
  `skipped-load-random` info diagnostics.
- Report root `.per` files loaded by multiple `.ai` files as
  `duplicate-root-target` warning diagnostics.
- Report `.ai` files with the same case-insensitive display name as
  `duplicate-ai-name` warning diagnostics.

## Commands

Command palette entries:

- `AoE2: Lint Current File`
- `AoE2: Lint Package`
- `AoE2: Generate Package Report`
- `AoE2: Open Latest Package Report`
- `AoE2: Open Symbol Docs Preview`

Command output goes to the `AOE2 AI Parser` output panel.

`AoE2: Lint Package` runs `lint-package --json` and formats top-level
`issue_groups` for the output panel. This keeps the command palette view aligned
with the Markdown report: issue categories include both lint findings and
package-integrity issues, while live diagnostics still use the detailed per-file
findings and integrity manifest from the same JSON payload.

Package reports are written to:

```text
.tmp/lint-package
```

`lint-package` exits non-zero when findings meet the fail threshold. The
extension treats stdout/report output as useful output, not as a hard command
failure. A generated report with findings should show a warning notification,
not a generic `Command failed` message.

## Registry Completions

The extension keeps the original completion list and appends local registry
completions from:

```text
extensions/aoe2-aiscript-cursor-local-lab/data/completions.json
```

The source generator is:

```powershell
node extensions\aoe2-aiscript-cursor\scripts\build-completions.mjs
Copy-Item extensions\aoe2-aiscript-cursor\data\completions.json extensions\aoe2-aiscript-cursor-local-lab\data\completions.json -Force
```

The generated completion data is built from local inventories under
`docs/extracted/inventories` and includes commands, strategic numbers, objects,
techs, classes/value families, and other enumerated values.

## Context-Aware Completions

The language server ranks completion results by cursor context:

- Command positions such as `(` prioritize AI script commands and control forms.
- Strategic-number positions such as `(set-strategic-number `,
  `(up-modify-sn `, and `(up-compare-sn ` prioritize strategic numbers.
- Known command parameters are ranked by argument position from registry syntax.
  For example, `(up-find-local c: ` prioritizes object/class constants,
  `(up-target-objects 0 ` prioritizes DUC actions, and
  `(up-modify-sn sn-maximum-town-size ` prioritizes math operators.
- `(map-type ` prioritizes documented MapType values.
- `c:` value positions prioritize objects, values, techs, strategic numbers,
  and local constants.
- Local `(defconst ...)` names in the current document are offered as
  completions.
- `.ai` load statements such as `(load "` and `(load-random ... "` suggest
  nearby `.per` load targets from the current AI package.

Cursor still applies its own fuzzy ranking and AI suggestions on top of the
language-server list. The extension improves the structured candidate set that
Cursor sees.

## Registry Hovers

The extension also uses `data/completions.json` as a compact hover registry.
Hover lookup checks the local registry first, then falls back to the original
extension hover data. This keeps hover docs aligned with the completion and
validator inventories without introducing another generated file. The client
extension also adds a trusted hover action, `Open in Markdown Preview`, which
opens the local symbol reference in a side Markdown Preview pane. The trusted
client-side provider is used because Cursor may render language-server hover
markdown without enabling `command:` links.

## Semantic Coloring

The extension registers semantic tokens backed by `data/completions.json`.
Cursor can color known symbols by registry role:

- `aoe2Action`: action commands.
- `aoe2Fact`: fact commands.
- `aoe2FactAction`: commands documented for both fact and action positions.
- `aoe2Command`: control or other commands.
- `aoe2StrategicNumber`: strategic numbers.
- `aoe2Object`: object, unit, building, or class tokens.
- `aoe2Tech`: technology tokens.
- `aoe2Value`: DUC actions, operators, resources, and other enumerated values.
- `aoe2LocalConstant`: local `defconst` declarations.

The workspace `.vscode/settings.json` enables semantic highlighting and assigns
default colors for these token types. Users can override them with
`editor.semanticTokenColorCustomizations`. The workspace also includes
TextMate fallback color rules for the grammar scopes used by commands, facts,
strategic numbers, object-ish tokens, value tokens, resources, and local
constants. These fallback rules help Cursor themes that do not visibly apply
custom semantic token types.

Use `samples/semantic_coloring_sample.per` as the visual check file after
changing grammar scopes or color settings. It is intentionally lint-clean while
covering representative token categories.

## Definition Navigation

The language server supports definition/declaration navigation for common AI
script symbols:

- Local or package-reachable `defconst` references jump to the matching
  `(defconst ...)` declaration. The current buffer is checked first, then nearby
  package `.per` files are scanned from the package root.
- `.ai` and `.per` `(load "...")` / `(load-random ... "...")` string targets
  jump to the resolved `.per` file when it exists.
- Built-in registry symbols such as commands, strategic numbers, objects, techs,
  classes, DUC actions, and value constants jump to the matching anchor in the
  combined local reference at `docs/reference/generated/ai-symbol-reference.md`.
  Per-symbol generated Markdown pages under `docs/reference/generated/symbols/`
  remain a compatibility fallback when the aggregate reference is unavailable.

Regenerate symbol docs after completion-registry changes:

```powershell
npm run generate:symbol-docs
```

The generated table of contents is intentionally section-level only. Per-symbol
anchors remain in the body for definition navigation and hover-preview links,
but the visible TOC should link to broad groups such as commands, strategic
numbers, objects, techs, and values.

Use `AoE2: Open Symbol Docs Preview` on a symbol to open the same local symbol
entry in Markdown Preview to the side. This is implemented as a client command
because editor definition navigation itself opens source locations, not rendered
Markdown previews. The command asks Cursor to open
`vscode.markdown.preview.editor` in `ViewColumn.Beside`, with the built-in
`markdown.showPreviewToSide` command as a fallback. It opens the combined local
reference with the symbol anchor fragment when present and falls back to a
per-symbol Markdown page when necessary. There is no default keyboard shortcut;
use Cursor's built-in `Ctrl+Alt+Click` side-definition gesture when that is
sufficient, or the hover link/context menu command when rendered Markdown
Preview is preferred.

This workspace also sets Markdown files to open through Cursor/VS Code's
Markdown Preview editor by default:

```json
"workbench.editorAssociations": {
  "*.md": "vscode.markdown.preview.editor"
}
```

That makes Ctrl-click definition targets into generated local docs prefer the
rendered Markdown view when the editor honors default associations. If Cursor
opens raw Markdown for a remembered file, use `View: Reopen Editor With...` and
select Markdown Preview, or use `AoE2: Open Symbol Docs Preview`.

## Registry Signatures

Signature help also prefers `data/completions.json` for command syntax and
active parameter detection. This keeps parameter popups aligned with the same
local command docs used by completions, hovers, and validator rules. If the
registry has no matching command syntax, the extension falls back to the
original signature-help data.

## Code Actions

The language server offers quick fixes for selected aoe2-ai-lab diagnostics:

- `missing-load-target`: replace the unresolved `.ai` load target with a nearby
  reachable `.per` load target.
- `undefined-strategic-number`, `undefined-constant`,
  `undefined-identifier`, and `undefined-position-constant`: replace the token
  with closest local registry matches. Replacement candidates are narrowed by
  command argument context when possible, using the same parameter-family logic
  as completions and signature help.
- `command-typed-prefix-mismatch`: replace operator-style tokens such as `g:=`
  with plain type prefixes such as `g:`, `c:`, or `s:`.
- `command-typed-operand-mismatch`: show a review action when a valid prefix is
  followed by an operand that looks like a different type, such as `g:` or
  `g:=` before an `sn-*` strategic number.
- `redundant-built-in-defconst`: remove the redundant defconst line.
- `command-role-mismatch`: show a review action that keeps the diagnostic
  visible in Cursor's quick-fix UI.

Explanation actions are also available for common review-oriented diagnostics
such as `unsafe-set-target-object`, `unscoped-duc-target`,
`command-typed-prefix-mismatch`, `up-can-build-zero-escrow`,
`up-build-place-point-coordinate-as-escrow`, `repeat-chat`,
`command-typed-operand-mismatch`, `command-argument-mismatch`, and
`redundant-built-in-defconst`. These actions do not edit files; they surface
the practical meaning of the warning in Cursor's quick-fix UI and open
`docs/workflows/validator-diagnostic-codes.md` in Markdown Preview to the
matching diagnostic-code anchor when the local docs are bundled or configured.

## Samples

Diagnostic samples live under:

```text
extensions/aoe2-aiscript-cursor-local-lab/samples
```

Useful samples:

- `lab_diagnostics_sample.per`: intentionally invalid `.per` file with many
  token-level diagnostics.
- `lab_diagnostics_sample.ai`: loads the diagnostic `.per` sample so package
  lint can see it.
- `lab_bad_load_sample.ai`: intentionally missing load target for `.ai`
  missing-load diagnostics.
- `lab_load_random_sample.ai`: intentionally has a skipped zero-weight
  `load-random` entry.
- `lab_duplicate_one.ai` and `lab_duplicate_two.ai`: intentionally load the
  same root `.per` file to exercise duplicate-root diagnostics.
- `semantic_coloring_sample.per`: representative commands, facts, actions,
  strategic numbers, object tokens, techs, DUC values, resources, local
  constants, strings, comments, and numbers for visually checking semantic and
  TextMate coloring.

## Verification

Run these before handoff:

```powershell
node scripts\verify-cursor-extension.mjs
node scripts\smoke-cursor-package-output.mjs
node scripts\smoke-cursor-completions.mjs
node --check extensions\aoe2-aiscript-cursor-local-lab\languageExtension\out\extension.js
node --check extensions\aoe2-aiscript-cursor-local-lab\languageExtension\out\server.js
$env:PYTHONPATH='src'; python -m pytest tests -p no:cacheprovider
```

Focused extension tests:

```powershell
$env:PYTHONPATH='src'; python -m pytest tests\test_cursor_extension.py -p no:cacheprovider
```

The Node verifier checks for required compiled-JS hooks, command palette
contributions, `.per`/`.ai` language registration, registry completion data,
registry hover hooks, diagnostics hooks, package-output smoke hooks, and
required sample files.

The package-output smoke test runs `lint-package --json` on the extension
sample package, formats it through the extension's `issue_groups` formatter,
and asserts that the output panel shape starts with `Package summary:` and
`Issue categories:` instead of the old `--summary` output.

The completion smoke test forks the language server over LSP IPC, opens small
temporary `.per` and `.ai` documents, and checks that context-ranked completions
surface expected candidates near the top for DUC search arguments, DUC actions,
SN math operators, local `defconst` names, and `.ai` load targets. It also
checks registry-backed signature help for active DUC/SN parameters and quick
fixes for representative diagnostics.
