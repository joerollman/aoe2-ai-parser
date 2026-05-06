# `up-guard-unit`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-guard-unit"></a>

## `up-guard-unit`

- Kind: `command`
- Detail: Action - Units

Syntax: `(up-guard-unit <ObjectId> <typeOp> <UnitId>)`

Set a single unit of a specific type to protect a random instance of another, as long as they are on the same continent. my-unique-unit, my-elite-unique-unit, and my-unique-unit-line can be used for the UnitId, which will automatically get the UnitId of the unique unit, elite unique unit, or unique unit line that the AI's civ can train from the castle.

[AIRef](https://airef.github.io/commands/commands-details.html#up-guard-unit)

Completion insert text:

```text
(up-guard-unit ${1:ObjectId} ${2:typeOp} ${3:UnitId})
```

