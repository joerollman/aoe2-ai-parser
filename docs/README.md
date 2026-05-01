# Documentation Index

Use this as the entry point for project notes.

## Start Here

- [agent-session-startup.md](./agent-session-startup.md): shortest startup path
  for new sessions.
- [../AGENTS.md](../AGENTS.md): repo-wide agent workflow and handoff rules.

## Shared References

- [reference/README.md](./reference/README.md): shared scripting references.
- [reference/command-reference.md](./reference/command-reference.md): command
  semantics and project-observed command notes.
- [reference/map-type-evidence.md](./reference/map-type-evidence.md): local
  evidence and validation status for AI `map-type` values.
- [reference/load-random-evidence.md](./reference/load-random-evidence.md):
  validation status for `load-random` weight forms and package reachability.
- [reference/include-xs-evidence.md](./reference/include-xs-evidence.md):
  local rules and validator/editor behavior for `include` and
  `xs-script-call`.
- [extracted/README.md](./extracted/README.md): offline imported inventories
  and raw evidence.
- [extracted/offline-reference-map.md](./extracted/offline-reference-map.md):
  token-to-inventory lookup map.

## Workflows

- [workflows/README.md](./workflows/README.md): local tooling workflows.
- [workflows/ai-package-validator.md](./workflows/ai-package-validator.md):
  package linting, JSON output, severity/confidence, and integrity checks.
- [workflows/validator-diagnostic-codes.md](./workflows/validator-diagnostic-codes.md):
  validator issue-code registry.
- [workflows/cursor-extension.md](./workflows/cursor-extension.md): VS
  Code/Cursor extension diagnostics, command palette linting, completions,
  hovers, quick fixes, packaging, and verification.
- [workflows/release-and-repo-split.md](./workflows/release-and-repo-split.md):
  marketplace publishing and bundled extension runtime.
- [workflows/generator-usage.md](./workflows/generator-usage.md): generation
  helpers.

## Reference Lookup

When resolving tokens during scripting work, prefer:

```powershell
$env:PYTHONPATH='src'
python -m aoe2_ai_lab resolve-reference <token>
```

When triaging AI packages, prefer:

```powershell
$env:PYTHONPATH='src'
python -m aoe2_ai_lab lint-package <package> --json
```

Read top-level `issue_groups` first. It is the compact agent-facing summary of
lint and package-integrity categories.
