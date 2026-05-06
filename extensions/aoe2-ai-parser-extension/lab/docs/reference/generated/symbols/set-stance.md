# `set-stance`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-set-stance"></a>

## `set-stance`

- Kind: `command`
- Detail: Action - Diplomacy

Syntax: `(set-stance <PlayerNumber> <PlayerStance>)`

Sets the diplomatic stance toward a given player to the specified stance, either ally, neutral, or enemy. To check our stance toward a given player, use stance-toward. To check the stance another player has toward us, use players-stance. The action allows "focus-player", "target-player", and "any"/"every" wildcard parameters for pPlayerNumber. It also allows the use of rule variables for Player, such as "this-any-ally" or "this-any-enemy". It also allows for scenario-player-# and lobby-player-#, where # is between 1 and 8. scenario-player-# refers to the player color (where red = scenario-player-2), and lobby-player-# refers to the player slot (where the lobby host or human player playing a single player campaign is always lobby-player-1).

[AIRef](https://airef.github.io/commands/commands-details.html#set-stance)

Completion insert text:

```text
(set-stance ${1:PlayerNumber} ${2:PlayerStance})
```

