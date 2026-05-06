# `sn-local-targeting-mode`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-sn-local-targeting-mode"></a>

## `sn-local-targeting-mode`

- Kind: `strategic-number`
- Detail: SN 286 - Attack

Set to 1 to prioritize attack bonuses and overall damage per hit. If set to 2, units will prioritize targets with high base pierce armor, such as rams; otherwise, they will target as usual. The offensive priority value of a target (-1 to 11) is added to the weight for modes 1 and 2, as well. If set to 0, units will target as usual. Note that units that do 1hp or less damage per hit (like archers) will intentionally try to avoid wasting shots on high-pierce targets like rams on modes 1 and 2, if a better target is available. Here are the exact weight calculations:SN = 0 (AoC local targeting system): 5 weight is given to the current target, 0-75 weight based on distance (nearest available target is 75, farthest is 0), and 0-10 weight is given to time to eliminate the target based on number of hits and reload time.SN = 1: Weight = the net attack value (i.e. attack+bonuses-armor) * 3 + offensive-priority-value. If the net attack value is SN = 2: Weight is the same as SN = 1, but only if the target has >= 40 base pierce armor; otherwise default local targeting behavior is used (the SN=0 weights).In other words, SN=2 is primarily for defense from things like rams coming for your trebuchets, etc. With SN=1, you might get the best behavior. After all weights are added together, the target with the highest weight is attacked. It's possible that the weights from SN=0 are added to the weights of SN=1 when sn-local-targeting-mode is set to 1, but probably not. The explanations from patch notes are unclear. However, units that don't move have reduced priority compared to units that move, except rams, cannon galleons, petards, and trebuchets have this ordering reversed and prioritize units that don't move first.

Default: `0`

Required range: `0 to 2`

Range: `Min to Max`

[AIRef](https://airef.github.io/strategic-numbers/sn-details.html#sn-local-targeting-mode)

