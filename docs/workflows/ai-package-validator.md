# AI Package Validator

Use the package validator when checking an AI package, imported community AI
pack, or extension sample package.

## Commands

Single-file lint:

```powershell
$env:PYTHONPATH='src'
python -m aoe2_ai_lab lint extensions\aoe2-aiscript-cursor-local-lab\samples\lab_diagnostics_sample.per
```

Package lint:

```powershell
$env:PYTHONPATH='src'
python -m aoe2_ai_lab lint-package extensions\aoe2-aiscript-cursor-local-lab\samples --profile default
```

You can pass a specific `.ai` file to validate just one root from a larger pack:

```powershell
$env:PYTHONPATH='src'
python -m aoe2_ai_lab lint-package "path\\to\\Some AI.ai" --profile corpus --summary
```

You can also pass a specific `.per` file to validate that script plus its
reachable `load`, `#load`, and `load-random` graph without needing a wrapper
`.ai` file:

```powershell
$env:PYTHONPATH='src'
python -m aoe2_ai_lab lint-package "path\\to\\main.per" --profile corpus --summary
```

Community/corpus package lint:

```powershell
$env:PYTHONPATH='src'
python -m aoe2_ai_lab lint-package "path\\to\\ai-package" --profile corpus --json
```

Use `--summary` only when you need a compact console view. It includes severity
counts, confidence counts, top finding codes, and top files, but it does not
expose the full `issue_groups`, examples, spans, or root manifest.

Machine-readable output:

```powershell
$env:PYTHONPATH='src'
python -m aoe2_ai_lab lint-package extensions\aoe2-aiscript-cursor-local-lab\samples --profile default --json
```

Write machine-readable output to a file:

```powershell
python -m aoe2_ai_lab lint-package extensions\aoe2-aiscript-cursor-local-lab\samples --profile default --output .tmp\lint-package\p.json
```

Write a verbose Markdown report:

```powershell
python -m aoe2_ai_lab lint-package extensions\aoe2-aiscript-cursor-local-lab\samples --profile default --report .tmp\lint-package\p.md
```

The Markdown report is intended for humans and agent handoff notes. It includes
a summary, root manifest, category explanations, and file/line occurrences for
each warning or error category.

## Profiles

- `default`: strict normal project lint profile.
- `corpus`: suppresses compatibility noise that appears in working community
  AIs, such as redundant built-in class aliases.

Use `default` for `extensions\aoe2-aiscript-cursor-local-lab\samples`. Use `corpus` when evaluating imported AIs unless the
task is explicitly to enforce project style.

## Severity

Findings have one of three severities:

- `error`: likely syntax, load, command-role, or command-schema failure.
- `warning`: suspicious or fragile pattern that can appear in working AIs.
- `info`: compatibility or package hygiene signal.

Do not treat severity as certainty. Use `confidence`, `source`, and the
category explanation in `issue_groups` to decide whether the issue is a hard
failure, a heuristic review prompt, or package hygiene.

## Issue Groups

`issue_groups` is the preferred first read for agents and the Cursor command
palette. It groups package output by issue code and includes both lint findings
and integrity issues.

Each group has:

- `source`: `lint` or `integrity`.
- `code`: the finding or integrity issue code.
- `count`: total occurrences in the package.
- `severity_counts` and `confidence_counts`.
- `explanation`: practical reason the validator reports that category.
- representative `examples` with paths, lines where applicable, and messages.

Use `issue_groups` to decide what to inspect next. Use per-root `findings` for
exact spans and line-level diagnostics. Use `integrity.root_manifest` when the
issue is package structure, missing loads, stale roots, duplicate roots, skipped
`load-random` entries, or unreachable files.

Resolve diagnostic-code meanings from the same registry used by reports and
Cursor:

```powershell
python -m aoe2_ai_lab diagnostics command-role-mismatch
python -m aoe2_ai_lab diagnostics command-role-mismatch --json
```

## Editor Extension

The active local VS Code/Cursor extension workflow is documented in
[`cursor-extension.md`](./cursor-extension.md).

The installed local extension is `extensions/aoe2-aiscript-cursor-local-lab`.
It integrates this validator into VS Code/Cursor diagnostics and command palette
commands, while preserving the original extension's syntax highlighting and
extending completion, hover, signature-help, and quick-fix behavior with local
registry data.

The `AoE2: Lint Package` command runs `lint-package --json` and formats
top-level `issue_groups` in the `AOE2 AI Parser` output panel. Live squiggle
diagnostics still use the detailed per-file `findings` and `integrity`
manifest from that same JSON payload.

