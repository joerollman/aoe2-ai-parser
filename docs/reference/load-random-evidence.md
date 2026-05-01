# Load Random Evidence

Use this note when deciding how to validate `(load-random ...)` entries.

## Current Rules

- Treat literal positive weights as reachable.
- Treat default entries without a weight as reachable.
- Treat literal weights `<= 0` as disabled for package-root discovery.
- Treat `+` and `+constant` weight entries as reachable but warn with
  `load-random-plus-weight-de-behavior` in normal lint profiles.

## Plus Weights

AIRef documents `+` and `+constant` as UserPatch syntax and notes uncertain or
bugged DE behavior. Because a plus-weight entry may still select a file in some
runtime/version contexts, package discovery keeps those targets reachable
instead of marking them unreachable.

Current validator behavior:

- `(load-random + "strategy")` and `(load-random +chance "strategy")` produce
  `load-random-plus-weight-de-behavior`.
- The `corpus` profile suppresses the warning because large community AIs often
  use this form intentionally.
- Package lint still follows plus-weight targets so later diagnostics inside the
  selected file are not hidden.

Do not mark plus-weight behavior as fully DE-validated until an in-game probe or
direct DE documentation confirms the exact selection behavior.

Useful local lookups:

```powershell
$env:PYTHONPATH='src'
python -m aoe2_ai_lab diagnostics load-random-plus-weight-de-behavior
rg -n "load-random|load-random-plus-weight-de-behavior" docs src tests
```
