# `up-store-player-name`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-store-player-name"></a>

## `up-store-player-name`

- Kind: `command`
- Detail: Action - Other Player Info, Text Data

Syntax: `(up-store-player-name <PlayerNumber>)`

Store a player name in the internal buffer. The buffer can be referenced by the chat-data commands using %s instead of %d with c: 7031232 (7031232 cannot be stored in a defconst). This buffer is shared by all AIs, so please store data before using it in a rule pass. The action only allows for exact player numbers, "my-player-number", or "this-any" rule variables for pPlayerNumber, such as "this-any-ally" or "this-any-enemy". It does not allow "any"/"every" wildcard parameters for pPlayerNumber. It also allows for scenario-player-# and lobby-player-#, where # is between 1 and 8. scenario-player-# refers to the player color (where red = scenario-player-2), and lobby-player-# refers to the player slot (where the lobby host or human player playing a single player campaign is always lobby-player-1).

[AIRef](https://airef.github.io/commands/commands-details.html#up-store-player-name)

Completion insert text:

```text
(up-store-player-name ${1:PlayerNumber})
```

