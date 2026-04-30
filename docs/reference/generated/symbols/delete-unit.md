# `delete-unit`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-delete-unit"></a>

## `delete-unit`

- Kind: `command`
- Detail: Action - Units

Syntax: `(delete-unit <UnitId>)`

Deletes exactly one unit of a given type. You cannot use unit classes with this command. my-unique-unit, my-elite-unique-unit, and my-unique-unit-line can also be used, which will automatically get the UnitId of the unique unit, elite unique unit, or unique unit line that the AI's civ can train from the castle. There are several other commands available to delete objects: delete-building: delete exactly one building of a given typeup-delete-distant-farms: delete farms that are beyond a specified distance from a dropsiteup-delete-idle-units: delete all idle units of the specified typeup-delete-objects: delete all objects of the given type that have less than the specified hitpointsup-target-objects or up-target-point: when used with the action-delete action, this command will delete all objects in the local search list

[AIRef](https://airef.github.io/commands/commands-details.html#delete-unit)

Completion insert text:

```text
(delete-unit ${1:UnitId})
```

