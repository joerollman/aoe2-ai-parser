# `up-filter-include`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-filter-include"></a>

## `up-filter-include`

- Kind: `command`
- Detail: Action - DUC

Syntax: `(up-filter-include <CmdId> <ActionId> <OrderId> <OnMainland>)`

Set include parameters for the direct targeting system. If any of these parameters is set to -1, then the associated condition will be ignored during search filtering.

[AIRef](https://airef.github.io/commands/commands-details.html#up-filter-include)

Completion insert text:

```text
(up-filter-include ${1:CmdId} ${2:ActionId} ${3:OrderId} ${4:OnMainland})
```

