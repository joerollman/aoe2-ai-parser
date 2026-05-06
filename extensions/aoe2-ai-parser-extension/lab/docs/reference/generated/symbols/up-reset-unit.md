# `up-reset-unit`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-reset-unit"></a>

## `up-reset-unit`

- Kind: `command`
- Detail: Action - Units

Syntax: `(up-reset-unit <typeOp> <UnitId>)`

Halt the activity of all units of a specific type. This is equivalent to clicking the &quot;stop&quot; button. my-unique-unit, my-elite-unique-unit, and my-unique-unit-line can be used for the UnitId, which will automatically get the UnitId of the unique unit, elite unique unit, or unique unit line that the AI's civ can train from the castle.

[AIRef](https://airef.github.io/commands/commands-details.html#up-reset-unit)

Completion insert text:

```text
(up-reset-unit ${1:typeOp} ${2:UnitId})
```

