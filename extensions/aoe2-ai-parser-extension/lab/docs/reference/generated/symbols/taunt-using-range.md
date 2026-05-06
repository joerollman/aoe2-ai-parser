# `taunt-using-range`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-taunt-using-range"></a>

## `taunt-using-range`

- Kind: `command`
- Detail: Action - Chat, Other Player Info

Syntax: `(taunt-using-range <TauntId> <Value>)`

Triggers a random taunt that is picked from a given taunt range. This taunt will only be sent to allies, and other AIs can detect this taunt with the taunt-detected command.

[AIRef](https://airef.github.io/commands/commands-details.html#taunt-using-range)

Completion insert text:

```text
(taunt-using-range ${1:TauntId} ${2:Value})
```

