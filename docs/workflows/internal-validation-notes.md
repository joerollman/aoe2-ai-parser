# Internal Validation Notes

These notes are for maintainers and agents. Keep user-facing diagnostics focused
on what to fix; do not expose probe names, scenario files, or log paths in normal
lint output.

## Site-Specific Train Aliases

Public diagnostics:

- `site-specific-train-alias-requires-defconst`
- `site-specific-train-alias-requires-defconst-warning`

Internal validation source:

- Lab repo: `C:\Users\joero\programming-projects\aoe2-ai-lab`
- Scenario harness: `ai/site_specific_training_probes/sst_shared/sst_shared.per`
- Result notes: `ai/site_specific_training_probes/results.md`
- Lab commit: `ed70484 Add canonical site-specific training scenario probe`

Validated behavior:

- `donjon-spearman` is not a built-in identifier; direct bare use failed at
  startup. It works as a local alias with `(defconst donjon-spearman 1786)`.
- `donjon-pikeman` works as a local alias with
  `(defconst donjon-pikeman 1787)`.
- `donjon-halberdier` works as a local alias with
  `(defconst donjon-halberdier 1788)`.
- `elite-donjon-serjeant`, `krepost-konnik`, and `elite-krepost-konnik` are
  valid built-in direct `train` targets in the validated fixture.
- `konnik-line` did not become trainable from a Krepost in the validated
  fixture.

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
- Do not mark `donjon-serjeant-line`, `donjon-spearman-line`, or
  `krepost-konnik-line` as validated direct `can-train`/`train` targets.
- Do not mark `c:` `action-train` contexts for these local unit lines as
  validated yet.

Implementation note:

- User-facing linter output should say the argument is not validated for that
  command slot, not reference the scenario fixture directly.