Examples:

- `missing-load-target`: error.
- `duplicate-preprocessor-else`: error.
- `preprocessor-nesting-depth-exceeded`: error.
- `malformed-defconst`: error.
- `defconst-value-out-of-range`: error.
- `malformed-load-directive`: error.
- `malformed-include-directive`: error.
- `include-missing-xs-extension`: error.
- `malformed-load-random-directive`: error.
- `load-random-plus-weight-de-behavior`: warning in `default`; suppressed in
  `corpus`.
- `load-cycle`: error.
- `load-depth-exceeded`: error.
- `command-typed-prefix-mismatch`: error.
- `source-line-too-long`: error.
- `command-typed-operand-mismatch`: warning.
- `command-family-mismatch`: warning.
- `command-role-mismatch`: error.
- `logical-operator-arity-mismatch`: error.
- `empty-fact`: error.
- `empty-action`: error.
- `unsafe-set-target-object`: warning.
- `unscoped-duc-target`: warning.
- `up-build-place-point-coordinate-as-escrow`: warning.
- `duplicate-defconst-conflict`: warning in `default`; suppressed in `corpus`.
- `defconst-alias-cycle`: warning.
- `repeat-chat`: warning in `default`; suppressed in `corpus`.
- `up-can-build-zero-escrow`: warning in `default`; suppressed in `corpus`.
- `builtin-constant-alias`: info in principle, suppressed by `corpus`. Reports
  both numeric aliases such as `(defconst class-villager 904)` and symbolic
  aliases such as `(defconst class-villager villager-class)`.

By default, `lint-package` fails on `error`.

DUC search-state warnings are file-level heuristics. The validator tracks
retained local and remote search lists across rules until the relevant list is
cleared by `up-full-reset-search` or by `up-reset-search` arguments:

- `(up-reset-search _ 1 _ _)` clears retained local-list evidence.
- `(up-reset-search _ _ _ 1)` clears retained remote-list evidence.

These commands establish retained search-list evidence:

- `up-find-local` and `up-find-remote`.
- `up-set-group search-local` and `up-set-group search-remote`.
- `up-set-target-object` in facts, because a passing fact proves the indexed
  object exists in that list.

This matters for package validation because large community AIs often build a
DUC list in one rule, then consume it in the next rule.

To fail on warnings too:

```powershell
python -m aoe2_ai_lab lint-package extensions\aoe2-aiscript-cursor-local-lab\samples --fail-level warning
```

Known noisy finding codes can be suppressed per run:

```powershell
python -m aoe2_ai_lab lint-package "<package path>" --suppress-code repeat-chat
```

Use suppression for explicit triage decisions, not as a default import step.

## Confidence

Findings also have preprocessor confidence:

- `definite`: code is definitely reachable under the currently known local
  `defconst` state.
- `conditional`: code is retained because a preprocessor condition is unknown.

Unknown conditional code is intentionally kept active so the validator does not
hide possible problems.

Some structural findings are nonfatal. For example, malformed `defconst`,
`load`, `include`, or `load-random` entries are reported, but the linter still
continues into later rules when parentheses and rule structure remain safe to
parse. Fatal pre-parse issues, such as unbalanced parentheses, unterminated
rules, or malformed preprocessor blocks, stop deeper semantic checks so the
validator does not produce misleading command diagnostics from a broken parse
state.

The `corpus` profile keeps one extra low-noise guard for large legacy AIs: when
the only pre-parse findings are suppressed corpus-style findings, the linter
does not continue into deeper semantic checks for that file. This preserves
corpus triage stability without weakening default/project linting.

Package lint shares reachable `defconst` names and resolved numeric values
across the resolved load graph. Direct integer constants and simple alias chains
such as `(defconst gl-main gl-base)` are resolved when they ultimately point to
an integer; unknown symbols and cycles remain names only. That keeps cross-file
constants from producing false undefined warnings, and lets value-sensitive
checks such as `unsafe-goal-block` and `command-numeric-range-mismatch` work
when a goal constant is declared in a shared constants file.

By default, package lint fails only on definite findings at or above the failure
severity. Conditional findings are reported but do not fail unless requested.

Strict conditional failure:

```powershell
python -m aoe2_ai_lab lint-package extensions\aoe2-aiscript-cursor-local-lab\samples --fail-confidence conditional
```

Useful combinations:

