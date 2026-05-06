# `up-get-upgrade-id`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-get-upgrade-id"></a>

## `up-get-upgrade-id`

- Kind: `command`
- Detail: Action - DUC, Game Info

Syntax: `(up-get-upgrade-id <PlayerNumber> <Option> <GoalId> <OutputGoalId>)`

Get the upgrade type id for an object into a goal. Set the Option parameter to 1 to get the current type id for counting, otherwise 0. The action only allows for exact player numbers, "my-player-number", or "this-any" rule variables for pPlayerNumber, such as this-any-ally or this-any-enemy. It does not allow "any"/"every" wildcard parameters for pPlayerNumber. It also allows for scenario-player-# and lobby-player-#, where # is between 1 and 8. scenario-player-# refers to the player color (where red = scenario-player-2), and lobby-player-# refers to the player slot (where the lobby host or human player playing a single player campaign is always lobby-player-1).

[AIRef](https://airef.github.io/commands/commands-details.html#up-get-upgrade-id)

Completion insert text:

```text
(up-get-upgrade-id ${1:PlayerNumber} ${2:Option} ${3:GoalId} ${4:OutputGoalId})
```

