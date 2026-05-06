# Internal Validation Notes

These notes are for maintainers and agents. Keep user-facing diagnostics focused
on what to fix; do not expose probe names, scenario files, or log paths in normal
lint output.

## Validation Standard

- Do not promote inferred behavior into parser truth.
- Parser rules should be based on directly observed behavior, imported reference
  data, or clearly documented source material.
- If a result is inferred from nearby behavior, mark it as inferred or pending
  and prefer a stronger probe before changing validator behavior.
- Strong probes should test the exact boundary or command context being modeled,
  not merely a nearby value or related command.

## Site-Specific Train Aliases

Public diagnostics:

- `site-specific-train-alias-requires-defconst`
- `site-specific-train-alias-requires-defconst-warning`

Internal validation source:

- Lab repo: `C:\Users\joero\programming-projects\aoe2-ai-lab`
- Scenario harness: `ai/site_specific_training_probes/sst_shared/sst_shared.per`
- Result notes: `ai/site_specific_training_probes/results.md`
- Action-train alias harness: `ai/unitline_action_train_alias_probes/ulat_alias_shared.per`
- Action-train alias result notes: `ai/unitline_action_train_alias_probes/results.md`
- Lab commit: `ed70484 Add canonical site-specific training scenario probe`

Validated behavior:

- `donjon-spearman` is not a built-in identifier; direct bare use failed at
  startup. It works as a local alias with `(defconst donjon-spearman 1786)`.
- `donjon-serjeant` works as a local alias with
  `(defconst donjon-serjeant 1660)` for direct `can-train`/`train`.
- `donjon-pikeman` works as a local alias with
  `(defconst donjon-pikeman 1787)`.
- `donjon-halberdier` works as a local alias with
  `(defconst donjon-halberdier 1788)`.
- `elite-donjon-serjeant`, `krepost-konnik`, and `elite-krepost-konnik` are
  valid built-in direct `train` targets in the validated fixture.
- `konnik-line` did not become trainable from a Krepost in the validated
  fixture.
- Do not mark Donjon/Krepost site-specific aliases as validated
  `up-target-point ... action-train c:` targets. In the alias action-train
  fixture, `donjon-serjeant`, `donjon-pikeman`, `elite-donjon-serjeant`,
  `krepost-konnik`, and `elite-krepost-konnik` reached `can-train` and issued
  from their site-specific buildings, but produced no unit before observation
  ended.
- `donjon-halberdier` did not reach `can-train` in the alias action-train
  fixture, despite being validated as a local alias for direct `train`.
- `shotel-line` remained the positive control for `action-train c:` and
  produced `shotel-warrior`.

Implementation note:

- User-facing messages should say these aliases require `defconst`; internal
  evidence can stay here and in the lab repo.

## Unit-Line Command Contexts

Public diagnostics:

- `command-argument-mismatch`

Internal validation source:

- Lab repo: `C:\Users\joero\programming-projects\aoe2-ai-lab`
- Scenario harness: `ai/unitline_context_probes`
- Scenario config: `docs/workflows/scenario-unitline-context-probes.config.json`
- Lab commits:
  - `8a2dccc Add unit-line context scenario probes`
  - `3eb93c1 Add player-count unit-line probe checks`

Validated behavior:

- `donjon-serjeant-line`, `donjon-spearman-line`, `krepost-konnik-line`, and
  `shotel-line` are valid bare `UnitId` arguments for
  `unit-type-count-total`.
- The same four symbols are valid bare `UnitId` arguments for
  `players-unit-type-count`.
- `shotel-line` is valid as a bare `UnitId` for direct `can-train` and
  `train`; direct training produced `shotel-warrior` and then
  `elite-shotel-warrior` in the fixture.
- `shotel-line` is valid as the `c:` target paired with `action-train` in
  `up-target-point`; an isolated action-train fixture produced
  `shotel-warrior` and then `elite-shotel-warrior`.
- Do not mark `donjon-serjeant-line`, `donjon-spearman-line`, or
  `krepost-konnik-line` as validated direct `can-train`/`train` targets.
- Do not mark `c:` `action-train` contexts for `donjon-serjeant-line`,
  `donjon-spearman-line`, or `krepost-konnik-line` as validated. In the
  isolated fixture, each issued but reached observation end without a
  production marker.

Implementation note:

- User-facing linter output should say the argument is not validated for that
  command slot, not reference the scenario fixture directly.

## Defconst Numeric Range

Public diagnostics:

- `defconst-value-out-of-range`

Internal validation source:

- Lab repo: `C:\Users\joero\programming-projects\aoe2-ai-lab`
- Scenario harnesses:
  - `ai/defconst_range_probe/defconst_range_probe.per` in the original
    broad-range probe.
  - `ai/defconst_range_probe/defconst_range_valid32.per`,
    `ai/defconst_range_probe/defconst_range_high_overflow.per`, and
    `ai/defconst_range_probe/defconst_range_low_overflow.per` in the boundary
    probe.
- Scenario config: `docs/workflows/scenario-defconst-range-probe.config.json`

Validated behavior:

- DE accepted and matched numeric `defconst` values outside signed 16-bit range:
  `32768`, `65536`, `350000`, `2000000`, and `-32769`.
- These values were assigned with `set-goal` and then successfully checked with
  `goal`, ending in `DEFCONST-RANGE ALL-TESTS-COMPLETE`.
- This contradicts the older local AI scripting limit note that numeric
  `defconst` values are C++ `short` values.
- DE accepted and matched the signed 32-bit boundary values:
  `2147483647` and `-2147483648`.
- DE also loaded the one-step overflow values `2147483648` and `-2147483649`,
  but clamped them when used as goal values:
  - `2147483648` matched `2147483647`.
  - `-2147483649` matched `-2147483648`.

Implementation note:

- Treat ordinary numeric `defconst` values as signed 32-bit integers for parser
  validation.
- Report values outside signed 32-bit range as warnings, not hard parse errors:
  validated one-step overflow values load but silently clamp, which is likely a
  script bug without being a startup failure.
- Keep command-parameter-specific range checks separate. A large constant can be
  legal as a `defconst` while still invalid for a parameter such as `GoalId`.
