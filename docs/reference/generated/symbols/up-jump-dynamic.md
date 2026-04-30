# `up-jump-dynamic`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-jump-dynamic"></a>

## `up-jump-dynamic`

- Kind: `command`
- Detail: Action - Rule Jumps

Syntax: `(up-jump-dynamic <typeOp> <RuleDelta>)`

Jump dynamically within the current rule set. Never use this command where #load-if-defined or #load-if-not-defined blocks may make your jump target unreliable. Please ensure that the rule you are jumping to actually exists. With this action, you can either decrease rules per pass with intelligent skips, or greatly increase it with loops. Please consider game performance.

[AIRef](https://airef.github.io/commands/commands-details.html#up-jump-dynamic)

Completion insert text:

```text
(up-jump-dynamic ${1:typeOp} ${2:RuleDelta})
```

