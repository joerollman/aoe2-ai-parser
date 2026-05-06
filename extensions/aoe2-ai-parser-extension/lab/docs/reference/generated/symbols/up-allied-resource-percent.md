# `up-allied-resource-percent`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-allied-resource-percent"></a>

## `up-allied-resource-percent`

- Kind: `command`
- Detail: Fact - Economy, Other Player Info

Syntax: `(up-allied-resource-percent <PlayerNumber> <ResourceType> <compareOp> <Value>)`

Perform a comparison with an ally's internal resource value * 100. This command cannot be used with players who are not allies.

[AIRef](https://airef.github.io/commands/commands-details.html#up-allied-resource-percent)

Completion insert text:

```text
(up-allied-resource-percent ${1:PlayerNumber} ${2:ResourceType} ${3:compareOp} ${4:Value})
```

