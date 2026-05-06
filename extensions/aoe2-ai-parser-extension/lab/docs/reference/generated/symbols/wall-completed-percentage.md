# `wall-completed-percentage`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-wall-completed-percentage"></a>

## `wall-completed-percentage`

- Kind: `command`
- Detail: Fact - Buildings, Walls & Gates

Syntax: `(wall-completed-percentage <Perimeter> <compareOp> <Value>)`

Checks the completion percentage for a given wall perimeter. Trees and other destructible natural barriers are included and count as completed. The given perimeter must have been enabled with enable-wall-placement, and you should not check the completed percentage until the pass after the given wall perimeter has been enabled. Allowed perimeter values are 1 and 2, with 1 being closer to the Town Center than 2. Perimeter 1 is usually between 10 and 20 tiles from the starting Town Center. Perimeter 2 is usually between 18 and 30 tiles from the starting Town Center. Note: There are multiple cases where wall-completed-percentage equals 100 when you wouldn't expect:Maps with starting walls like Arena, Fortress, or Hideout.On island maps if there is an entirely water based barrier between the AI and any enemies.If a treaty is active.

[AIRef](https://airef.github.io/commands/commands-details.html#wall-completed-percentage)

Completion insert text:

```text
(wall-completed-percentage ${1:Perimeter} ${2:compareOp} ${3:Value})
```

