# `up-jump-direct`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-jump-direct"></a>

## `up-jump-direct`

- Kind: `command`
- Detail: Action - Rule Jumps

Syntax: `(up-jump-direct <typeOp> <RuleId>)`

Jump directly within the current rule set. Please ensure that the rule you are jumping to actually exists. You can use up-get-rule-id to get a valid rule id to jump to. With this action, you can either decrease rules per pass with intelligent skips, or greatly increase it with loops. Please consider game performance.

[AIRef](https://airef.github.io/commands/commands-details.html#up-jump-direct)

Completion insert text:

```text
(up-jump-direct ${1:typeOp} ${2:RuleId})
```

