# Offline Reference Completeness

This file is for agents. It answers one question: which local JSON inventory
should be used for a given AoE2 AI scripting token or category.

## Coverage Summary

The offline reference layer is complete for the main authoring categories used
in `.per` scripting and local tooling:

- commands
- parameters
- strategic numbers
- XS functions
- XS constants
- RMS fixtures
- RMS guide topics
- facts, actions, comparison operators, math operators, DUC actions
- classes, resource types, position types, object-data constants
- objects
- techs
- parser-maintained symbol notes for locally observed edge cases
- project-observed command behavior

## Canonical Local Inventories

| Category | Local file | Resolver kind |
| --- | --- | --- |
| Commands | `inventories/airef-command-inventory.json` | `command-inventory` |
| Parameters | `inventories/airef-parameter-inventory.json` | `parameter-inventory` |
| Strategic numbers | `inventories/airef-strategic-number-inventory.json` | `strategic-number-inventory` |
| Enum/value families | `inventories/airef-value-family-inventory.json` | `value-family`, `value-entry` |
| Objects | `inventories/airef-object-inventory.json` | `object-inventory` |
| Techs | `inventories/airef-tech-inventory.json` | `tech-inventory` |
| XS functions | `inventories/xs-function-inventory.json` | `xs-function-inventory` |
| XS constants | `inventories/xs-constant-inventory.json` | `xs-constant-inventory` |
| RMS fixtures | `inventories/rms-fixture-registry.json` | `rms-fixture` |
| RMS guide topics | `inventories/rms-topic-inventory.json` | `rms-topic-inventory` |
| Parser-maintained symbol notes | `inventories/aoe2-ai-parser-local-symbol-notes.json` | `local-symbol-note` |
| Locally observed behavior | `inventories/airef-site-registry.json` | `validated-command` |
| Local risky/mixed notes | `inventories/airef-site-registry.json` | `project-command-note` |
| Executable-only evidence | `inventories/airef-site-registry.json` plus `raw/aoe2de/` files | `binary-token`, `binary-family` opt-in or fallback only |

## Requested Categories Mapped

| Requested category | Local resolver kind |
| --- | --- |
| Commands | `command-inventory` |
| Facts | `value-entry` under `FactId` or `command-inventory` when fact-like names are commands |
| Actions | `value-entry` under `ActionId` or `DUCAction` |
| Math operations | `value-entry` under `mathOp`; use the `id` field as the DE ID, with `legacy_id` preserved separately |
| DUC actions | `value-entry` under `DUCAction` |
| Classes | `value-entry` under `ClassId` |
| Resource types | `value-entry` under `Resource` |
| Comparison operations | `value-entry` under `compareOp`; use the `id` field as the DE ID, with `legacy_id` preserved separately |
| Position types | `value-entry` under `PositionType` |
| Object-data constants | `value-entry` under `ObjectData` |
| Strategic numbers | `strategic-number-inventory` |
| Objects | `object-inventory` |
| Techs | `tech-inventory` |
| Parser-maintained symbol notes | `local-symbol-note` |
| XS functions | `xs-function-inventory` |
| XS constants | `xs-constant-inventory` |
| RMS test maps | `rms-fixture` |
| RMS language topics | `rms-topic-inventory` |

## Resolver Priority

Use the local layers in this order:

1. `validated-command`
2. `command-inventory`
3. `parameter-inventory`
4. `strategic-number-inventory`
5. `value-entry`
6. `object-inventory`
7. `tech-inventory`
8. `xs-function-inventory`
9. `xs-constant-inventory`
10. `rms-fixture`
11. `rms-topic-inventory`
12. `local-symbol-note`
13. `project-command-note`
14. `binary-token`

The intent is simple:

- use `validated-command` for behavior we have actually observed in project
  probes or scripts
- use imported AIRef inventories for raw offline reference
- use binary evidence only when structured local docs do not answer the question;
  default registry search hides binary entries unless `--kind binary-token` or
  `--kind binary-family` is requested explicitly

## Current Inventory Counts

Current generated counts:

- commands: `385`
- parameters: `121`
- strategic numbers: `171` (`169` AIRef entries with `de = 1`, plus `2`
  local DE binary-only supplements)
- value families: `56`
- objects: `929` (`DE` entries only; excluded entries are archived in
  `non-de-object-archive.md`)
- techs: `327` (`DE` entries only; excluded entries are archived in
  `non-de-tech-archive.md`)
- xs functions: `239`
- xs constants: `831`
- rms fixtures: `13`
- rms topics: `39`
- local symbol notes: `11`

These counts include widened object and tech coverage across:

- `standard`
- `ror`
- `chronicles`

## Known Limits

- `validated-command` is intentionally strict. A command does not belong there
  until local project behavior has been observed.
- Shell-hostile raw operator tokens such as `c:<` are still present locally,
  but alias text such as `less-than` is easier to query from PowerShell.
- Binary string presence does not prove runtime behavior.

## Default Agent Workflow

Resolve the token first:

```powershell
$env:PYTHONPATH='src'
python -m aoe2_ai_lab resolve-reference up-target-point
python -m aoe2_ai_lab resolve-reference action-garrison --kind value-entry
python -m aoe2_ai_lab resolve-reference Archer --kind object-inventory
```

If the result is not enough, widen to:

```powershell
$env:PYTHONPATH='src'
python -m aoe2_ai_lab search-registry garrison
```
