# `taunt`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-taunt"></a>

## `taunt`

- Kind: `command`
- Detail: Action - Chat, Debugging, Other Player Info

Syntax: `(taunt <TauntId>)`

Triggers the taunt associated with the given value. This taunt will only be sent to allies, and other AIs can detect this taunt with the taunt-detected command. To send a randomized taunt to allies between a range of taunt values, you can use taunt-using-range. You can also use any of the chat commands, like chat-to-player, to send a taunt along with a chat message. To do this, put the taunt number at the very beginning of the message, followed by the rest of the chat message, like (chat-to-allies "/3Please send food!"). In DE, the forward slash "/" is currently required, but in UP it is not. This example will send taunt 3 to all allies, and they will see the message without the taunt number at the beginning, just like when a human player starts a chat message with a taunt number.

[AIRef](https://airef.github.io/commands/commands-details.html#taunt)

Completion insert text:

```text
(taunt ${1:TauntId})
```

