# Validator Diagnostic Codes

Generated from `validator-diagnostic-codes.json`; edit the JSON and run `npm run generate:diagnostic-registry`. The same command also syncs the editor extension copy at `extensions/aoe2-aiscript-cursor-local-lab/data/diagnostic-codes.json`.

This is the registry for `aoe2_ai_lab` lint and package-integrity issue codes.
Use it when triaging `lint --json`, `lint-package --json`, Markdown reports, or VS Code/Cursor diagnostics.

Severity is the default validator severity. Confidence is per occurrence: `definite` for definitely reachable code and `conditional` when the finding is inside an unknown preprocessor branch.

Editor actions describe the current local VS Code/Cursor extension behavior:

- `quick fix`: an edit action may be offered.
- `explain`: a non-editing explanation action may be offered.
- `none`: no code action is currently wired.

## Profile Suppression

The `corpus` profile suppresses these compatibility/style codes:

- `builtin-constant-alias`
- `duplicate-defconst-conflict`
- `load-random-plus-weight-de-behavior`
- `redundant-built-in-defconst`
- `repeat-chat`
- `up-can-build-zero-escrow`

Manual `--suppress-code <code>` can suppress any finding code for one lint run. Package-integrity codes are not suppressible through linter profile suppression.

## Codes

| Code | Source | Severity | Corpus | Cursor action | Meaning |
| --- | --- | --- | --- | --- | --- |
| `bad-set-goal` | lint | error | active | none | `set-goal` is missing either the goal id or value. |
| `builtin-constant-alias` | lint | info | suppressed | none | A local `class-*` constant aliases a documented built-in class id or built-in class symbol. Prefer the built-in name. |
| `command-argument-mismatch` | lint | warning | active | quick fix, explain | A command argument does not match a known registry parameter family. This can be a real bug or a registry coverage gap. |
| `command-family-mismatch` | lint | warning | active | explain | A command argument is in a direct id slot but its symbol name strongly suggests a different family, such as an `sn-*` strategic number in a `GoalId` slot. |
| `command-numeric-range-mismatch` | lint | warning | active | explain | A literal numeric command argument or resolved integer `defconst` is outside an explicit documented range for that parameter, such as `0` in a `GoalId` slot documented as `1 to 16000`. |
| `command-arity-mismatch` | lint | error | active | none | A schema-validated command has the wrong number of arguments. |
| `command-role-mismatch` | lint | error | active | explain | A command documented as Fact/Action/FactAction is used in the wrong rule side or nested context. |
| `command-typed-prefix-mismatch` | lint | error | active | quick fix, explain | A `typeOp` slot received a math/compare operator such as `g:=` instead of a plain type prefix such as `g:`. |
| `command-typed-operand-mismatch` | lint | warning | active | explain | A valid typed prefix or typed operator is followed by an operand whose name strongly suggests a different type, such as `g:` or `g:=` before an `sn-*` strategic number. |
| `defrule-missing-arrow` | lint | error | active | none | A `defrule` closed without an `=>` separator. |
| `defconst-alias-cycle` | lint | warning | active | none | A set of `defconst` aliases forms a cycle, so the constants cannot resolve to a numeric value. |
| `defconst-value-out-of-range` | lint | error | active | explain | A numeric `defconst` value is outside the documented signed 16-bit range of -32768 to 32767. |
| `duplicate-preprocessor-else` | preprocessor | error | active | none | One `#load-if-defined` or `#load-if-not-defined` block contains more than one `#else`. |
| `duplicate-root-target` | integrity | warning | active | none | Multiple `.ai` files resolve to the same root `.per`. This can be intentional for personalities but should be explicit. |
| `duplicate-defconst-conflict` | lint | warning | suppressed | none | A definitely active file assigns two different parsed values to the same `defconst` name. |
| `empty-action` | lint | error | active | none | A rule has no actions after `=>`. |
| `empty-fact` | lint | error | active | none | A rule has no facts before `=>`. |
| `include-missing-xs-extension` | lint | error | active | none | An AI `include` directive has a quoted target that does not include the required `.xs` file extension. |
| `livestock-default-point` | lint | warning | active | none | Livestock targeting uses `action-default` where `action-move` is usually expected. |
| `logical-operator-arity-mismatch` | lint | error | active | none | A logical operator has the wrong number of direct child facts. `not` expects one child fact; binary operators such as `and` and `or` expect two. |
| `load-cycle` | package lint | error | active | none | The reachable load graph cycles back to an already-active `.per` file. |
| `load-depth-exceeded` | package lint | error | active | none | The reachable load graph exceeds the documented maximum nested load depth of 10. |
| `malformed-preprocessor-directive` | preprocessor | error | active | none | A preprocessor directive has invalid syntax, such as a missing condition token. |
| `preprocessor-nesting-depth-exceeded` | preprocessor | error | active | none | `#load-if-defined` and `#load-if-not-defined` conditionals are nested more than the documented maximum of 50 levels. |
| `malformed-defconst` | lint | error | active | none | A `defconst` declaration is structurally invalid, such as a missing name, missing value, unterminated quoted text value, or multiple unquoted value tokens. |
| `malformed-include-directive` | lint | error | active | none | An `include` directive is structurally invalid, usually because its target is not quoted. |
| `malformed-load-directive` | lint | error | active | none | A `load` or `#load` directive is structurally invalid, usually because its target is not quoted. |
| `malformed-load-random-directive` | lint | error | active | none | A `load-random` directive has a structurally invalid entry. Entries should be an optional weight followed by a quoted target. |
| `load-random-plus-weight-de-behavior` | lint | warning | suppressed | none | A `load-random` entry uses a `+` weight form. AIRef documents this as UserPatch syntax and notes uncertain or bugged DE behavior. |
| `missing-include-target` | package lint | error | active | none | An `(include "...")` target could not be resolved. |
| `missing-load-target` | package lint | error | active | quick fix, explain | A `(load "...")` or `#load` target could not be resolved. |
| `raw-load-in-per` | lint | error | active | none | A raw `#load` directive appears in an installed `.per`; assemble components before install. |
| `redundant-built-in-defconst` | lint | info | suppressed | quick fix, explain | A local `defconst` redefines a documented built-in class constant by the same name. |
| `repeat-chat` | lint | warning | suppressed | explain | A chat action may repeat every rule pass because the rule is not disabled or guarded. |
| `rule-too-long` | lint | error | active | none | A rule exceeds DE's 32 element limit for facts/actions/logical operators. |
| `split-typed-comparison` | lint | error | active | none | A typed comparison was split, such as `< g:` instead of `g:<`. |
| `source-line-too-long` | lint | error | active | none | A source line exceeds the documented 255-character AI script line limit, including comments. |
| `stale-ai-root` | integrity | error | active | none | An `.ai` file did not resolve to any root `.per`. |
| `unbalanced-parentheses` | lint | error | active | none | Parentheses close too early or the file is missing closing parentheses. |
| `undefined-constant` | lint | warning | active | quick fix | A value after `c:` is not a known built-in, documented value, or reachable `defconst`. |
| `undefined-identifier` | lint | warning | active | quick fix | A token looks like an AoE identifier but is not known in reachable constants or local reference data. |
| `undefined-position-constant` | lint | warning | active | quick fix | A position token used by `up-get-point` is not a built-in or reachable `defconst`. |
| `undefined-strategic-number` | lint | warning | active | quick fix | A strategic-number token is not in the local DE SN registry or reachable constants. |
| `unexpected-preprocessor-else` | preprocessor | error | active | none | `#else` appears without a matching active preprocessor conditional. |
| `unexpected-preprocessor-end-if` | preprocessor | error | active | none | `#end-if` appears without a matching active preprocessor conditional. |
| `unreachable-per-file` | integrity | info | active | none | A `.per` file exists in the package but is not reachable from any resolved `.ai` root. |
| `unsafe-goal-block` | lint | warning | active | none | A command writes a block of goals too low in the goal range; use safer higher goals. |
| `unsafe-set-target-object` | lint | warning | active | explain | `up-set-target-object` reads a search list before retained search evidence proves that list was rebuilt. |
| `unscoped-duc-target` | lint | warning | active | explain | A DUC target command runs without retained evidence that local target objects exist. |
| `unsupported-ai-xs-function` | XS lint | error | active | none | An XS function is known to be rejected by the AoE2 DE AI XS parser. |
| `xs-script-call-parameterized-function` | package lint | warning | active | none | `xs-script-call` targets an included XS function that has one or more parameters. AI scripts can only call zero-parameter XS functions. |
| `unterminated-defrule` | lint | error | active | none | A new `defrule` starts before the previous one closed. |
| `unterminated-preprocessor-conditional` | preprocessor | error | active | none | A preprocessor conditional is missing its matching `#end-if`. |
| `up-build-place-point-coordinate-as-escrow` | lint | warning | active | explain | `up-build place-point` uses the current target point; its third argument is still escrow state, not a coordinate. |
| `up-can-build-zero-escrow` | lint | warning | suppressed | explain | `up-can-build` uses literal `0` for escrow state; project scripts should prefer a named `without-escrow` goal. |

