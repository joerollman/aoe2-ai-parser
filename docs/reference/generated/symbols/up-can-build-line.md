# `up-can-build-line`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-can-build-line"></a>

## `up-can-build-line`

- Kind: `command`
- Detail: Fact - Buildings, Can Do, Walls & Gates

Syntax: `(up-can-build-line <EscrowGoalId> <Point> <typeOp> <BuildingId>)`

Check if a building can be constructed at a point goal pair. For town centers and gates, please use a FoundationId, such as town-center-foundation or gate-ascending. Do not use town-center or gate with this command.

[AIRef](https://airef.github.io/commands/commands-details.html#up-can-build-line)

Completion insert text:

```text
(up-can-build-line ${1:EscrowGoalId} ${2:Point} ${3:typeOp} ${4:BuildingId})
```

