# `sn-percent-civilian-explorers`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-sn-percent-civilian-explorers"></a>

## `sn-percent-civilian-explorers`

- Kind: `strategic-number`
- Detail: SN  - Exploring

Caps the number of villagers assigned to explore to the given percentage. It's recommended to set this SN to 100 and use other SNs to control villager exploration. Setting this SN to 100 will not prevent villagers from gathering or constructing buildings. This SN does not affect fishing ships, and sn-number-boat-explore-groups should be used instead for fishing ships. In practice, this SN caps the number of villagers to a percentage of all villagers, rounded up. So, if it is set to 33%, one of the three starting villagers will explore, but if it is set to 34%, then two villagers will explore (34% of 3 is 1.02, which when rounded up is 2). The AI will calculate the number of villagers to task to explore based on sn-percent-civilian-explorers, sn-cap-civilian-explorers, and sn-total-number-explorers, ultimately using whichever SN results in the smallest number of explorers. If at least sn-percent-half-exploration percent of the map is explored, this number is cut in half, so it's best to set sn-percent-half-exploration to 100 to have full control over the number of exploring villagers. The AI will try assign as many villagers as possible to reach the desired number of explorers, but villagers currently tasked to build, repair, explore, or gather (except non-luring hunters and miners) are not available to be tasked to explore. Instead, villagers assigned to these tasks must have their current task cancelled first, such as with up-retask-gatherers or garrisoning the villagers, or the AI will wait until their current task is finished before tasking the villager to explore, such as a lumberjack finishing the current tree. To stop villagers from exploring, set sn-percent-civilian-explorers, sn-cap-civilian-explorers, or sn-total-number-explorers to 0, and use up-reset-scouts. All land explorers will explore around the AI's town when the game time is less than sn-home-exploration-time. After the game time exceeds the value of sn-home-exploration-time, explorers will start exploring locations further away. It's usually simplest to use just one of sn-percent-civilian-explorers, sn-cap-civilian-explorers, and sn-total-number-explorers to cap villager exploration. Often, sn-cap-civilian-explorers is the easiest to use, and you can just set sn-percent-civilian-explorers to 100 and sn-total-number-explorers to a high number like 10, and then not worry about having to change them later. However, if you don't have a specific desired number of villager explorers that you want, and you just want to set a certain % of them to explore, you can set sn-cap-civilian-explorers to -1 (-1 = ignore sn-cap-civilian-explorers), and just use sn-percent-civilian-explorers instead. The settings of sn-percent-civilian-builders and sn-percent-civilian-gatherers do not affect the number of villagers that can be tasked to explore. Also, sn-minimum-civilian-explorers and archived-non-de-strategic-number don't appear to affect the number of villager explorers, so you can ignore these SNs.

Default: `34`

Required range: `0 to 100`

Range: `Min to Max`

[AIRef](https://airef.github.io/strategic-numbers/sn-details.html#sn-percent-civilian-explorers)

