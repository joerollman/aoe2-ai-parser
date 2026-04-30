# `taunt-detected`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-taunt-detected"></a>

## `taunt-detected`

- Kind: `command`
- Detail: Fact - Chat, Debugging, Other Player Info

Syntax: `(taunt-detected <PlayerNumber> <TauntId>)`

Detects a given taunt from the given player. The check can be performed any number of times until the taunt is explicitly acknowledged, meaning that if the given taunt is received from the given player, this fact with remain true until the AI uses the acknowledge-taunt command to acknowledge the taunt from that player. taunt-detected will detect taunts sent to the AI from another AI that uses the taunt command, and it will also detect taunts sent in a chat message if the message starts with a number between 1 and 255. The fact allows "focus-player", "target-player", and "any"/"every" wildcard parameters for pPlayerNumber. It also allows for scenario-player-# and lobby-player-#, where # is between 1 and 8. scenario-player-# refers to the player color (where red = scenario-player-2), and lobby-player-# refers to the player slot (where the lobby host or human player playing a single player campaign is always lobby-player-1).

[AIRef](https://airef.github.io/commands/commands-details.html#taunt-detected)

Completion insert text:

```text
(taunt-detected ${1:PlayerNumber} ${2:TauntId})
```

