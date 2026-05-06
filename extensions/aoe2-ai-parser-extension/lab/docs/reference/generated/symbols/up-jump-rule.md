# `up-jump-rule`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-jump-rule"></a>

## `up-jump-rule`

- Kind: `command`
- Detail: Action - Rule Jumps

Syntax: `(up-jump-rule <RuleDelta>)`

Jump forward or backward within the current rule set. Never use this command where #load-if-defined or #load-if-not-defined blocks may make your jump target unreliable. Please ensure that the rule you are jumping to actually exists. With this action, you can either decrease rules per pass with intelligent skips, or greatly increase it with loops. Please consider game performance.

[AIRef](https://airef.github.io/commands/commands-details.html#up-jump-rule)

Completion insert text:

```text
(up-jump-rule ${1:RuleDelta})
```

