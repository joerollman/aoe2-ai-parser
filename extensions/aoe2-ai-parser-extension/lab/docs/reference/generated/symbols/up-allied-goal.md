# `up-allied-goal`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-allied-goal"></a>

## `up-allied-goal`

- Kind: `command`
- Detail: Fact - Goals, Other Player Info

Syntax: `(up-allied-goal <PlayerNumber> <GoalId> <compareOp> <Value>)`

Perform a comparison with an allied AI's goal variable. The command cannot be used to check human players or computer players who are not allies.

[AIRef](https://airef.github.io/commands/commands-details.html#up-allied-goal)

Completion insert text:

```text
(up-allied-goal ${1:PlayerNumber} ${2:GoalId} ${3:compareOp} ${4:Value})
```

