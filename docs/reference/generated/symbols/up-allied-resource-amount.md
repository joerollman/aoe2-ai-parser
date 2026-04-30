# `up-allied-resource-amount`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-allied-resource-amount"></a>

## `up-allied-resource-amount`

- Kind: `command`
- Detail: Fact - Economy, Other Player Info

Syntax: `(up-allied-resource-amount <PlayerNumber> <ResourceType> <compareOp> <Value>)`

Perform a comparison with an ally's internal resource value. The command cannot be used to check the resources of players who are not allies.

[AIRef](https://airef.github.io/commands/commands-details.html#up-allied-resource-amount)

Completion insert text:

```text
(up-allied-resource-amount ${1:PlayerNumber} ${2:ResourceType} ${3:compareOp} ${4:Value})
```

