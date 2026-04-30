# `up-target-objects`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-target-objects"></a>

## `up-target-objects`

- Kind: `command`
- Detail: Action - DUC

Syntax: `(up-target-objects <Option> <DUCAction> <Formation> <AttackStance>)`

Direct local search results against remote search results. The action-default command is equivalent to a right-click. This command can only perform the following actions: action-default, action-move, action-patrol, action-guard, action-follow, action-stop, action-ground, action-garrison, action-delete, action-gather, and action-none. The other pDUCAction options available for up-target-point will not work. Set the Option parameter to 1 to target only the object set by up-set-target-object. If set to 0, the objects in the local list will evenly target all objects in the remote list. This command will aim to separate the units selected with up-find-local into groups of 20 units or less before sending them against the remote target(s). Do not use the action-default or action-move commands if the defensive targeting system (TSA) is locked on a target, or units will become "confused" and not respond for a few moments. Either bring the town size so that enemy-buildings-in-town is no longer true or set snDisableDefendGroups on. The action-patrol command seems to work regardless.

[AIRef](https://airef.github.io/commands/commands-details.html#up-target-objects)

Completion insert text:

```text
(up-target-objects ${1:Option} ${2:DUCAction} ${3:Formation} ${4:AttackStance})
```

