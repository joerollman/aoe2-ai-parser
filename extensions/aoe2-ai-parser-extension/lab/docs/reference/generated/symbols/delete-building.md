# `delete-building`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-delete-building"></a>

## `delete-building`

- Kind: `command`
- Detail: Action - Buildings

Syntax: `(delete-building <BuildingId>)`

Deletes exactly one building of a given type. You cannot use building classes with this command. There are several other commands available to delete objects: delete-unit: delete exactly one unit of a given typeup-delete-distant-farms: delete farms that are beyond a specified distance from a dropsiteup-delete-idle-units: delete all idle units of the specified typeup-delete-objects: delete all objects of the specified type that have less than the specified hitpointsup-target-objects or up-target-point: when used with the action-delete action, this command will delete all objects in the local search list

[AIRef](https://airef.github.io/commands/commands-details.html#delete-building)

Completion insert text:

```text
(delete-building ${1:BuildingId})
```

