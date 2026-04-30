# XS Agent Reference

This file is for agents. It summarizes how to use the local XS reference
material without falling back to web docs first.

External source-of-truth references folded into this local layer:

- Forgotten Empires XS reference
- AoE2DE UGC Guide XS beginner guide

## Primary Local Sources

- `inventories/xs-function-inventory.json`: structured local XS function
  inventory.
- `inventories/xs-constant-inventory.json`: structured local XS constant
  inventory from the UGC constants reference.
- `raw/aoe2de/aoe2de-xs-function-signatures.txt`: highest-signal raw signature
  source.
- `raw/aoe2de/aoe2de-xs-function-names.txt`: fallback name inventory.
- `raw/aoe2de/aoe2de-xs-strings.txt`: supplemental signature and file-I/O
  evidence.

## Resolution Workflow

Resolve an XS function first:

```powershell
$env:PYTHONPATH='src'
python -m aoe2_ai_lab resolve-reference xsChatData --kind xs-function-inventory
python -m aoe2_ai_lab resolve-reference xsCreateFile --kind xs-function-inventory
python -m aoe2_ai_lab resolve-reference cDarkAge --kind xs-constant-inventory
python -m aoe2_ai_lab search-registry cOriginVector --kind xs-constant-inventory
```

Use the returned fields:

- `signature`
- `return_type`
- `parameters`
- `category`
- `ai_context_status`
- `notes`

For constants, use:

- `category`
- `value_type`
- `value`

## AI Context Rules

- General XS documentation is broader than AI `xs-script-call` support.
- Treat most XS functions as `unvalidated-in-ai-context` until locally tested.
- `xsChatData` is currently the safest known live-debug function for AI XS.
- File I/O functions such as `xsCreateFile`, `xsOpenFile`, `xsWrite*`,
  `xsRead*`, and `xsCloseFile` are context-sensitive in AI. Project notes say
  to set XS context player before file operations and reset to `-1` after.
- The project linter blocks `xsGetUnitTargetId` because the DE AI parser
  rejected it. Prefer exact names from the local extracted signatures, such as
  `xsGetUnitTargetUnitId`.

## Categories Used In The Inventory

- `ai-state`
- `rules`
- `vector`
- `arrays`
- `context`
- `runtime`
- `scenario-trigger`
- `file-io`
- `debug`
- `game-state`
- `tech-effects`
- `unit-object`
- `tasks`
- `diplomacy`
- `bitcast`
- `misc`

XS constant categories are imported directly from the UGC constants guide, for
example:

- `Age`
- `Language Constants`
- `Victory Conditions`
- `Classes`
- `Object Attributes`
- `Terrain Restrictions`
- `Map Types`

## Source Hierarchy

Use this evidence ladder:

1. local XS inventory entry exists
2. extracted signature/name/strings confirm the symbol
3. project docs describe AI-context constraints
4. linter accepts the `.xs` file
5. in-game probe confirms AI-context behavior

Only step 5 should upgrade a function from unvalidated to observed behavior in
project notes.
