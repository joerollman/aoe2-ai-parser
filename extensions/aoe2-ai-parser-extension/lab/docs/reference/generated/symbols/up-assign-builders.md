# `up-assign-builders`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-assign-builders"></a>

## `up-assign-builders`

- Kind: `command`
- Detail: Action - Buildings, Economy

Syntax: `(up-assign-builders <typeOp> <BuildingId> <typeOp> <Value>)`

Assign a specific number of builders to a building type or class. This assignment lasts for all future buildings of the specified building type or class until a new up-assign-builders command is issued. If the current number of builders for the building type or class is less than the amount of villagers specified by up-assign-builders, the additional builders are immediately sent to help construct the building. If you want a certain number of assign builders to only last for the construction of one building, you must set up-assign-builders again after the building is constructed. Additionally, if you want to stop sending any builders to construct a building type or class, you must set up-assign-builders to -1, not 0. When using any build command besides up-build-line, the game will automatically assign one builder to construct the building, regardless of what you have up-assign-builders set to. However, if the original builder is killed or restasked and up-assign-builders is set to -1 for the building, the AI will not send a replacement builder to finish the building. Assigning the number of builders by class is best for walls and gates. By default, like AoC, wonders have 250 (max) builders, and the wall class has 2.

[AIRef](https://airef.github.io/commands/commands-details.html#up-assign-builders)

Completion insert text:

```text
(up-assign-builders ${1:typeOp} ${2:BuildingId} ${3:typeOp} ${4:Value})
```

