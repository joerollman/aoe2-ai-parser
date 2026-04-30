# `sn-object-repair-level`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-sn-object-repair-level"></a>

## `sn-object-repair-level`

- Kind: `strategic-number`
- Detail: SN 246 - Defense

Add bit flags together to generate a value: 0 = wonder; 1 = castle, monastery; 2 = town-center; 4 = barracks; 8 = archery-range; 16 = stable; 32 = siege-workshop; 64 = dock; 128 = market; 256 = university; 512 = blacksmith; 1024 = lumber-camp, mining-camp, mill; 2048 = house; 4096 = towers; 8192 = walls and gates; 16384 = siege weapons. For scenarios and campaigns, the default is 1 for compatibility. The default is 16387 (wonder, castle, monastery, town-center, siege) for all other game modes. Examples: 0 = wonder only (essentially disabled) 1 = wonder, castle, monastery (the AoC repair level) 3 = wonder, castle, monastery, town-center 20547 = wonder, castle, monastery, town-center, dock, towers, siege weapons (scripter64 uses this in Chameleon) 20547 = 0 + 1 + 2 + 64 + 4096 + 16384

Default: `16387`

Required range: `0 to Max`

Range: `Min to Max`

[AIRef](https://airef.github.io/strategic-numbers/sn-details.html#sn-object-repair-level)