```powershell
# Normal package validation: definite errors fail.
python -m aoe2_ai_lab lint-package extensions\aoe2-aiscript-cursor-local-lab\samples

# Strict error validation: definite and conditional errors fail.
python -m aoe2_ai_lab lint-package extensions\aoe2-aiscript-cursor-local-lab\samples --fail-confidence conditional

# Release-style strictness: warnings and errors fail, including conditional branches.
python -m aoe2_ai_lab lint-package extensions\aoe2-aiscript-cursor-local-lab\samples --fail-level warning --fail-confidence conditional
```

## Preprocessor Handling

The validator understands these `.per` preprocessor forms:

- `#load-if-defined NAME`
- `#load-if-not-defined NAME`
- `#else`
- `#end-if`
- simple inline payloads, such as:

```per
#load-if-defined UNKNOWN (load "maybe-active") #end-if
```

Known inactive branches are ignored for parsing, linting, and package load
discovery. Unknown branches are retained and marked `conditional`.

Line numbers in findings remain original source line numbers.

## XS Includes

Package lint resolves `(include "...")` entries found in reachable `.per` files.
Resolved `.xs` files are linted and reported under each root's `xs_files`.
Missing include targets produce `missing-include-target` errors with candidate
paths in JSON.

When an included `.xs` file is available locally, package lint also cross-checks
`xs-script-call` targets against visible XS function signatures. A call to a
function with one or more parameters is reported as
`xs-script-call-parameterized-function`, because AI scripts can only call
zero-parameter XS functions.

## Package Integrity

`lint-package` also reports package-level integrity:

- stale `.ai` roots: `.ai` files that do not resolve to a root `.per`.
- unreachable `.per` files: `.per` files not reachable from any resolved `.ai`
  root.
- duplicate root targets: multiple `.ai` files resolving to the same root
  `.per`.

If one `.ai` file contains multiple plain `load` entries or positive-weight
`load-random` entries, each resolved load is treated as a package root. This
prevents secondary entry scripts from being hidden as unreachable files.
Zero-weight `load-random` entries stay ignored.

For `load-random`, literal weights `<= 0` are treated as disabled. Literal
positive weights, default entries with no weight, and `+`/`+constant` entries
are treated as reachable candidates because they can select a file depending on
runtime/version behavior.

Reachable load graphs also report `load-cycle` when a load path loops back to a
file already active on the current stack, and `load-depth-exceeded` when nested
loads exceed the documented maximum depth of 10. The root file is depth 0; each
load edge increments the depth.

Stale `.ai` roots are integrity errors and fail package validation by default.
Unreachable `.per` files are integrity info by default. Duplicate root targets
are integrity warnings because they may be intentional personality entries.
`--fail-level warning` fails on duplicate roots, and `--fail-level info` also
fails on unreachable files.

## JSON Output

`--json` is the preferred interface for agents and CI.

Top-level fields:

- `path`
- `profile`
- `fail_level`
- `fail_confidence`
- `suppressed_codes`
- `failed`
- `root_count`
- `integrity`
- `totals`
- `issue_groups`
- `finding_groups`
- `roots`

Important `totals` fields:

- `finding_count`
- `severity_counts`
- `confidence_counts`
- `code_counts`
- `reachable_file_count`
- `xs_file_count`
- `file_confidence_counts`
- `failed_root_count`
- `definite_error_count`
- `conditional_error_count`
- `stale_ai_root_count`
- `unreachable_per_file_count`
- `duplicate_root_target_count`
- `integrity_severity_counts`
- `integrity_code_counts`

Each finding includes:

- `path`
- `line`
- `severity`
- `confidence`
- `code`
- `message`
- `suggestion`
- `span`

`span` is 0-based column data with 1-based line numbers:

- `start_line`
- `start_col`
- `end_line`
- `end_col`

Parser-backed command diagnostics prefer exact token spans from the parsed
expression tree. Older line-scan diagnostics may still use conservative fallback
spans inferred from the source line.

Top-level `issue_groups` is the preferred agent entry point when triaging a
package. It combines lint findings and package-integrity issues. Each group
contains:

- `code`
- `source`: `lint` or `integrity`
- `count`
- `severity_counts`
- `confidence_counts`
- `explanation`
- up to five representative `examples`

Top-level and per-root `finding_groups` contain the lint-only subset of
`issue_groups`. Keep using `integrity` for complete root-manifest details.

Each root also includes:

