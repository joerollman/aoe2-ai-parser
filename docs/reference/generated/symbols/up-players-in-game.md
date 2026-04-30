# `up-players-in-game`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-players-in-game"></a>

## `up-players-in-game`

- Kind: `command`
- Detail: Fact - Diplomacy, Other Player Info

Syntax: `(up-players-in-game <PlayerStance> <compareOp> <Value>)`

Check the number of active players in the game of the specified stance. Players are considered allied with themselves, so "ally" will include the AI player itself.

[AIRef](https://airef.github.io/commands/commands-details.html#up-players-in-game)

Completion insert text:

```text
(up-players-in-game ${1:PlayerStance} ${2:compareOp} ${3:Value})
```

