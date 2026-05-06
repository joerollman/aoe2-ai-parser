# `up-gather-inside`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-gather-inside"></a>

## `up-gather-inside`

- Kind: `command`
- Detail: Action - Buildings

Syntax: `(up-gather-inside <typeOp> <BuildingId> <typeOp> <Option>)`

Set all existing buildings of a specific type to hold units inside. If the Option parameter is set to 1, both trained and garrisoned units will be held inside the building. If set to -1, only garrisoned units will be held inside. Otherwise, if set to 0, all units will be released as usual.

[AIRef](https://airef.github.io/commands/commands-details.html#up-gather-inside)

Completion insert text:

```text
(up-gather-inside ${1:typeOp} ${2:BuildingId} ${3:typeOp} ${4:Option})
```

