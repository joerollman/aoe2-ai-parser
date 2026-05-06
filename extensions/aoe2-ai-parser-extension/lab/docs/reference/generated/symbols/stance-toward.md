# `stance-toward`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-stance-toward"></a>

## `stance-toward`

- Kind: `command`
- Detail: Fact - Diplomacy, Own Player Info

Syntax: `(stance-toward <PlayerNumber> <PlayerStance>)`

Checks if the computer player's diplomatic stance toward a given player matches the given stance, either ally, neutral, or enemy. To check another player's diplomatic stance toward the computer player, use players-stance. The fact allows "focus-player", "target-player", and "any"/"every" wildcard parameters for pPlayerNumber. It also allows for scenario-player-# and lobby-player-#, where # is between 1 and 8. scenario-player-# refers to the player color (where red = scenario-player-2), and lobby-player-# refers to the player slot (where the lobby host or human player playing a single player campaign is always lobby-player-1).

[AIRef](https://airef.github.io/commands/commands-details.html#stance-toward)

Completion insert text:

```text
(stance-toward ${1:PlayerNumber} ${2:PlayerStance})
```

