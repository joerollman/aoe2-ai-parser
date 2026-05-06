# `set-signal`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-set-signal"></a>

## `set-signal`

- Kind: `command`
- Detail: Action - Scenarios

Syntax: `(set-signal <SignalId>)`

Sets a given signal value that can be checked by the AI Signal trigger condition in the scenario editor. To set a signal dynamically, use up-set-signal. To check if a signal was already set, use up-get-signal. There are 256 different signals that an AI can send to the scenario editor, from 0 to 255, which can trigger various events in the scenario. Signals are essentially on/off flags which are set to "off" at the beginning of the game, and are set to "on" whenever the set-signal action is used. This AI Signal trigger condition can be very useful to detect events that AIs can detect, but scenario triggers cannot easily detect, such as receiving tribute. Once the given signal is set, the scenario designer can create a trigger with the condition "AI Signal", and select the corresponding AI Signal value in the dropdown list. Once the signal is set in the AI script, the AI Signal condition for the given signal value will become true for the rest of the game, even after a trigger with an AI Signal condition is executed, unless you use the up-set-signal AI command to turn the signal off by setting the signal ID to the value 0, or the scenario designer uses the Acknowledge AI Signal trigger effect to turn the signal off (this trigger effect is only available in DE). Signals are essentially the inverse of AI Script Goal trigger effects. To allow an AI script to detect an AI Script Goal trigger effect from a scenario trigger, use event-detected. This action only works with a single player scenario and "AI Signal" trigger condition. For a multiplayer scenario, use "Multiplayer AI Signal" and fe-set-signal.

[AIRef](https://airef.github.io/commands/commands-details.html#set-signal)

Completion insert text:

```text
(set-signal ${1:SignalId})
```

