# `sn-number-explore-groups`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-sn-number-explore-groups"></a>

## `sn-number-explore-groups`

- Kind: `strategic-number`
- Detail: SN 42 - Exploring

Sets the desired number of land-based soldier exploration groups. Each explore group will only have one unit. sn-minimum-explore-group-size and sn-maximum-explore-group-size have no effect. To explore with ships, use sn-number-boat-explore-groups. The number of land-based soldier exploration groups are also affected by sn-total-number-explorers which caps the total number of land-based soldier and villager explorers. The number of villager explorers are calculated first (see sn-cap-civilian-explorers for details). Then, if the number of villager explorers is less than sn-total-number-explorers, the AI will send military units to explore until it reaches the number of sn-number-explore-groups or the total number of land explorers reaches sn-total-number-explorers. If at least sn-percent-half-exploration percent of the map is explored, the amount of this SN is cut in half, so it's best to set sn-percent-half-exploration to 100 to have full control over the number of exploring units. To stop land-based soldier units from exploring, set sn-number-explore-groups or sn-total-number-explorers to 0, and use up-reset-scouts. All land explorers will explore around the AI's town when the game time is less than sn-home-exploration-time. After the game time exceeds the value of sn-home-exploration-time, explorers will start exploring locations further away. It's usually simplest to use just one of sn-number-explore-groups and sn-total-number-explorers to cap military exploration. Often, it's usually simplest to set sn-total-number-explorers to a high number like 10 and just use sn-number-explore-groups.

Default: `0`

Required range: `0 to Max`

Range: `Min to Max`

[AIRef](https://airef.github.io/strategic-numbers/sn-details.html#sn-number-explore-groups)

