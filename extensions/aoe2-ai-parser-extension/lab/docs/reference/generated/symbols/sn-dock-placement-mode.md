# `sn-dock-placement-mode`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-sn-dock-placement-mode"></a>

## `sn-dock-placement-mode`

- Kind: `strategic-number`
- Detail: SN 278 - Water

Set to 1 to prefer placement toward the front, -1 to prefer placement toward the back, or 0 for standard placement. Placement toward the front or back means closer to the map center or further away from the map center, relative to the home town center. Higher positive values like 2 or 3 can theoretically set an even higher priority toward placing the dock near the map center. Note: it is important to explore the area you want the AI to build the dock. Otherwise, it will only build the dock on shoreline you have explored.

Default: `0`

Required range: `-1 to 1`

Range: `Min to Max`

[AIRef](https://airef.github.io/strategic-numbers/sn-details.html#sn-dock-placement-mode)

