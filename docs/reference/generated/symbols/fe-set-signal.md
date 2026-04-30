# `fe-set-signal`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-fe-set-signal"></a>

## `fe-set-signal`

- Kind: `command`
- Detail: Action - Scenarios

Syntax: `(fe-set-signal <typeOp> <SignalId> <typeOp> <Value>)`

DE only. Set the value of a multiplayer scenario trigger signal. This action only works with a "Multiplayer AI Signal" trigger condition in a single and multiplayer scenario. For the "AI Signal" condition use up-set-signal (only works in a single player scenario).

[AIRef](https://airef.github.io/commands/commands-details.html#fe-set-signal)

Completion insert text:

```text
(fe-set-signal ${1:typeOp} ${2:SignalId} ${3:typeOp} ${4:Value})
```

