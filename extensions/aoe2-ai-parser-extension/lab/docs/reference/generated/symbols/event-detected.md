# `event-detected`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-event-detected"></a>

## `event-detected`

- Kind: `command`
- Detail: Fact - Scenarios

Syntax: `(event-detected <EventType> <EventId>)`

Checks if the given event has been detected. Scenario triggers that execute an AI Script Goal effect are the only events that AI scripts can detect. The event-detected fact stays true until the event is explicitly disabled by the acknowledge-event action. This command, along with acknowledge-event, is used to detect an AI Script Goal effect from a scenario trigger, often with the intention of changing the AI behavior after the scenario trigger has fired. The scenario designer chooses an AI Trigger number for the AI Script Goal effect in the scenario editor. Then, the event-detected command in the AI script will detect when this trigger effect happens. The event-detected command will remain true after the AI Script Goal trigger effect fires, so acknowledge-event is used to reset the event-detected flag so that event-detected will no longer be true, similar to how the disable-timer command clears a timer that has triggered or how the acknowledge-taunt command accepts the taunt message. Trigger events are essentially the inverse of signals. To allow an AI script to send a signal which the AI Signal trigger condition can detect, use set-signal.

[AIRef](https://airef.github.io/commands/commands-details.html#event-detected)

Completion insert text:

```text
(event-detected ${1:EventType} ${2:EventId})
```

