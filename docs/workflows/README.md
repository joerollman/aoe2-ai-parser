# Workflow Docs

Use this folder for local tooling and handoff workflows.

- [generator-usage.md](./generator-usage.md): generated `.per` helper patterns.
- [ai-package-validator.md](./ai-package-validator.md): package linting,
  machine-readable JSON output, severity/confidence semantics, and package
  integrity checks.
- [validator-diagnostic-codes.md](./validator-diagnostic-codes.md): registry of
  validator issue codes, default severity, profile suppression, and editor
  actions.
- [cursor-extension.md](./cursor-extension.md): local VS Code/Cursor extension
  diagnostics, commands, registry completions, packaging, and verification.
- [community-feedback.md](./community-feedback.md): Discord-first feedback
  triage, bot entry points, report templates, and maintainer handoff format.
- [community-feedback.json](./community-feedback.json): compact bot-facing
  manifest for generic Discord automation.
- [release-and-repo-split.md](./release-and-repo-split.md): public extension
  release flow, marketplace publishing, and bundled validator runtime.

Core commands:

```powershell
$env:PYTHONPATH='src'; python -m aoe2_ai_lab lint extensions\aoe2-ai-parser-extension\samples\lab_diagnostics_sample.per
$env:PYTHONPATH='src'; python -m aoe2_ai_lab lint-package extensions\aoe2-ai-parser-extension\samples --profile default --json
$env:PYTHONPATH='src'; python -m pytest tests -p no:cacheprovider
```

For package triage, `lint-package --json` is the agent-facing interface. Start
with top-level `issue_groups`; they combine lint findings and package-integrity
issues into category summaries before you inspect per-root findings.

For community feedback triage, read `community-feedback.md` first. The Discord
bot should stay generic and use this repo's docs to learn project-specific
commands, categories, and response rules.
