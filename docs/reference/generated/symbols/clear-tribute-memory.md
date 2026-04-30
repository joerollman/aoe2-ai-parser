# `clear-tribute-memory`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-clear-tribute-memory"></a>

## `clear-tribute-memory`

- Kind: `command`
- Detail: Action - Diplomacy

Syntax: `(clear-tribute-memory <PlayerNumber> <Resource>)`

Clears the given player's tribute memory, the amount of a given resource received in tribute from the given player since the tribute memory was cleared. Only tribute memory for the given resource type is cleared. This command is used in conjunction with cPlayersTributeMemory, which allows you to check the amount of tribute received from the specified player since clear-tribute-memory was issued. The action allows "focus-player", "target-player", and "any"/"every" wildcard parameters for pPlayerNumber. It also allows the use of rule variables for pPlayerNumber, such as "this-any-ally" or "this-any-enemy". It also allows for scenario-player-# and lobby-player-#, where # is between 1 and 8. scenario-player-# refers to the player color (where red = scenario-player-2), and lobby-player-# refers to the player slot (where the lobby host or human player playing a single player campaign is always lobby-player-1).

[AIRef](https://airef.github.io/commands/commands-details.html#clear-tribute-memory)

Completion insert text:

```text
(clear-tribute-memory ${1:PlayerNumber} ${2:Resource})
```

