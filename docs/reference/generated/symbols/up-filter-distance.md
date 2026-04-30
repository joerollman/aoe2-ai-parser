# `up-filter-distance`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-filter-distance"></a>

## `up-filter-distance`

- Kind: `command`
- Detail: Action - DUC

Syntax: `(up-filter-distance <typeOp> <MinDistance> <typeOp> <MaxDistance>)`

Set distance parameters for the direct targeting system. If any of these parameters is set to -1, then the associated condition will be ignored during search filtering.

[AIRef](https://airef.github.io/commands/commands-details.html#up-filter-distance)

Completion insert text:

```text
(up-filter-distance ${1:typeOp} ${2:MinDistance} ${3:typeOp} ${4:MaxDistance})
```

