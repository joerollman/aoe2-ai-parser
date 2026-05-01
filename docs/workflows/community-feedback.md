# Community Feedback Workflow

This project expects most user feedback to arrive through Discord, not GitHub.
Users are not expected to create pull requests or understand the repository
layout. Treat Discord reports as the front door, and use this repository as the
source of truth for project-specific triage rules, parser commands, extension
behavior, and response guidance.

## Bot Entry Points

A generic Discord bot can read this file first when operating in this project.
Use these local docs and commands instead of hardcoding project behavior in the
bot repo.

Machine-readable companion:

- `docs/workflows/community-feedback.json`: compact bot-facing manifest for
  entry docs, commands, categories, required report fields, and handoff fields.

Primary docs:

- `AGENTS.md`: repo scope, agent startup path, and verification commands.
- `docs/README.md`: documentation index.
- `docs/workflows/ai-package-validator.md`: package linting, JSON output,
  `issue_groups`, severity/confidence, suppressions, profiles, and integrity
  checks.
- `docs/workflows/validator-diagnostic-codes.md`: diagnostic-code
  explanations, severity, and suppression policy.
- `docs/workflows/cursor-extension.md`: VS Code/Cursor extension behavior,
  hover/reference navigation, command palette commands, themes, packaging, and
  local verification.
- `docs/reference/command-reference.md`: command behavior notes and
  project-observed semantics.
- `docs/reference/generated/symbols/`: fast per-symbol Markdown reference files.

Primary commands:

```powershell
$env:PYTHONPATH='src'
python -m aoe2_ai_lab lint <file>
python -m aoe2_ai_lab lint-package <folder-or-ai-file> --json
python -m aoe2_ai_lab lint-package <folder-or-ai-file> --profile corpus --json
python -m aoe2_ai_lab resolve-reference <token>
python -m aoe2_ai_lab search-registry <query>
```

Use `lint-package --json` for bot/agent triage. Start with top-level
`issue_groups`; inspect per-root findings only when the group summary is not
enough.

## Discord Channels

Recommended channels:

- `#parser-help`: usage questions, setup issues, and how-to requests.
- `#bug-reports`: extension crashes, failed commands, bad output, broken UI.
- `#false-positives`: valid AI code that the validator reports as a problem.
- `#feature-requests`: requested diagnostics, autocomplete, docs, UI, or
  workflow improvements.
- `#known-issues`: pinned maintainer summaries and workarounds.

The bot should prefer answering in-thread. If a report becomes actionable, it
should summarize the issue and ask for the missing repro data.

## Report Templates

General report:

```text
Extension version:
Editor: VS Code / Cursor:
OS:
What were you doing:
What happened:
What did you expect:
AOE2 AI Parser output:
Smallest .ai/.per files or snippet that reproduces it:
Screenshot or screen recording if UI-related:
```

False-positive report:

```text
Diagnostic code:
Flagged line:
Why you believe this works in AoE2 DE:
Does the script run in-game:
Is this pattern used by an existing AI:
Smallest .ai/.per repro:
```

Performance report:

```text
Extension version:
Editor: VS Code / Cursor:
File size or package size:
Command or action that was slow:
Approximate delay:
Does hover/autocomplete block while linting:
AOE2 AI Parser output:
```

## Classification

Use these labels when summarizing Discord reports for maintainers:

- `bug: extension`: VS Code/Cursor command, hover, completion, theme, or UI bug.
- `bug: parser`: parser crash or incorrect structural parse.
- `false-positive`: valid script reported as an issue.
- `false-negative`: invalid or suspicious script not reported.
- `docs`: missing or confusing docs, hover text, symbol reference, or README.
- `autocomplete`: completion ranking, missing suggestions, or wrong suggestions.
- `hover/reference`: hover loading, docs links, go-to-definition, or preview.
- `theme`: syntax coloring, light/dark colors, or customization defaults.
- `performance`: slow lint, blocked hover, large-file behavior, package scans.
- `feature-request`: new diagnostic, command, workflow, or editor behavior.

Priority order:

1. Extension commands crash or throw runtime errors.
2. Hover/autocomplete hangs or is blocked during common workflows.
3. Lint package cannot run on normal AI packages.
4. Valid working scripts are flagged as hard errors.
5. Package reports or diagnostics are too slow to be useful.
6. Missing docs, low-risk false positives, and feature requests.

## Bot Response Rules

For help questions:

- Answer from local docs when possible.
- Link to the relevant generated symbol file for command-specific questions.
- If a command/fact/action behavior is uncertain, say it is unverified and ask
  for an in-game repro or community evidence.

For bug reports:

- Ask for the extension version and editor if missing.
- Ask for the `AOE2 AI Parser` output panel text if a command failed.
- Ask for the smallest repro package or snippet.
- Do not promise a fix until the issue is reproduced or the failure mode is
  clear.

For false positives:

- Request the diagnostic code and flagged line.
- Check `docs/workflows/validator-diagnostic-codes.md`.
- Run `lint-package --json` on the repro when available.
- If the pattern is known to work in AoE2 DE, classify as `false-positive` and
  recommend changing severity, profile behavior, or the validator rule.
- If compatibility is unclear, classify as `needs evidence` and ask for in-game
  confirmation or examples from working AIs.

For extension issues:

- Check `docs/workflows/cursor-extension.md`.
- Confirm whether the user has reloaded the editor after installing an update.
- Ask whether the issue occurs in VS Code, Cursor, or both.
- For hover/reference issues, ask for the exact symbol under the cursor.
- For lint command issues, ask which command was run: current file, package,
  folder, or package report.

## Maintainer Handoff Format

When handing a Discord thread to a coding agent, use:

```text
Source:
Reporter environment:
Category:
Priority:
User-visible symptom:
Expected behavior:
Repro files or snippet:
Command/output:
Likely docs to read:
Recommended next step:
Draft user response:
```

If attached files are needed, place them outside the public repo unless they are
small fixtures that can be committed intentionally. Good temporary locations are
`.tmp/community-repros/<short-name>/` or another local folder that is not part
of the extension package.

## What Not To Do

- Do not ask community users to submit pull requests.
- Do not commit private AI packages, large downloaded corpora, game logs, or
  Discord exports to this public repo.
- Do not add bot tokens, Discord server IDs, deployment config, or moderation
  secrets to this repo.
- Do not promote uncertain AI scripting claims to validator rules without local
  docs, in-game evidence, or repeated community confirmation.
- Do not suppress a diagnostic globally just because one imported AI triggers
  it; first decide whether the rule should be downgraded, profile-specific, or
  documented as compatibility noise.

## Internal Tracking

Discord remains the user-facing feedback channel. GitHub Issues are optional
and should be maintainer-created only when a report needs longer-term tracking.
If an issue is created, summarize the Discord report rather than asking the
user to move platforms.

Useful internal issue title format:

```text
[extension] Hover blocks while package lint runs
[parser] False positive: command-role-mismatch for up-set-target-object
[docs] Explain theme color customization defaults
```
