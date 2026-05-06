# `up-find-player-flare`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-find-player-flare"></a>

## `up-find-player-flare`

- Kind: `command`
- Detail: Action - Other Player Info, Points

Syntax: `(up-find-player-flare <PlayerNumber> <Point>)`

Read the (x,y) position of any visible flare into an extended goal pair. This command writes to 2 consecutive goals and requires an extended goal pair between 41 and 15998. If it fails to get a valid position, it will return (-1,-1). Please note that it has never been designed to work with this-any-* or every-* wildcards, as flares belong to all recipient players, even when they aren't owned by them, so the stored player from this-* would not necessarily be the actual sender of the flare. If you search for players-unit-type-count any-* flare, do not expect this-* to be the sender player for any action commands (not limited to just the flare stuff). If you need to know the specific player number of the sender, you'll need to loop with focus-player checks. The action allows "my-player-number", "focus-player", "target-player", and "any"/"every" wildcard parameters for pPlayerNumber. It also allows for scenario-player-# and lobby-player-#, where # is between 1 and 8. scenario-player-# refers to the player color (where red = scenario-player-2), and lobby-player-# refers to the player slot (where the lobby host or human player playing a single player campaign is always lobby-player-1).

[AIRef](https://airef.github.io/commands/commands-details.html#up-find-player-flare)

Completion insert text:

```text
(up-find-player-flare ${1:PlayerNumber} ${2:Point})
```

