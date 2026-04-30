# `up-filter-garrison`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-filter-garrison"></a>

## `up-filter-garrison`

- Kind: `command`
- Detail: Action - DUC

Syntax: `(up-filter-garrison <typeOp> <MinGarrison> <typeOp> <MaxGarrison>)`

Set garrison parameters for the direct targeting system. If any of these parameters is set to -1, then the associated condition will be ignored during search filtering.

[AIRef](https://airef.github.io/commands/commands-details.html#up-filter-garrison)

Completion insert text:

```text
(up-filter-garrison ${1:typeOp} ${2:MinGarrison} ${3:typeOp} ${4:MaxGarrison})
```

