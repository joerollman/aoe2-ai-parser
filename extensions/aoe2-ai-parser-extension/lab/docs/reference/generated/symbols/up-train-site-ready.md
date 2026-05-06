# `up-train-site-ready`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-train-site-ready"></a>

## `up-train-site-ready`

- Kind: `command`
- Detail: Fact - Buildings, Can Do

Syntax: `(up-train-site-ready <typeOp> <UnitId>)`

Check if a unit's training site is ready and available. You can also check the train site of my-unique-unit, which will automatically check the train site of the UnitId of the unique unit that the AI's civ can train from the castle. Important Note: Unit lines, negative unit IDs, or invalid unit Ids may result in a crash. Do not use unit lines or unit classes with this command. Please use the root unit type instead, such as using archer instead of archer-line, even if Crossbowman has been researched. In most cases, the unit you use to test whether a train site is ready doesn't matter. However, for docks, the unit you choose to test is important. Trade cogs may be rejected by the dock if you use snDockTrainingFilter and it hasn't found an allied dock. On the other hand, a military ship (galley works to test all of these) uses enemy ships/docks to determine if it is acceptable when that sn is in use. Fishing ships may also provide a different result sooner or later. An alternative to this command is finding a building you want to check, setting it as the target object with up-set-target-object or up-set-target-by-id and using up-get-object-data like this:(up-get-object-data object-data-progress-type gl-data) If 0 is stored in gl-data, then the building is not training or researching, and it is ready to train units.

[AIRef](https://airef.github.io/commands/commands-details.html#up-train-site-ready)

Completion insert text:

```text
(up-train-site-ready ${1:typeOp} ${2:UnitId})
```

