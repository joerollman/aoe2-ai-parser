# `up-train`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-train"></a>

## `up-train`

- Kind: `command`
- Detail: Action - Units

Syntax: `(up-train <EscrowGoalId> <typeOp> <UnitId>)`

Add a unit to the training queue with dynamic values. You can also train unique units by using my-unique-unit, my-elite-unique-unit, and my-unique-unit-line, which will automatically get the UnitId of the unique unit, elite unique unit, or unique unit line that the AI's civ can train from the castle. The setting of snDockTrainingFilter affects the ability for docks to train warships with this command.

[AIRef](https://airef.github.io/commands/commands-details.html#up-train)

Completion insert text:

```text
(up-train ${1:EscrowGoalId} ${2:typeOp} ${3:UnitId})
```

