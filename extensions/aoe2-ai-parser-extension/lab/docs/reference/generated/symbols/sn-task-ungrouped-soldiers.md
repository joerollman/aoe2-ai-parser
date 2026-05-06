# `sn-task-ungrouped-soldiers`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-sn-task-ungrouped-soldiers"></a>

## `sn-task-ungrouped-soldiers`

- Kind: `strategic-number`
- Detail: SN 143 - Defense

Controls whether or not ungrouped computer player soldiers get tasked to spread out and guard the computer player's general town area. When set to the default value of 1, this SN requires all idle military units to keep a certain distance from each other, usually around 4-6 tiles. The AI will check every few seconds, and if it finds units that are too close together, it will order those units to spread out. In practice, it makes units look like the are slowly wandering around the town in a random pattern, and if the AI has a large army, these soldiers may spread out a far distance away from the center of the AI's town. In most cases the behavior of sn-task-ungrouped-soldiers is undesirable, and setting the SN to zero is better. Town defense is usually most effective when defensive soldiers aren't separated. However, some scripters will temporarily set this SN to 1 for a couple seconds every minute or so to prevent soldiers from clumping around their training buildings after being trained.

Default: `1`

Required range: `0 to 1`

Range: `1 to 1`

[AIRef](https://airef.github.io/strategic-numbers/sn-details.html#sn-task-ungrouped-soldiers)