## Code Details

<a id="diagnostic-bad-set-goal"></a>

### `bad-set-goal`

- Source: lint
- Default severity: error
- Corpus profile: active
- Cursor action: none
- Meaning: `set-goal` is missing either the goal id or value.

<a id="diagnostic-builtin-constant-alias"></a>

### `builtin-constant-alias`

- Source: lint
- Default severity: info
- Corpus profile: suppressed
- Cursor action: none
- Meaning: A local `class-*` constant aliases a documented built-in class id or built-in class symbol. Prefer the built-in name.

<a id="diagnostic-command-argument-mismatch"></a>

### `command-argument-mismatch`

- Source: lint
- Default severity: warning
- Corpus profile: active
- Cursor action: quick fix, explain
- Meaning: A command argument does not match a known registry parameter family. This can be a real bug or a registry coverage gap.

<a id="diagnostic-command-family-mismatch"></a>

### `command-family-mismatch`

- Source: lint
- Default severity: warning
- Corpus profile: active
- Cursor action: explain
- Meaning: A command argument is in a direct id slot but its symbol name strongly suggests a different family, such as an `sn-*` strategic number in a `GoalId` slot.

<a id="diagnostic-command-numeric-range-mismatch"></a>

### `command-numeric-range-mismatch`

- Source: lint
- Default severity: warning
- Corpus profile: active
- Cursor action: explain
- Meaning: A literal numeric command argument or resolved integer `defconst` is outside an explicit documented range for that parameter, such as `0` in a `GoalId` slot documented as `1 to 16000`.

