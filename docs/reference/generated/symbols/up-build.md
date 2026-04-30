# `up-build`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-build"></a>

## `up-build`

- Kind: `command`
- Detail: Action - Buildings

Syntax: `(up-build <PlacementType> <EscrowGoalId> <typeOp> <BuildingId>)`

Add a building to the construction queue with dynamic values. The AI will avoid placing the building in the following locations according to the placement type: System 1 (used by place-normal, place-control, and place-point):Ally (and self): will avoid placing the building on tiles where an allied building already exists.Enemy: will avoid placing the building on tiles where an enemy building already exists. Will also avoid placing a building within the attack range of a tower, TC, or castle, + 0.5 tiles.System 2 (used by place-forward):Ally (and self): will avoid placing the building on tiles where an allied building already exists.Enemy: will avoid placing the building on tiles where an enemy building already exists. Will also avoid placing a building within any enemy building's line of sight, + 2 tiles.

[AIRef](https://airef.github.io/commands/commands-details.html#up-build)

Completion insert text:

```text
(up-build ${1:PlacementType} ${2:EscrowGoalId} ${3:typeOp} ${4:BuildingId})
```

