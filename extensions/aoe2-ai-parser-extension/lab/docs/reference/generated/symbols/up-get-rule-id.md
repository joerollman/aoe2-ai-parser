# `up-get-rule-id`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-get-rule-id"></a>

## `up-get-rule-id`

- Kind: `command`
- Detail: Action - Rule Jumps

Syntax: `(up-get-rule-id <GoalId>)`

Get the zero-based id for the current rule within the rule set. This id can be used with up-jump-direct to precisely control jump destinations.

[AIRef](https://airef.github.io/commands/commands-details.html#up-get-rule-id)

Completion insert text:

```text
(up-get-rule-id ${1:GoalId})
```

