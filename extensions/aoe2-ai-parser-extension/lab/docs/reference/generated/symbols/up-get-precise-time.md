# `up-get-precise-time`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-get-precise-time"></a>

## `up-get-precise-time`

- Kind: `command`
- Detail: Action - Game Info

Syntax: `(up-get-precise-time <OptionGoalId> <OutputGoalId>)`

Get a system timestamp or the elapsed time into a goal. The OptionGoalId parameter determines whether a system timestamp is retrieved or the elapsed time since a previous system timestamp is retrieved. To get a system timestamp, use 0 for the OptionGoalId parameter. To get the elapsed time since a timestamp, use a pGoalId that is currently storing a system timestamp for the OptionGoalId parameter. The system timestamp or elapsed time will be stored in the OutputGoal.

[AIRef](https://airef.github.io/commands/commands-details.html#up-get-precise-time)

Completion insert text:

```text
(up-get-precise-time ${1:OptionGoalId} ${2:OutputGoalId})
```

