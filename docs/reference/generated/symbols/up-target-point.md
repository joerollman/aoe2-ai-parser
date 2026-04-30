# `up-target-point`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-target-point"></a>

## `up-target-point`

- Kind: `command`
- Detail: Action - DUC, Points

Syntax: `(up-target-point <Point> <DUCAction> <Formation> <AttackStance>)`

Direct local search results to a specific point on the map. This command can perform all actions from the DUCAction list. However, action-default, action-guard, action-follow, and action-garrison will perform as action-move. If you wish to action-move back into formation nearby after attacking, please action-move to the point (-1,-1) first to reset distance. This command will aim to separate the units selected with up-find-local into groups of 20 units or less before sending them against the remote target(s). Do not use the action-default or action-move commands if the defensive targeting system (TSA) is locked on a target, or units will become "confused" and not respond for a few moments. Either bring the town size so that enemy-buildings-in-town is no longer true or set snDisableDefendGroups on. The action-patrol command seems to work regardless.

[AIRef](https://airef.github.io/commands/commands-details.html#up-target-point)

Completion insert text:

```text
(up-target-point ${1:Point} ${2:DUCAction} ${3:Formation} ${4:AttackStance})
```

