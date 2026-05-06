# `tribute-to-player`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-tribute-to-player"></a>

## `tribute-to-player`

- Kind: `command`
- Detail: Action - Diplomacy

Syntax: `(tribute-to-player <PlayerNumber> <Resource> <Value>)`

Tributes the given amount of the given resource type to the player defined by the PlayerNumber parameter. If the computer player does not have a Market, no tribute is given. In the case when the value parameter specifies an amount larger than available, only the available resources of the given type are tributed. If, for example, there is only 60 food and the tribute action specifies 100 food, only 60 food will be tributed. The tribute action is ignored when there are no resources of the given type. Tribute fees are paid and deducted from the tribute amount (if applicable). The action allows "focus-player", "target-player", and "any"/"every" wildcard parameters for pPlayerNumber. It also allows the use of rule variables for Player, such as "this-any-ally" or "this-any-enemy". It also allows for scenario-player-# and lobby-player-#, where # is between 1 and 8. scenario-player-# refers to the player color (where red = scenario-player-2), and lobby-player-# refers to the player slot (where the lobby host or human player playing a single player campaign is always lobby-player-1).

[AIRef](https://airef.github.io/commands/commands-details.html#tribute-to-player)

Completion insert text:

```text
(tribute-to-player ${1:PlayerNumber} ${2:Resource} ${3:Value})
```

