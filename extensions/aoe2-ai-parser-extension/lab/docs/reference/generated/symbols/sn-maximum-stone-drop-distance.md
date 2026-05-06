# `sn-maximum-stone-drop-distance`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-sn-maximum-stone-drop-distance"></a>

## `sn-maximum-stone-drop-distance`

- Kind: `strategic-number`
- Detail: SN 238 - Economy

The parameters control how far from a dropsite a given resource type can be before the CP ignores it. -1 indicates a &quot;don't care&quot; -- i.e. it can be any distance (as it used to be). -2 disables stone gathering. The default of this SN is -1, meaning the SN is ignored by default. This can allow the AI's villagers to go all the across the map to gather stone if the AI ran out of that resource at home. To fix this, set a reasonable maximum distance at the beginning of the game, such as 20, and increase it throughout the game, perhaps per age. You'll probably want to set these SNs back to -1 later on in the game, perhaps in the Imperial Age or after an hour of game time, to prevent your AI from ignoring certain resources.

Default: `-1`

Required range: `-2 to 255`

Range: `Min to Max`

[AIRef](https://airef.github.io/strategic-numbers/sn-details.html#sn-maximum-stone-drop-distance)

