# `up-modify-sn`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-modify-sn"></a>

## `up-modify-sn`

- Kind: `command`
- Detail: Fact/Action - SNs

Syntax: `(up-modify-sn <SnId> <mathOp> <Value>)`

Perform math operations on a strategic number. In DE, this command can be used as either a fact or an action, but it can only be used as an action in UP and WK. When used as a fact, it will modify the strategic number just like it would if it was used in the actions section of the rule. The only difference when up-modify-sn is used as a fact is that if it to modify the strategic number (because of an invalid strategic number ID or an invalid value), then the rest of the rule won't execute.

[AIRef](https://airef.github.io/commands/commands-details.html#up-modify-sn)

Completion insert text:

```text
(up-modify-sn ${1:SnId} ${2:mathOp} ${3:Value})
```

