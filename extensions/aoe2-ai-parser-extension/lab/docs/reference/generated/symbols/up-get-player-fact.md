# `up-get-player-fact`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-get-player-fact"></a>

## `up-get-player-fact`

- Kind: `command`
- Detail: Fact/Action - Other Player Info, Player Facts

Syntax: `(up-get-player-fact <PlayerNumber> <FactId> <FactParameter> <OutputGoalId>)`

Read a fact for a specific player into a goal. This command can be used as either a fact or an action. For better performance, please use one of the more direct commands from the up-get-fact series whenever possible. The action only allows for exact player numbers, "my-player-number", or "this-any" rule variables for pPlayerNumber, such as this-any-ally or this-any-enemy. It does not allow "any"/"every" wildcard parameters for pPlayerNumber. It also allows for scenario-player-# and lobby-player-#, where # is between 1 and 8. scenario-player-# refers to the player color (where red = scenario-player-2), and lobby-player-# refers to the player slot (where the lobby host or human player playing a single player campaign is always lobby-player-1).

[AIRef](https://airef.github.io/commands/commands-details.html#up-get-player-fact)

Completion insert text:

```text
(up-get-player-fact ${1:PlayerNumber} ${2:FactId} ${3:FactParameter} ${4:OutputGoalId})
```

