# `enable-timer`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-enable-timer"></a>

## `enable-timer`

- Kind: `command`
- Detail: Action - Timers

Syntax: `(enable-timer <TimerId> <Value>)`

Enables the given timer and sets it to the given time interval. The given timer can be any valid timer number, which can range from 1 to 50. You can also substitute a defconst that is defined with a value between 1 and 50 if you want to give the timer a name. Time intervals are measured in game time seconds, so enabling a timer for 240 seconds would start a 4 minute timer. If played on 2.0 speed (Fast speed), this 4 minute timer would last 2 minutes in real time. Timers have three possible states, and they cannot have multiple states at once: timer-running, timer-triggered, and timer-disabled. disable-timer or up-set-timer with a -1 timer length puts the timer in the timer-disabled state. enable-timer or up-set-timer with a timer length > 0 puts the timer in the timer-running state. disable-timer doesn't have to be used before using an enable-timer command.

[AIRef](https://airef.github.io/commands/commands-details.html#enable-timer)

Completion insert text:

```text
(enable-timer ${1:TimerId} ${2:Value})
```

