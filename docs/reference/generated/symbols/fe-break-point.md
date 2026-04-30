# `fe-break-point`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-fe-break-point"></a>

## `fe-break-point`

- Kind: `command`
- Detail: Action - Debugging

Syntax: `(fe-break-point <Value> <compareOp> <Value> <OptionGoalId>)`

DE only. Add a break point to force the AI debugger interface to display if the break point conditions are met. The break point conditions are met if the comparison between the first and second values is true and either the last parameter is -1 or the goal specified in the last parameter is set to a value >= 1. The debugger shows you various information about the AI's current state, such as the current value of each goal and the object IDs stored in the local and remote lists. Once the debugger is opened, you'll be able to step through your rules. To enable the debugger you must first enable AI debugging for the game in the Steam launch options. Before launching the game, go to Steam => Right click game => Properties => in bottom box type AIDEBUGGING.

[AIRef](https://airef.github.io/commands/commands-details.html#fe-break-point)

Completion insert text:

```text
(fe-break-point ${1:Value} ${2:compareOp} ${3:Value} ${4:OptionGoalId})
```

