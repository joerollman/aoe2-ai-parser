# `up-get-fact-max`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-get-fact-max"></a>

## `up-get-fact-max`

- Kind: `command`
- Detail: Fact/Action - Other Player Info, Player Facts

Syntax: `(up-get-fact-max <PlayerNumber> <FactId> <FactParameter> <OutputGoalId>)`

Read the maximum value of the facts for specific players into a goal. This command can be used as either a fact or an action. The matching player will be set to the this-any-* rule variable for use in the action section of the rule, even if up-get-fact-max is used as an action. The Action allows only the "any" wildcard parameters for pPlayerNumber, such as any-ally or any-enemy. It also allows for scenario-player-# and lobby-player-#, where # is between 1 and 8. scenario-player-# refers to the player color (where red = scenario-player-2), and lobby-player-# refers to the player slot (where the lobby host or human player playing a single player campaign is always lobby-player-1).

[AIRef](https://airef.github.io/commands/commands-details.html#up-get-fact-max)

Completion insert text:

```text
(up-get-fact-max ${1:PlayerNumber} ${2:FactId} ${3:FactParameter} ${4:OutputGoalId})
```

