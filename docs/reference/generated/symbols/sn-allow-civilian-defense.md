# `sn-allow-civilian-defense`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-sn-allow-civilian-defense"></a>

## `sn-allow-civilian-defense`

- Kind: `strategic-number`
- Detail: SN 225 - Defense

Set to 0 to disable civilian defense except against gaia (wolves, etc.), 1 to defend against weak, non-ranged units (like AoC), 2 for all weak units except warships and units faster than villagers, and 3 for all weak units except warships. For reference, villager speed: default: 0.8, wheelbarrow: 0.88, hand-cart: 0.97. For archer-line and skirmisher-line, speed: 0.96. With sn-allow-civilian-offense set to 1, the "weak units" check is eliminated, allowing for a more aggressive response. Despite the speed advantage, even with only wheelbarrow, early ranged units are swiftly eliminated by villagers with minimal losses and luring.

Default: `1`

Required range: `0 to 3`

Range: `Min to Max`

[AIRef](https://airef.github.io/strategic-numbers/sn-details.html#sn-allow-civilian-defense)

