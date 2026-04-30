# `log-trace`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-log-trace"></a>

## `log-trace`

- Kind: `command`
- Detail: Action - Debugging

Syntax: `(log-trace <Value>)`

Writes the given value to a log file. Used purely for testing to check when a rule gets executed. Works only if logging is enabled (which it isn't). Use up-log-data instead. You can also use log to log a text string if you are scripting for DE.

[AIRef](https://airef.github.io/commands/commands-details.html#log-trace)

Completion insert text:

```text
(log-trace ${1:Value})
```

