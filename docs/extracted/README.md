# Extracted Reference Data

This folder contains offline reference data imported or derived from AIRef,
AoE2 DE binary strings, XS docs, and RMS guide material.

For normal scripting work, do not browse raw files first. Use:

```powershell
$env:PYTHONPATH='src'
python -m aoe2_ai_lab resolve-reference <token>
```

## Layout

- [inventories/](./inventories/README.md): generated JSON inventories loaded by
  `resolve-reference` and `search-registry`.
- [offline-reference-map.md](./offline-reference-map.md): token-to-inventory
  lookup map.
- [offline-reference-completeness.md](./offline-reference-completeness.md):
  coverage summary.
- [non-de-object-archive.md](./non-de-object-archive.md): object entries
  excluded from the active DE inventory.
- [non-de-tech-archive.md](./non-de-tech-archive.md): tech entries excluded
  from the active DE inventory.
- [xs-agent-reference.md](./xs-agent-reference.md): XS-specific workflow.

## Inventory Commands

Common lookups:

```powershell
$env:PYTHONPATH='src'
python -m aoe2_ai_lab resolve-reference up-target-point
python -m aoe2_ai_lab resolve-reference villager-class --kind value-entry
python -m aoe2_ai_lab resolve-reference xsChatData --kind xs-function-inventory
python -m aoe2_ai_lab resolve-reference Conditionals --kind rms-topic-inventory
```

Regeneration targets write under `inventories/` by default when source evidence
is available:

```powershell
$env:PYTHONPATH='src'
python -m aoe2_ai_lab scrape-airef-commands
python -m aoe2_ai_lab scrape-airef-parameters
python -m aoe2_ai_lab scrape-airef-strategic-numbers
python -m aoe2_ai_lab scrape-airef-value-families
python -m aoe2_ai_lab scrape-airef-objects
python -m aoe2_ai_lab scrape-airef-techs
python -m aoe2_ai_lab scrape-xs-functions
python -m aoe2_ai_lab scrape-xs-constants
```

## Evidence Rule

Raw files are evidence, not proof. Use this ladder:

1. Raw/binary string exists.
2. AIRef/community docs provide syntax or semantic claims.
3. The project linter accepts the source.
4. The game parser accepts the installed script.
5. An isolated in-game probe confirms runtime behavior.

Only step 5 should upgrade behavior to `observed` in project docs.
