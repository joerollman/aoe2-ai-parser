# `up-timer-status`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-timer-status"></a>

## `up-timer-status`

- Kind: `command`
- Detail: Fact - Timers

Syntax: `(up-timer-status <TimerId> <compareOp> <TimerState>)`

Check whether a timer is disabled, triggered, running, or a combination.

[AIRef](https://airef.github.io/commands/commands-details.html#up-timer-status)

Completion insert text:

```text
(up-timer-status ${1:TimerId} ${2:compareOp} ${3:TimerState})
```

