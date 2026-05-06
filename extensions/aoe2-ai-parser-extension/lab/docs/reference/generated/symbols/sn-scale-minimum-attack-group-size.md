# `sn-scale-minimum-attack-group-size`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-sn-scale-minimum-attack-group-size"></a>

## `sn-scale-minimum-attack-group-size`

- Kind: `strategic-number`
- Detail: SN 93 - Attack

The scaling factor for the minimum attack group size. Added to sn-minimum-attack-group-size when the tactical AI does its scaling. The SN automatically increases sn-minimum-attack-group-size by the value of sn-scale-minimum-attack-group-size every X minutes, where X is the value of sn-scaling-frequency. If sn-scale-minimum-attack-group-size is kept at the default of 1 and sn-scaling-frequency is kept at the default value of 10, then sn-minimum-attack-group-size will increase by 1 every 10 minutes. It's best to set sn-scale-minimum-attack-group-size to 0 and modify sn-minimum-attack-group-size directly. The automatic scaling behavior from this SN on its own isn't a big deal, but the default value of the corresponding SN sn-scale-maximum-attack-group-size is zero, meaning that sn-maximum-attack-group-size isn't automatically increased in the same manner, and eventually sn-minimum-attack-group-size can exceed sn-maximum-attack-group-size. My understanding is that this will prevent attack groups from being sent, since it is impossible for attack groups to have a valid size in this situation. Even if attack groups are still sent, it is more straightforward for scripters to set sn-scale-minimum-attack-group-size to zero and to increase sn-minimum-attack-group-size directly over time.

Default: `1`

Required range: `0 to Max`

Range: `Min to Max`

[AIRef](https://airef.github.io/strategic-numbers/sn-details.html#sn-scale-minimum-attack-group-size)