- `file_summaries` with per-file confidence, finding counts, severity counts,
  and code counts. Use this to find the relevant file in large community
  packages before reading individual findings.
- `constants`, a package symbol table for reachable `defconst` declarations.
  Each entry includes the name, raw value token, resolved integer value when
  available, path, line, and preprocessor confidence.

`integrity.root_manifest` lists each `.ai` root, whether it resolved or went
stale, the resolved `.per` roots, each load entry's source (`load`, `#load`, or
`load-random`), candidate paths, and skipped zero-weight `load-random` entries.
Use this first when debugging package structure.

Suggestions are conservative and intended to guide review, not blindly apply
patches. Examples include replacing a math operator in a `typeOp` slot, using a
real action instead of a `can-*` fact after `=>`, or adding a missing load file.

## Current Known Behaviors

- Parser-backed checks understand compact rules such as
  `(defrule (true) => (disable-self))` and multiple complete facts/actions on
  one line. Legacy token-scan checks ignore quoted text, so diagnostics are not
  produced from identifiers that only appear inside chat or string literals.
  Escaped quotes inside those strings are treated as string content by comment
  stripping, parenthesis balancing, expression splitting, and token scans.
- Recoverable structure errors such as `unterminated-defrule` and
  `unbalanced-parentheses` are still reported, but the linter continues into
  later recoverable rules where possible so one broken block does not hide all
  later semantic diagnostics. `defrule-missing-arrow` remains fatal because the
  parser cannot safely classify facts and actions without the separator.
  Preprocessor directive scanning also ignores `#load-if-defined`, `#else`, and
  `#end-if` text that appears inside quoted strings.
- `typeOp` slots accept modern `c:`, `g:`, `s:` and legacy redirect operators
  `c:<`, `g:<`, `s:<`.
- Math operators such as `g:=`, `c:-`, and `g:>=` do not belong in `typeOp`
  slots and are reported as `command-typed-prefix-mismatch`.
- Valid typed prefixes and typed operators can still point at the wrong kind of
  symbol. For example, `g: sn-maximum-town-size` and
  `g:= sn-maximum-town-size` are reported as
  `command-typed-operand-mismatch` because `sn-*` names normally require `s:`
  or `s:=` when reading the strategic number value.
- Direct id slots also get conservative family checks. For example,
  `(set-goal sn-maximum-town-size 1)` is reported as
  `command-family-mismatch` because a `GoalId` slot received an `sn-*`
  strategic-number-looking token. These checks use naming evidence only and are
  warnings.
- The validator applies narrow local schema corrections when the scraped AIRef
  signature conflicts with the command description and examples. For example,
  AIRef labels the first `up-compare-sn` argument as `GoalId`, but the command
  compares strategic numbers and its example uses `sn-maximum-town-size`, so the
  validator treats that slot as `SnId`.
- Unknown strategic numbers in strategic-number command slots report the
  specific `undefined-strategic-number` diagnostic without also emitting a
  generic `undefined-identifier` for the same token.
- Explicit command-specific argument restrictions are reported as
  `command-argument-mismatch`. For example, `up-set-placement-data` does not
  allow `any-*` or `every-*` wildcards in its `PlayerNumber` slot. The same
  single-player restriction is enforced for `up-get-player-color`,
  `up-get-upgrade-id`, `up-store-player-chat`, and `up-store-player-name`.
  It is also enforced for `up-get-player-fact` when that Fact/Action command is
  used in an action context.
  `up-find-player-flare` is checked separately: `any-*` is allowed, but
  `this-any-*` and `every-*` are reported because the command documentation says
  those forms are not designed for flare lookup.
- Literal numeric id slots and resolved integer `defconst` values are checked
  against explicit documented ranges. For example, `(set-goal 0 1)` is reported
  as `command-numeric-range-mismatch` because AIRef documents `GoalId` as
  `1 to 16000`. Dynamic typed values such as `g:` and `s:` are skipped because
  their runtime value cannot be known statically.
- Object, tech, and strategic-number symbols that only appear in the local
  non-DE archive remain invalid for DE validation, but the diagnostic message
  explains that they are archived non-DE symbols instead of reporting them as
  unknown symbols. This applies both to command-specific id slots and generic
  `c:` typed constants.
- `map-type` uses the local MapType registry plus narrow supplemental modern DE
  values when the scraped registry lags behind current maps. Keep this list
  small and evidence-based.
- `c:` typed constants are allowed to reference documented value-family
  constants such as attack stances without a local `defconst`.
