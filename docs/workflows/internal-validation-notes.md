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
