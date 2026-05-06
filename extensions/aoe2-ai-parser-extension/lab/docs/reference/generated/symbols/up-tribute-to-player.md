# `up-tribute-to-player`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-tribute-to-player"></a>

## `up-tribute-to-player`

- Kind: `command`
- Detail: Action - Diplomacy

Syntax: `(up-tribute-to-player <PlayerNumber> <ResourceType> <typeOp> <Value>)`

Tribute a variable amount of resources to other players. The fact allows "focus-player", "target-player", and "any"/"every" wildcard parameters for pPlayerNumber. It also allows the use of rule variables for PlayerNumber, such as "this-any-ally" or "this-any-enemy". It also allows for scenario-player-# and lobby-player-#, where # is between 1 and 8. scenario-player-# refers to the player color (where red = scenario-player-2), and lobby-player-# refers to the player slot (where the lobby host or human player playing a single player campaign is always lobby-player-1).

[AIRef](https://airef.github.io/commands/commands-details.html#up-tribute-to-player)

Completion insert text:

```text
(up-tribute-to-player ${1:PlayerNumber} ${2:ResourceType} ${3:typeOp} ${4:Value})
```

