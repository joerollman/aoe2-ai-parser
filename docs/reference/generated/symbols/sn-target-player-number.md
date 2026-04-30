# `sn-target-player-number`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-sn-target-player-number"></a>

## `sn-target-player-number`

- Kind: `strategic-number`
- Detail: SN 249 - Attack

Set to the number of the player that should be targeted for attack. If this sn is set to -1, initiating an attack will instead provide assistance to allies. When set to 0, sn-attack-winning-player will determine the target. Setting this to a player that cannot be attacked (an ally or the AI itself) will result in undefined behavior. You can also use this value with the &quot;target-player&quot; identifier in facts and actions.

Default: `0`

Required range: `-1 to 8`

Range: `Min to Max`

[AIRef](https://airef.github.io/strategic-numbers/sn-details.html#sn-target-player-number)

