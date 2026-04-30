# `up-garrison`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-garrison"></a>

## `up-garrison`

- Kind: `command`
- Detail: Action - Buildings

Syntax: `(up-garrison <ObjectId> <typeOp> <UnitId>)`

Garrison all units of the specified type into another object. The first parameter cannot be a class or a unit-line. my-unique-unit and my-elite-unique-unit can be used though, which will automatically get the UnitId of the unique unit or elite unique unit that the AI's civ can train from the castle. It must be a valid root object type id that can accept a garrison (battering-ram instead of battering-ram-line). DE requires "feudal-battering-ram" (ID 1258) instead of battering-ram. Objects tasked to garrison are prioritized in the order from newest to oldest trained/built.

[AIRef](https://airef.github.io/commands/commands-details.html#up-garrison)

Completion insert text:

```text
(up-garrison ${1:ObjectId} ${2:typeOp} ${3:UnitId})
```

