# `up-retreat-to`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-retreat-to"></a>

## `up-retreat-to`

- Kind: `command`
- Detail: Action - Attack

Syntax: `(up-retreat-to <ObjectId> <typeOp> <UnitId>)`

Retreat all units of a specific type to a random instance of another. Military units within 6 range of the retreat target object (the object in the first parameter) will not be told to retreat, to allow better defense of the retreat object, such as an offensive trebuchet or a castle. Active explorers will not retreat. If explorers need to retreat, use up-reset-scouts before using this command. my-unique-unit, my-elite-unique-unit, and my-unique-unit-line can be used for the UnitId, which will automatically get the UnitId of the unique unit, elite unique unit, or unique unit line that the AI's civ can train from the castle.

[AIRef](https://airef.github.io/commands/commands-details.html#up-retreat-to)

Completion insert text:

```text
(up-retreat-to ${1:ObjectId} ${2:typeOp} ${3:UnitId})
```

