# `up-player-distance`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-player-distance"></a>

## `up-player-distance`

- Kind: `command`
- Detail: Fact - Other Player Info

Syntax: `(up-player-distance <PlayerNumber> <compareOp> <Value>)`

Check the distance in tiles to the nearest building of another player. The action allows "focus-player", "target-player", and "any"/"every" wildcard parameters for pPlayerNumber. It cannot be used with players who aren't allies. It also allows for scenario-player-# and lobby-player-#, where # is between 1 and 8. scenario-player-# refers to the player color (where red = scenario-player-2), and lobby-player-# refers to the player slot (where the lobby host or human player playing a single player campaign is always lobby-player-1).

[AIRef](https://airef.github.io/commands/commands-details.html#up-player-distance)

Completion insert text:

```text
(up-player-distance ${1:PlayerNumber} ${2:compareOp} ${3:Value})
```

