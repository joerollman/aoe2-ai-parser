# Agent Session Startup

Use this file at the start of a new session. It is the shortest path to the
project's current working context.

## Read First

1. [AGENTS.md](../AGENTS.md)
2. [docs/README.md](./README.md)
3. [offline-reference-map.md](./extracted/offline-reference-map.md)

Then read the task surface that matches the request:

- command semantics: [reference/command-reference.md](./reference/command-reference.md)
- tooling workflow: [workflows/README.md](./workflows/README.md)
- package validation: [workflows/ai-package-validator.md](./workflows/ai-package-validator.md)
- diagnostic code meanings: [workflows/validator-diagnostic-codes.md](./workflows/validator-diagnostic-codes.md)

## Resolve Before Guessing

Before guessing syntax or semantics, resolve the token locally:

```powershell
$env:PYTHONPATH='src'
python -m aoe2_ai_lab resolve-reference <token>
```

Common examples:

```powershell
python -m aoe2_ai_lab resolve-reference up-target-point
python -m aoe2_ai_lab resolve-reference BuildingId
python -m aoe2_ai_lab resolve-reference sn-target-point-adjustment
python -m aoe2_ai_lab resolve-reference xsChatData --kind xs-function-inventory
python -m aoe2_ai_lab resolve-reference cDarkAge --kind xs-constant-inventory
python -m aoe2_ai_lab resolve-reference villager-class --kind value-entry
```

Use `search-registry` only when the exact token is unknown.

## Local Reference Priority

Use local sources in this order:

1. `validated-command`
2. `command-inventory`
3. `parameter-inventory`
4. `strategic-number-inventory`
5. `value-entry`
6. `object-inventory` / `tech-inventory`
7. `xs-function-inventory`
8. `xs-constant-inventory`
9. `rms-topic-inventory`
10. `project-command-note`
11. `binary-token` / `binary-family`, only as explicit evidence or resolver
    fallback when structured references have no answer

## Current Reality

- This public repository is tooling-only. Do not expect a bundled in-game AI
  package.
- The offline reference layer is strong enough that live AIRef should rarely be
  needed for normal scripting work.
- RMS is documented locally at the topic level, not as a full parsed grammar.
- RMS syntax and `.per` AI scripting syntax are separate; resolve through the
  correct local reference path before applying an example.
- XS is documented locally for both functions and constants, but AI-context
  behavior still needs explicit validation.
- Package validation is documented in
  [workflows/ai-package-validator.md](./workflows/ai-package-validator.md).
  Prefer `lint-package --json` for agent/CI consumption. Start package triage
  with top-level `issue_groups`, then drill into `integrity.root_manifest` or
  per-root `findings` only when a grouped issue needs line-level context.
- VS Code/Cursor extension behavior is documented in
  [workflows/cursor-extension.md](./workflows/cursor-extension.md). Its package
  lint command formats the same `issue_groups` that agents should use.
