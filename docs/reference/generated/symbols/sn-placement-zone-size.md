# `sn-placement-zone-size`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-sn-placement-zone-size"></a>

## `sn-placement-zone-size`

- Kind: `strategic-number`
- Detail: SN 268 - Buildings

Set to the size of the tile zone used for forward and controlled building placement. All build commands store this value and the up-set-placement-data information with each successful call. For every pass that a building cannot be placed, its zone size will be increased from this starting point. The placement region set by sn-placement-zone-size expands by 1 tile per building every 7 "internal" passes. These internal passes usually happen ~10 times for each AI script pass. The default for this sn is 20. A small zone size (0) will provide more precise positioning. A large value allows you to surround the enemy when forward building. sn-placement-zone-size is stored with the placement data, so this SN can be changed once the building has been added to the building placement queue.

Default: `20`

Required range: `0 to 255`

Range: `Min to Max`

[AIRef](https://airef.github.io/strategic-numbers/sn-details.html#sn-placement-zone-size)

