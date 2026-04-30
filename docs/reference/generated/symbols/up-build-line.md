# `up-build-line`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-build-line"></a>

## `up-build-line`

- Kind: `command`
- Detail: Action - Buildings, Walls & Gates

Syntax: `(up-build-line <Point> <Point> <typeOp> <BuildingId>)`

Place a line of buildings between two point goal pairs. For town centers and gates, please use a FoundationId, such as town-center-foundation or gate-ascending. Do not use town-center or gate with this command.

[AIRef](https://airef.github.io/commands/commands-details.html#up-build-line)

Completion insert text:

```text
(up-build-line ${1:Point} ${2:Point} ${3:typeOp} ${4:BuildingId})
```

