# `sn-whaling-max-distance`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-sn-whaling-max-distance"></a>

## `sn-whaling-max-distance`

- Kind: `strategic-number`
- Detail: SN 317 - Water

Controls how far from a dropsite a whale can be before the CP ignores it. -1 indicates a &quot;don't care&quot; -- i.e. it can be any distance (as it used to be). -2 disables all whale gathering. The default of this SN is -1, meaning the SN is ignored by default. This can allow whaling ships to go all the across the map to gather from whales, which might not be what you want early in the game. You'll probably want to set it back to -1 later on in the game, perhaps in the Imperial Age or after an hour of game time.

Default: `-1`

Required range: `-2 to 255`

Range: `Min to Max`

[AIRef](https://airef.github.io/strategic-numbers/sn-details.html#sn-whaling-max-distance)

