# `up-set-placement-data`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-set-placement-data"></a>

## `up-set-placement-data`

- Kind: `command`
- Detail: Action - Buildings

Syntax: `(up-set-placement-data <PlayerNumber> <ObjectId> <typeOp> <Value>)`

Specify placement information for managed construction. Please ensure Player has at least a town-center to use for reference, if they don't have ObjectId. If Player has no objects left, placement will not work as expected. The properties assigned by up-set-placement-data that are in effect when a build command is executed are stored with them, so you can change properties immediately afterward and it won't break your previous settings. The action only allows exact player numbers, "my-player-number", or "this-any" rule variables for pPlayerNumber, such as "this-any-ally" or "this-any-computer-ally". It does not allow "any"/"every" wildcard parameters for pPlayerNumber. It cannot be used with players who aren't allies. It also allows for scenario-player-# and lobby-player-#, where # is between 1 and 8. scenario-player-# refers to the player color (where red = scenario-player-2), and lobby-player-# refers to the player slot (where the lobby host or human player playing a single player campaign is always lobby-player-1).

[AIRef](https://airef.github.io/commands/commands-details.html#up-set-placement-data)

Completion insert text:

```text
(up-set-placement-data ${1:PlayerNumber} ${2:ObjectId} ${3:typeOp} ${4:Value})
```

