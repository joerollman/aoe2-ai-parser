# `sn-coop-share-attacking`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-sn-coop-share-attacking"></a>

## `sn-coop-share-attacking`

- Kind: `strategic-number`
- Detail: SN 196 - Attack

Controls whether allied computer players can attack to defend each other. If set to 1, it appears to run computations any time a unit takes damage, and if it's an ally unit it will increase the likelihood that attack groups will come help the ally whenever sn-number-attack-groups is set > 0. It should have no effect on attack-now, TSA, or any other attack methods. If you don't use attack groups, or you use sn-target-player-number to select the enemy player to attack, it's best to set this SN to 0 to improve game performance.

Default: `1`

Required range: `0 to 1`

Range: `Min to Max`

[AIRef](https://airef.github.io/strategic-numbers/sn-details.html#sn-coop-share-attacking)

