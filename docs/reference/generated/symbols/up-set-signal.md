# `up-set-signal`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-set-signal"></a>

## `up-set-signal`

- Kind: `command`
- Detail: Action - Scenarios

Syntax: `(up-set-signal <typeOp> <SignalId> <typeOp> <Value>)`

Set the value of a scenario trigger signal. This action only works with a single player scenario and "AI Signal" trigger condition. For a multiplayer scenario, use "Multiplayer AI Signal" and fe-set-signal.

[AIRef](https://airef.github.io/commands/commands-details.html#up-set-signal)

Completion insert text:

```text
(up-set-signal ${1:typeOp} ${2:SignalId} ${3:typeOp} ${4:Value})
```

