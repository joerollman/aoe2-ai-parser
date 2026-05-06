# `up-can-train`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-can-train"></a>

## `up-can-train`

- Kind: `command`
- Detail: Fact - Can Do, Units

Syntax: `(up-can-train <EscrowGoalId> <typeOp> <UnitId>)`

Check if a unit can be trained with dynamic values. my-unique-unit, my-elite-unique-unit, and my-unique-unit-line can also be used for the Unit ID to check, which will automatically get the UnitId of the unique unit, elite unique unit, or unique unit line that the AI's civ can train from the castle. This fact will return false if nhe setting of snDockTrainingFilter currently restricts the training of ships.

[AIRef](https://airef.github.io/commands/commands-details.html#up-can-train)

Completion insert text:

```text
(up-can-train ${1:EscrowGoalId} ${2:typeOp} ${3:UnitId})
```

