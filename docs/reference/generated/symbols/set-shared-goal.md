# `set-shared-goal`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-set-shared-goal"></a>

## `set-shared-goal`

- Kind: `command`
- Detail: Action - Goals, Other Player Info

Syntax: `(set-shared-goal <SharedGoalId> <Value>)`

Sets a given shared goal (a goal that is shared among all computer players) to a given value. To be used only when all computer players are on the same team. Shared goals are a separate set of 256 goals, in addition to the regular 16000 normal goals, which are shared between all AIs in the game, even between AIs that are enemies. Any AI can modify them at any time with set-shared-goal or up-set-shared-goal, and all AIs can check their values with shared-goal or up-get-shared-goal. Otherwise, shared goals share the same characteristics of normal goals, which you can read about in the set-goal description. Because shared goals can change without the AI's knowledge and the fact than enemy AIs can check their values, it's often better to use up-allied-goal, which allows you to check the value of one of an allied AI's normal 16000 goals.

[AIRef](https://airef.github.io/commands/commands-details.html#set-shared-goal)

Completion insert text:

```text
(set-shared-goal ${1:SharedGoalId} ${2:Value})
```

