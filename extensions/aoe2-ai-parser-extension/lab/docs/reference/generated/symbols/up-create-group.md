# `up-create-group`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-create-group"></a>

## `up-create-group`

- Kind: `command`
- Detail: Action - DUC, DUC Groups

Syntax: `(up-create-group <GoalId> <GoalId> <typeOp> <GroupId>)`

Reset the group and create a search group from the local search results. The number of units put into the group will be capped by the number stored in CountGoalId. If 0 is used for the CountGoalId parameter, up to 40 objects will be put into the group instead (the highest amount). If there are no units available in the results list to create the specified group, the group will be cleared in the same way as up-reset-group.

[AIRef](https://airef.github.io/commands/commands-details.html#up-create-group)

Completion insert text:

```text
(up-create-group ${1:GoalId} ${2:GoalId} ${3:typeOp} ${4:GroupId})
```

