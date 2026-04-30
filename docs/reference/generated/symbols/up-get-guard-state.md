# `up-get-guard-state`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-get-guard-state"></a>

## `up-get-guard-state`

- Kind: `command`
- Detail: Action - Game Info

Syntax: `(up-get-guard-state <OutputGoalId>)`

Get the guard state into 4 consecutive extended goals. The guard state is defined in custom random maps using the guard_state command, which enables a resource trickle and/or a defeat condition depending on whether a certain unit type is killed. The goals will be filled with data in the following order: TypeId, ResourceType, ResourceDelta, GuardFlags. Please use up-compare-flag to check the guard flags (see pGuardFlag for a list of guard flags). If guard-flag-resource is set in GuardFlags, then ResourceDelta/100 will slowly be added to ResourceType as long as TypeId objects remain. If both guard-flag-resource and guard-flag-inverse are set, then the resources will be added only when there are no TypeId objects left. If the guard-flag-victory condition is set, the AI will be defeated if no TypeId objects remain.

[AIRef](https://airef.github.io/commands/commands-details.html#up-get-guard-state)

Completion insert text:

```text
(up-get-guard-state ${1:OutputGoalId})
```

