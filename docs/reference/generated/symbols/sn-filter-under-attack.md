# `sn-filter-under-attack`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-sn-filter-under-attack"></a>

## `sn-filter-under-attack`

- Kind: `strategic-number`
- Detail: SN 276 - Attack

Set to 1 or 2 to filter retreat commands to only those units that are under attack. When this is 2, units near threatened units (within 6 tiles) will also be retreated, not just units that are under attack, which may be computationally expensive. The nearby units that will be retreated do not consider the filter type provided to up-retreat-to, and will be all military units except monks. The 1 and 2 states will also reject high base pierce armor units >= 20, so rams are left despite being attacked. If set to 0, the filter is disabled.

Default: `0`

Required range: `0 to 2`

Range: `Min to Max`

[AIRef](https://airef.github.io/strategic-numbers/sn-details.html#sn-filter-under-attack)