<a id="diagnostic-command-arity-mismatch"></a>

### `command-arity-mismatch`

- Source: lint
- Default severity: error
- Corpus profile: active
- Cursor action: none
- Meaning: A schema-validated command has the wrong number of arguments.

<a id="diagnostic-command-role-mismatch"></a>

### `command-role-mismatch`

- Source: lint
- Default severity: error
- Corpus profile: active
- Cursor action: explain
- Meaning: A command documented as Fact/Action/FactAction is used in the wrong rule side or nested context.

<a id="diagnostic-command-typed-prefix-mismatch"></a>

### `command-typed-prefix-mismatch`

- Source: lint
- Default severity: error
- Corpus profile: active
- Cursor action: quick fix, explain
- Meaning: A `typeOp` slot received a math/compare operator such as `g:=` instead of a plain type prefix such as `g:`.

<a id="diagnostic-command-typed-operand-mismatch"></a>

### `command-typed-operand-mismatch`

- Source: lint
- Default severity: warning
- Corpus profile: active
- Cursor action: explain
- Meaning: A valid typed prefix or typed operator is followed by an operand whose name strongly suggests a different type, such as `g:` or `g:=` before an `sn-*` strategic number.

<a id="diagnostic-defrule-missing-arrow"></a>

### `defrule-missing-arrow`

- Source: lint
- Default severity: error
- Corpus profile: active
- Cursor action: none
- Meaning: A `defrule` closed without an `=>` separator.

<a id="diagnostic-defconst-alias-cycle"></a>

### `defconst-alias-cycle`

- Source: lint
- Default severity: warning
- Corpus profile: active
- Cursor action: none
- Meaning: A set of `defconst` aliases forms a cycle, so the constants cannot resolve to a numeric value.

<a id="diagnostic-defconst-value-out-of-range"></a>

