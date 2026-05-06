# `up-add-object-cost`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-add-object-cost"></a>

## `up-add-object-cost`

- Kind: `command`
- Detail: Action - Cost Data

Syntax: `(up-add-object-cost <typeOp> <ObjectId> <typeOp> <Value>)`

Add or subtract objects of a specific type to the current cost data. Note the special exception for town centers below. Gates likely also need to use foundation IDs instead. It's recommended to use the base unit or building, rather than a unit or building line. This command does not work with unit or building lines if the unit or building is not yet available to the civ because of incomplete techs or not being in the prerequisite age for the object. For example, "mangonel-line" only works once the AI is in the castle or imperial age, but "mangonel" works from the start of the game.

[AIRef](https://airef.github.io/commands/commands-details.html#up-add-object-cost)

Completion insert text:

```text
(up-add-object-cost ${1:typeOp} ${2:ObjectId} ${3:typeOp} ${4:Value})
```

