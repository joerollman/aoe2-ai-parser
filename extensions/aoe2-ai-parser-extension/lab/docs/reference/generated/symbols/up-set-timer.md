# `up-set-timer`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-set-timer"></a>

## `up-set-timer`

- Kind: `command`
- Detail: Action - Timers

Syntax: `(up-set-timer <typeOp> <TimerId> <typeOp> <Value>)`

Disable or enable a timer by interval. Set Value to -1 to disable the timer. If Value is positive, this will perform like the enable-timer action.

[AIRef](https://airef.github.io/commands/commands-details.html#up-set-timer)

Completion insert text:

```text
(up-set-timer ${1:typeOp} ${2:TimerId} ${3:typeOp} ${4:Value})
```

