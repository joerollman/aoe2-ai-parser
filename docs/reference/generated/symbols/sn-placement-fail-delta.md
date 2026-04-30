# `sn-placement-fail-delta`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-sn-placement-fail-delta"></a>

## `sn-placement-fail-delta`

- Kind: `strategic-number`
- Detail: SN 269 - Buildings

Set to the value that will be added to the placement distance set by up-set-placement-data for every pass that a building cannot be placed. This sn does not affect forward building. It should be a low value (-2 to 2). The default is 0, which means that only the per-building zone-size is increased for each placement failure. This zone size expands by 1 per building every 7 "internal" passes. These internal passes usually happen ~10 times for each AI script pass. Unlike sn-placement-zone-size, sn-placement-fail-delta is not stored with the placement data.

Default: `0`

Required range: `-10 to 10`

Range: `Min to Max`

[AIRef](https://airef.github.io/strategic-numbers/sn-details.html#sn-placement-fail-delta)

