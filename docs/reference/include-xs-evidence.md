# Include And XS Evidence

Use this note when working on AI `include` directives and `xs-script-call`.

## Current Rules

- `include` is DE-only and loads `.xs` files from an AI script.
- The target must be quoted and must include the `.xs` extension.
- `include` directives belong between rules, not inside a `defrule`.
- Keep `load` and `load-random` directives before `include` directives.
- `xs-script-call` can call functions from included XS files, but only
  zero-parameter functions are callable from AI script.
- `xs-script-call` can be used as a fact or action. As a fact, the called
  function should return `true` or a non-zero integer if the rule is expected to
  pass.

## Local Validator Behavior

Package lint resolves `(include "...")` from reachable `.per` files. The local
resolution order is:

1. Relative to the current `.per` file directory.
2. Relative to the package root.

Resolved `.xs` files are linted with the AI-safe XS checks. Missing targets are
reported as `missing-include-target` errors. Repeated includes that resolve to
the same `.xs` file within one `.per` file are reported as
`duplicate-include-target` warnings.

Package lint also reports `load-after-include` when a reachable `.per` has a
`load` or `load-random` directive after the first `include`. Keep all loads
before includes.

When an included XS file is visible locally, package lint parses simple XS
function declarations and reports `xs-script-call-parameterized-function` when
AI script calls a function that has one or more parameters.

## Editor Behavior

The Cursor/VS Code extension supports go-to-definition for quoted
`(include "...")` targets. It opens the resolved `.xs` file using the same local
package-relative assumptions as completion and package lint.

## Useful Commands

```powershell
$env:PYTHONPATH='src'
python -m aoe2_ai_lab lint-package <package> --json
```

```powershell
$env:PYTHONPATH='src'
python -m aoe2_ai_lab lint <file.per>
```
