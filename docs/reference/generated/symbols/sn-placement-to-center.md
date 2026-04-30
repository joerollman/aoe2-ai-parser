# `sn-placement-to-center`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-sn-placement-to-center"></a>

## `sn-placement-to-center`

- Kind: `strategic-number`
- Detail: SN 270 - Buildings

Set to 1 to force place-control to use the map center as the second point of reference for placement. The first point of reference is set with up-set-placement-data. If set to 0, the active target player's nearest building will become the second point of reference instead, once discovered. If sn-target-player-number is 0, the target enemy will be determined by sn-attack-winning-player.

Default: `0`

Required range: `0 to 1`

Range: `Min to Max`

[AIRef](https://airef.github.io/strategic-numbers/sn-details.html#sn-placement-to-center)

