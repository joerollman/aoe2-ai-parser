# `sn-enemy-sighted-response-distance`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-sn-enemy-sighted-response-distance"></a>

## `sn-enemy-sighted-response-distance`

- Kind: `strategic-number`
- Detail: SN 20 - Attack

Sets the distance inside of which units will be candidates for response to an enemy attack. The maximum distance is 50 tiles, unless sn-disable-sighted-response-cap is set to 1. Once an enemy attack is detected, sn-percent-enemy-sighted-response sets the percentage of the AI's military units within sn-enemy-sighted-response-distance from the attack who will respond to the attack. They will respond by targeting the enemy unit that initiated the attack. This response only applies to an AI's units that are attacked outside of either sn-maximum-town-size or sn-safe-town-size. Otherwise, the town defense system takes over. See sn-disable-defend-groups for details on the town defense system.

Default: `25`

Required range: `0 to 50`

Range: `Min to 50`

[AIRef](https://airef.github.io/strategic-numbers/sn-details.html#sn-enemy-sighted-response-distance)