### `defconst-value-out-of-range`

- Source: lint
- Default severity: error
- Corpus profile: active
- Cursor action: explain
- Meaning: A numeric `defconst` value is outside the documented signed 16-bit range of -32768 to 32767.

<a id="diagnostic-duplicate-preprocessor-else"></a>

### `duplicate-preprocessor-else`

- Source: preprocessor
- Default severity: error
- Corpus profile: active
- Cursor action: none
- Meaning: One `#load-if-defined` or `#load-if-not-defined` block contains more than one `#else`.

<a id="diagnostic-duplicate-root-target"></a>

### `duplicate-root-target`

- Source: integrity
- Default severity: warning
- Corpus profile: active
- Cursor action: none
- Meaning: Multiple `.ai` files resolve to the same root `.per`. This can be intentional for personalities but should be explicit.

<a id="diagnostic-duplicate-defconst-conflict"></a>

### `duplicate-defconst-conflict`

- Source: lint
- Default severity: warning
- Corpus profile: suppressed
- Cursor action: none
- Meaning: A definitely active file assigns two different parsed values to the same `defconst` name.

<a id="diagnostic-empty-action"></a>

### `empty-action`

- Source: lint
- Default severity: error
- Corpus profile: active
- Cursor action: none
- Meaning: A rule has no actions after `=>`.

<a id="diagnostic-empty-fact"></a>

### `empty-fact`

- Source: lint
- Default severity: error
- Corpus profile: active
- Cursor action: none
- Meaning: A rule has no facts before `=>`.

<a id="diagnostic-include-missing-xs-extension"></a>

### `include-missing-xs-extension`

- Source: lint
- Default severity: error
- Corpus profile: active
- Cursor action: none
- Meaning: An AI `include` directive has a quoted target that does not include the required `.xs` file extension.

<a id="diagnostic-livestock-default-point"></a>

### `livestock-default-point`

- Source: lint
- Default severity: warning
- Corpus profile: active
- Cursor action: none
- Meaning: Livestock targeting uses `action-default` where `action-move` is usually expected.

<a id="diagnostic-logical-operator-arity-mismatch"></a>

### `logical-operator-arity-mismatch`

- Source: lint
- Default severity: error
- Corpus profile: active
- Cursor action: none
- Meaning: A logical operator has the wrong number of direct child facts. `not` expects one child fact; binary operators such as `and` and `or` expect two.

<a id="diagnostic-load-cycle"></a>

### `load-cycle`

- Source: package lint
- Default severity: error
- Corpus profile: active
- Cursor action: none
- Meaning: The reachable load graph cycles back to an already-active `.per` file.

<a id="diagnostic-load-depth-exceeded"></a>

### `load-depth-exceeded`

- Source: package lint
- Default severity: error
- Corpus profile: active
- Cursor action: none
- Meaning: The reachable load graph exceeds the documented maximum nested load depth of 10.

<a id="diagnostic-malformed-preprocessor-directive"></a>

### `malformed-preprocessor-directive`

- Source: preprocessor
- Default severity: error
- Corpus profile: active
- Cursor action: none
- Meaning: A preprocessor directive has invalid syntax, such as a missing condition token.

<a id="diagnostic-preprocessor-nesting-depth-exceeded"></a>

### `preprocessor-nesting-depth-exceeded`

- Source: preprocessor
- Default severity: error
- Corpus profile: active
- Cursor action: none
- Meaning: `#load-if-defined` and `#load-if-not-defined` conditionals are nested more than the documented maximum of 50 levels.

<a id="diagnostic-malformed-defconst"></a>

### `malformed-defconst`

- Source: lint
- Default severity: error
- Corpus profile: active
- Cursor action: none
- Meaning: A `defconst` declaration is structurally invalid, such as a missing name, missing value, unterminated quoted text value, or multiple unquoted value tokens.

<a id="diagnostic-malformed-include-directive"></a>

### `malformed-include-directive`

- Source: lint
- Default severity: error
- Corpus profile: active
- Cursor action: none
- Meaning: An `include` directive is structurally invalid, usually because its target is not quoted.

<a id="diagnostic-malformed-load-directive"></a>

### `malformed-load-directive`

