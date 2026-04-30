# `disable-timer`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-disable-timer"></a>

## `disable-timer`

- Kind: `command`
- Detail: Action - Timers

Syntax: `(disable-timer <TimerId>)`

Disables the given timer. The given timer can be any valid timer number, which can range from 1 to 50. You can also substitute a defconst that is defined with a value between 1 and 50 if you want to give the timer a name. Timers have three possible states, and they cannot have multiple states at once: timer-running, timer-triggered, and timer-disabled. disable-timer or up-set-timer with a -1 timer length puts the timer in the timer-disabled state. enable-timer or up-set-timer with a timer length > 0 puts the timer in the timer-running state. disable-timer doesn't have to be used before using an enable-timer command.

[AIRef](https://airef.github.io/commands/commands-details.html#disable-timer)

Completion insert text:

```text
(disable-timer ${1:TimerId})
```

