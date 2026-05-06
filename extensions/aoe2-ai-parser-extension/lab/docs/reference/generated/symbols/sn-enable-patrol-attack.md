# `sn-enable-patrol-attack`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-sn-enable-patrol-attack"></a>

## `sn-enable-patrol-attack`

- Kind: `strategic-number`
- Detail: SN 247 - Attack

Set to 1 to enable the patrol-style local targeting system. When attacking a distant target, this causes units to retarget against nearby sighted units immediately instead of waiting until they are in proximity to the original target. Note: this SN does not work on units that are information, so it will not work on grouped soldiers attacking with attack-now or sn-number-attack-groups. It doesn't cause your AI to put soldiers into formation and patrol a formed group toward the enemy, as the name might suggest. Instead ungrouped units sent to attack will patrol toward their target. If you use one-soldier attack groups or TSA, you'll almost always want to set this SN to 1. There may be cases where you may want to keep this SN at zero, such as if your AI is trying to raid or if the enemy has a forward tower that you want to ignore, so that your soldiers will march all the way to their attack target without getting sidetracked.

Default: `0`

Required range: `0 to 1`

Range: `Min to Max`

[AIRef](https://airef.github.io/strategic-numbers/sn-details.html#sn-enable-patrol-attack)