- Source: lint
- Default severity: error
- Corpus profile: active
- Cursor action: none
- Meaning: A `load` or `#load` directive is structurally invalid, usually because its target is not quoted.

<a id="diagnostic-malformed-load-random-directive"></a>

### `malformed-load-random-directive`

- Source: lint
- Default severity: error
- Corpus profile: active
- Cursor action: none
- Meaning: A `load-random` directive has a structurally invalid entry. Entries should be an optional weight followed by a quoted target.

<a id="diagnostic-load-random-plus-weight-de-behavior"></a>

### `load-random-plus-weight-de-behavior`

- Source: lint
- Default severity: warning
- Corpus profile: suppressed
- Cursor action: none
- Meaning: A `load-random` entry uses a `+` weight form. AIRef documents this as UserPatch syntax and notes uncertain or bugged DE behavior.

<a id="diagnostic-missing-include-target"></a>

### `missing-include-target`

- Source: package lint
- Default severity: error
- Corpus profile: active
- Cursor action: none
- Meaning: An `(include "...")` target could not be resolved.

<a id="diagnostic-missing-load-target"></a>

### `missing-load-target`

- Source: package lint
- Default severity: error
- Corpus profile: active
- Cursor action: quick fix, explain
- Meaning: A `(load "...")` or `#load` target could not be resolved.

<a id="diagnostic-raw-load-in-per"></a>

### `raw-load-in-per`

- Source: lint
- Default severity: error
- Corpus profile: active
- Cursor action: none
- Meaning: A raw `#load` directive appears in an installed `.per`; assemble components before install.

<a id="diagnostic-redundant-built-in-defconst"></a>

### `redundant-built-in-defconst`

- Source: lint
- Default severity: info
- Corpus profile: suppressed
- Cursor action: quick fix, explain
- Meaning: A local `defconst` redefines a documented built-in class constant by the same name.

<a id="diagnostic-repeat-chat"></a>

### `repeat-chat`

- Source: lint
- Default severity: warning
- Corpus profile: suppressed
- Cursor action: explain
- Meaning: A chat action may repeat every rule pass because the rule is not disabled or guarded.

<a id="diagnostic-rule-too-long"></a>

### `rule-too-long`

- Source: lint
- Default severity: error
- Corpus profile: active
- Cursor action: none
- Meaning: A rule exceeds DE's 32 element limit for facts/actions/logical operators.

<a id="diagnostic-split-typed-comparison"></a>

### `split-typed-comparison`

- Source: lint
- Default severity: error
- Corpus profile: active
- Cursor action: none
- Meaning: A typed comparison was split, such as `< g:` instead of `g:<`.

<a id="diagnostic-source-line-too-long"></a>

### `source-line-too-long`

- Source: lint
- Default severity: error
- Corpus profile: active
- Cursor action: none
- Meaning: A source line exceeds the documented 255-character AI script line limit, including comments.

<a id="diagnostic-stale-ai-root"></a>

### `stale-ai-root`

- Source: integrity
- Default severity: error
- Corpus profile: active
- Cursor action: none
- Meaning: An `.ai` file did not resolve to any root `.per`.

<a id="diagnostic-unbalanced-parentheses"></a>

### `unbalanced-parentheses`

- Source: lint
- Default severity: error
- Corpus profile: active
- Cursor action: none
- Meaning: Parentheses close too early or the file is missing closing parentheses.

<a id="diagnostic-undefined-constant"></a>

### `undefined-constant`

- Source: lint
- Default severity: warning
- Corpus profile: active
- Cursor action: quick fix
- Meaning: A value after `c:` is not a known built-in, documented value, or reachable `defconst`.

<a id="diagnostic-undefined-identifier"></a>

### `undefined-identifier`

- Source: lint
- Default severity: warning
- Corpus profile: active
- Cursor action: quick fix
- Meaning: A token looks like an AoE identifier but is not known in reachable constants or local reference data.

<a id="diagnostic-undefined-position-constant"></a>

### `undefined-position-constant`

- Source: lint
- Default severity: warning
- Corpus profile: active
- Cursor action: quick fix
- Meaning: A position token used by `up-get-point` is not a built-in or reachable `defconst`.

