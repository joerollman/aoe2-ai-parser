# `up-chat-data-to-player`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-chat-data-to-player"></a>

## `up-chat-data-to-player`

- Kind: `command`
- Detail: Action - Chat, Debugging, Goals

Syntax: `(up-chat-data-to-player <PlayerNumber> <String> <typeOp> <Value>)`

Send a chat message with a formatted value to a player. The Action allows "my-player-number", "focus-player", "target-player", and "any"/"every" wildcard parameters for pPlayerNumber. It also allows the use of rule variables for pPlayerNumber, such as "this-any-ally" or "this-any-enemy". It also allows for scenario-player-# and lobby-player-#, where # is between 1 and 8. scenario-player-# refers to the player color (where red = scenario-player-2), and lobby-player-# refers to the player slot (where the lobby host or human player playing a single player campaign is always lobby-player-1).

[AIRef](https://airef.github.io/commands/commands-details.html#up-chat-data-to-player)

Completion insert text:

```text
(up-chat-data-to-player ${1:PlayerNumber} ${2:String} ${3:typeOp} ${4:Value})
```