- `can-research-with-escrow` is a fact, not an action. If it appears after
  `=>`, the validator reports `command-role-mismatch` and suggests `research`
  after escrow release or `up-research` with an escrow-state goal.
- `up-set-target-object` and DUC target warnings are heuristic. Treat them as
  review prompts unless the surrounding search lifecycle clearly proves a bug.
- `up-build place-point` uses the current target point from
  `up-set-target-point`. Its third argument remains `EscrowGoalId`, so
  `(up-build place-point gl-point-x c: mill)` is suspicious even when
  `gl-point-x` was just passed to `up-set-target-point`.
- `duplicate-defconst-conflict` only reports conflicting parsed values in
  definitely active code, including alias values such as
  `(defconst gl-state gl-opening)` and quoted text values. Conditional branches
  are ignored so civ/map/personality-specific constant tables do not produce
  false conflicts.
  The `corpus` profile suppresses it because some large legacy AIs deliberately
  reuse goal names in distant sections. Package lint also reports conflicting
  reachable definitions across files in the `default` profile.
- `defconst-alias-cycle` reports direct or indirect cycles such as
  `(defconst gl-a gl-b)` with `(defconst gl-b gl-a)`. Unknown aliases are still
  allowed; only cycles are reported. Package lint also checks cycles that span
  multiple reachable `.per` files when every definition in the cycle is
  definitely active.
- `malformed-defconst` reports structurally invalid constant declarations, such
  as missing names, missing values, unterminated quoted text, or multiple
  unquoted value tokens. The validator intentionally accepts broad legacy names
  such as `1TC-4MARKET` and alias values such as
  `(defconst food-sn sn-food-gatherer-percentage)`. Multiple compact
  declarations on one line, such as `(defconst a 1)(defconst b 2)`, are parsed
  as separate declarations.
- `malformed-load-directive` and `malformed-include-directive` report load graph
  directives that cannot be resolved reliably, usually because the target path
  is not quoted.
- `malformed-load-random-directive` reports structurally invalid `load-random`
  entries. The validator accepts literal weights, symbolic `+name` weights,
  bare `+` weights, and omitted weights, but each entry must target a quoted
  load path.
- `load-random-plus-weight-de-behavior` reports `+` and `+name` weight forms as
  DE-risky behavior, not syntax errors. AIRef documents those forms as
  UserPatch syntax and notes uncertain or bugged DE behavior. The `corpus`
  profile suppresses this because large legacy AIs may retain those forms for
  compatibility or historical reasons.
- `repeat-chat` is a project hygiene warning for probes and local AIs, where
  repeated chat can drown out useful diagnostics. Community AIs often use chat
  for strategy announcements, taunt responses, personality, or debug output, so
  `corpus` suppresses it as style noise rather than a package defect.
- `up-can-build 0` is documented by AIRef and common in community AIs, but our
  local DE logs have shown `Invalid goal used (0)` in some probes. The default
  profile keeps the warning so project scripts prefer a real
  `without-escrow` goal; the `corpus` profile suppresses it until we have a
  targeted in-game test that proves it should be treated as a package issue.
- Some `sn-target-evaluation-*` strategic numbers are accepted as
  binary-observed names because they appear in the DE executable string
  extracts, even though AIRef's version table marks them as non-DE/AoE1. This
  prevents false `undefined-strategic-number` noise in community AIs, but it is
  not a claim that each SN's behavior has been validated in-game.
- `duplicate-preprocessor-else` means one conditional block has two `#else`
  directives before the matching `#end-if`. If the enclosing preprocessor
  condition is unknown, this is reported as a conditional error: it should be
  reviewed, but it does not fail the default package gate unless
  `--fail-confidence conditional` is used.

## Recommended Agent Workflow

For `extensions\aoe2-aiscript-cursor-local-lab\samples`:

```powershell
$env:PYTHONPATH='src'
python -m aoe2_ai_lab lint-package extensions\aoe2-aiscript-cursor-local-lab\samples --profile default --json
python -m pytest tests -p no:cacheprovider
```

For imported community packs:

```powershell
$env:PYTHONPATH='src'
python -m aoe2_ai_lab lint-package "<package path>" --profile corpus --json
```

When triaging package output:

1. Start with `totals.definite_error_count`.
2. Review failed roots.
3. Review conditional errors separately.
4. Treat warnings as prioritization signals, not automatic failures.
5. Use `--fail-confidence conditional` only for strict validation passes.
