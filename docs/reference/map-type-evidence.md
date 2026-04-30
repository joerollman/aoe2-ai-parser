# Map Type Evidence

Use this note when deciding whether a `(map-type <MapType>)` value should be
accepted, warned, or rejected.

## Current Rules

- Accept values present in the local `MapType` registry.
- Accept `custom` as a narrow supplemental alias for custom maps.
- Warn on `(map-type michi)` until direct AI-script evidence is found.

## Michi

Observed evidence:

- Community AI scripts use `(map-type michi)`.
- Community AI scripts also use `UP-MICHI-STYLE` / local constants derived from
  Michi-style RMS metadata.
- RMS documentation and community references describe Michi as the separate
  `ai_info_map_type` Michi-style flag, not clearly as the first map-type
  argument.

Current validator behavior:

- `(map-type michi)` reports `command-argument-mismatch` with a targeted message
  explaining that it is observed but unverified.
- Do not move `michi` into accepted supplemental MapType values until either an
  in-game probe confirms the fact or direct documentation says it is a valid
  `map-type` value.

Useful local lookups:

```powershell
$env:PYTHONPATH='src'
python -m aoe2_ai_lab resolve-reference map-type
python -m aoe2_ai_lab resolve-reference custom_map
rg -n "michi|MICHI|UP-MICHI-STYLE|ai_info_map_type" docs .tmp src
```
