# `unit-available`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-unit-available"></a>

## `unit-available`

- Kind: `command`
- Detail: Fact - Can Do, Units

Syntax: `(unit-available <UnitId>)`

Checks that the unit is available to the computer player's civ, and that the tech tree prerequisites for training the unit are met. The fact does not check whether the unit training can start, meaning this command does not check resource availability, housing headroom, or whether the building needed for training is currently used for research/training of another unit. The fact allows the use of unit line wildcard parameters for pUnitId. my-unique-unit, my-elite-unique-unit, and my-unique-unit-line can also be used, which will automatically get the UnitId of the unique unit, elite unique unit, or unique unit line that the AI's civ can train from the castle. When the AI checks the tech tree prerequisites, this includes checking whether the prerequisite age has been researched. There isn't a way at the beginning of the game to check if the unit will be available for the civilization in future ages.

[AIRef](https://airef.github.io/commands/commands-details.html#unit-available)

Completion insert text:

```text
(unit-available ${1:UnitId})
```

