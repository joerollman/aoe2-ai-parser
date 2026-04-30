# Generator Usage

The `generate` CLI writes reusable `.per` blocks from stable templates. Generated
blocks are wrapped in markers so the same command can be rerun safely.

Important workflow rule: do not run multiple insertion commands against the same
file in parallel. Each insertion reads, edits, and writes the whole file.

Before copying generated output into the game AI folder, run the linter. This is
required because DE will reject missing identifiers at load time:

```powershell
python -m aoe2_ai_lab lint extensions\aoe2-aiscript-cursor-local-lab\samples\lab_diagnostics_sample.per
```

## Markers

Sections define insertion targets:

```lisp
; <aoe2-ai-lab:section state>
; </aoe2-ai-lab:section state>
```

Blocks define idempotent generated regions:

```lisp
; <aoe2-ai-lab:block opening.initial>
(defrule
    (true)
=>
    (set-goal goal-opening opening-dark-age-eco)
    (disable-self)
)
; </aoe2-ai-lab:block opening.initial>
```

If a block ID already exists, the generator replaces that block. If the section
does not exist, the generator appends a new section to the file.

## Strategic Number Defaults

Print to stdout:

```powershell
python -m aoe2_ai_lab generate sn-defaults
```

Insert into a file:

```powershell
python -m aoe2_ai_lab generate sn-defaults `
  --insert ai\betterbot\betterbot.per `
  --section init
```

## Goal Batch

Use this for one-shot state setup.

```powershell
python -m aoe2_ai_lab generate goal-batch `
  --id opening.initial `
  --set goal-opening=opening-dark-age-eco `
  --insert ai\betterbot\betterbot.per `
  --section state
```

Add repeated facts with `--fact`:

```powershell
python -m aoe2_ai_lab generate goal-batch `
  --id strategy.default `
  --fact "(true)" `
  --set goal-strategy=strategy-default `
  --set goal-unit-line=archer-line
```

By default, goal batches add `(disable-self)`. Use `--keep-enabled` only for a
rule that should keep firing.

## State Transition

Use this for guarded transitions from one goal value to another.

```powershell
python -m aoe2_ai_lab generate state-transition `
  --id opening.feudal-archers `
  --goal goal-opening `
  --from opening-dark-age-eco `
  --to opening-feudal-archers `
  --fact "(current-age == feudal-age)" `
  --insert ai\betterbot\betterbot.per `
  --section state
```

This emits:

```lisp
(defrule
    (current-age == feudal-age)
    (goal goal-opening opening-dark-age-eco)
=>
    (set-goal goal-opening opening-feudal-archers)
    (disable-self)
)
```

## Next Templates

Likely next generators:

- `research`: guarded `(research tech)` rule
- `production`: guarded `(train unit)` rule
- `build`: guarded `(build building)` or `up-build`
- `jump-guard`: `up-compare-goal` plus `up-jump-rule`
