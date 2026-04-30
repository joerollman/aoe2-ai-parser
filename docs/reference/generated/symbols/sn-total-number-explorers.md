# `sn-total-number-explorers`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-sn-total-number-explorers"></a>

## `sn-total-number-explorers`

- Kind: `strategic-number`
- Detail: SN 18 - Exploring

Caps the total number of land explorers allocated. It's recommended to set this SN to a high number like 10 and use other SNs to control exploration. This SN sets a cap on all total land explorers, both land military units and villagers. Ship explorers aren't included. Some older documentation states that setting sn-total-number-explorers to -1 will ignore this SN, but using -1 prevents villagers from exploring. To determine the number of explorers the AI uses, first, the AI will calculate the number of villagers to task to explore based on sn-percent-civilian-explorers, sn-cap-civilian-explorers, and sn-total-number-explorers, ultimately using whichever SN results in the smallest number of villager explorers. Then, if the number of villager explorers is less than sn-total-number-explorers, the AI will send military units to explore until it reaches the number of sn-number-explore-groups or the total number of land explorers reaches sn-total-number-explorers. If at least sn-percent-half-exploration percent of the map is explored, the amount of this SN is cut in half, so it's best to set sn-percent-half-exploration to 100 to have full control over the number of exploring units. The AI will try assign as many land units as possible to reach the desired number of explorers, but villagers currently tasked to build, repair, explore, or gather (except non-luring hunters and miners) are not available to be tasked to explore. Instead, villagers assigned to these tasks must have their current task cancelled first, such as with up-retask-gatherers or garrisoning the villagers, or the AI will wait until their current task is finished before tasking the villager to explore, such as a lumberjack finishing the current tree. To stop villagers from exploring, set sn-percent-civilian-explorers, sn-cap-civilian-explorers, or sn-total-number-explorers to 0, and use up-reset-scouts. Similarly, to stop military units from exploring, set sn-number-explore-groups or sn-total-number-explorers to 0, and use up-reset-scouts. All land explorers will explore around the AI's town when the game time is less than sn-home-exploration-time. After the game time exceeds the value of sn-home-exploration-time, explorers will start exploring locations further away. It's usually simplest to use just one of sn-percent-civilian-explorers, sn-cap-civilian-explorers, and sn-total-number-explorers to cap villager exploration, and it's usually simplest to use just one of sn-number-explore-groups and sn-total-number-explorers to cap military exploration. Often, sn-cap-civilian-explorers is the easiest to use for villager exploration, and you can just set sn-percent-civilian-explorers to 100 and sn-total-number-explorers to a high number like 10, and then not worry about having to change them later. Similarly, for military exploration it's usually simplest to set sn-total-number-explorers to -1 to ignore this SN and just use sn-number-explore-groups. sn-minimum-civilian-explorers and archived-non-de-strategic-number don't appear to affect the number of villager explorers, so you can ignore these SNs.

Default: `4`

Required range: `-1 to Max`

Range: `Min to Max`

[AIRef](https://airef.github.io/strategic-numbers/sn-details.html#sn-total-number-explorers)

