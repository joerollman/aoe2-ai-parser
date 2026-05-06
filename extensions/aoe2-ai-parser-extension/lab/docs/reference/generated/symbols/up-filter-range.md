# `up-filter-range`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-filter-range"></a>

## `up-filter-range`

- Kind: `command`
- Detail: Action - DUC

Syntax: `(up-filter-range <MinGarrison> <MaxGarrison> <MinDistance> <MaxDistance>)`

Set range parameters for the direct targeting system. If any of these parameters is set to -1, then the associated condition will be ignored during search filtering.

[AIRef](https://airef.github.io/commands/commands-details.html#up-filter-range)

Completion insert text:

```text
(up-filter-range ${1:MinGarrison} ${2:MaxGarrison} ${3:MinDistance} ${4:MaxDistance})
```

