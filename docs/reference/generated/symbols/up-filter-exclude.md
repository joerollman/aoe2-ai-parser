# `up-filter-exclude`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-filter-exclude"></a>

## `up-filter-exclude`

- Kind: `command`
- Detail: Action - DUC

Syntax: `(up-filter-exclude <CmdId> <ActionId> <OrderId> <ClassId>)`

Set exclude parameters for the direct targeting system. If any of these parameters is set to -1, then the associated condition will be ignored during search filtering.

[AIRef](https://airef.github.io/commands/commands-details.html#up-filter-exclude)

Completion insert text:

```text
(up-filter-exclude ${1:CmdId} ${2:ActionId} ${3:OrderId} ${4:ClassId})
```