<a id="diagnostic-undefined-strategic-number"></a>

### `undefined-strategic-number`

- Source: lint
- Default severity: warning
- Corpus profile: active
- Cursor action: quick fix
- Meaning: A strategic-number token is not in the local DE SN registry or reachable constants.

<a id="diagnostic-unexpected-preprocessor-else"></a>

### `unexpected-preprocessor-else`

- Source: preprocessor
- Default severity: error
- Corpus profile: active
- Cursor action: none
- Meaning: `#else` appears without a matching active preprocessor conditional.

<a id="diagnostic-unexpected-preprocessor-end-if"></a>

### `unexpected-preprocessor-end-if`

- Source: preprocessor
- Default severity: error
- Corpus profile: active
- Cursor action: none
- Meaning: `#end-if` appears without a matching active preprocessor conditional.

<a id="diagnostic-unreachable-per-file"></a>

### `unreachable-per-file`

- Source: integrity
- Default severity: info
- Corpus profile: active
- Cursor action: none
- Meaning: A `.per` file exists in the package but is not reachable from any resolved `.ai` root.

<a id="diagnostic-unsafe-goal-block"></a>

### `unsafe-goal-block`

- Source: lint
- Default severity: warning
- Corpus profile: active
- Cursor action: none
- Meaning: A command writes a block of goals too low in the goal range; use safer higher goals.

<a id="diagnostic-unsafe-set-target-object"></a>

### `unsafe-set-target-object`

- Source: lint
- Default severity: warning
- Corpus profile: active
- Cursor action: explain
- Meaning: `up-set-target-object` reads a search list before retained search evidence proves that list was rebuilt.

<a id="diagnostic-unscoped-duc-target"></a>

### `unscoped-duc-target`

- Source: lint
- Default severity: warning
- Corpus profile: active
- Cursor action: explain
- Meaning: A DUC target command runs without retained evidence that local target objects exist.

<a id="diagnostic-unsupported-ai-xs-function"></a>

### `unsupported-ai-xs-function`

- Source: XS lint
- Default severity: error
- Corpus profile: active
- Cursor action: none
- Meaning: An XS function is known to be rejected by the AoE2 DE AI XS parser.

<a id="diagnostic-xs-script-call-parameterized-function"></a>

### `xs-script-call-parameterized-function`

- Source: package lint
- Default severity: warning
- Corpus profile: active
- Cursor action: none
- Meaning: `xs-script-call` targets an included XS function that has one or more parameters. AI scripts can only call zero-parameter XS functions.

<a id="diagnostic-unterminated-defrule"></a>

### `unterminated-defrule`

- Source: lint
- Default severity: error
- Corpus profile: active
- Cursor action: none
- Meaning: A new `defrule` starts before the previous one closed.

<a id="diagnostic-unterminated-preprocessor-conditional"></a>

### `unterminated-preprocessor-conditional`

- Source: preprocessor
- Default severity: error
- Corpus profile: active
- Cursor action: none
- Meaning: A preprocessor conditional is missing its matching `#end-if`.

<a id="diagnostic-up-build-place-point-coordinate-as-escrow"></a>

### `up-build-place-point-coordinate-as-escrow`

- Source: lint
- Default severity: warning
- Corpus profile: active
- Cursor action: explain
- Meaning: `up-build place-point` uses the current target point; its third argument is still escrow state, not a coordinate.

<a id="diagnostic-up-can-build-zero-escrow"></a>

### `up-can-build-zero-escrow`

- Source: lint
- Default severity: warning
- Corpus profile: suppressed
- Cursor action: explain
- Meaning: `up-can-build` uses literal `0` for escrow state; project scripts should prefer a named `without-escrow` goal.

## Triage Notes

- Start package triage from top-level `issue_groups` in `lint-package --json`.
- Treat `command-argument-mismatch`, `unsafe-set-target-object`, and `unscoped-duc-target` as review prompts unless the surrounding script context clearly proves a bug.
- Treat `stale-ai-root` as a package failure by default.
- Treat `duplicate-root-target` as warning-level package hygiene; community AI personalities can intentionally share a root script.
- Treat `unreachable-per-file` as info unless you are pruning package files or enforcing a release package.
