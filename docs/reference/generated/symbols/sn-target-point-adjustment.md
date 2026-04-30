# `sn-target-point-adjustment`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-sn-target-point-adjustment"></a>

## `sn-target-point-adjustment`

- Kind: `strategic-number`
- Detail: SN 292 - Other

Set to adjust the tile positioning of up-target-point toward 1:left, 2:top, 3:right, 4:bottom, 5:middle, 6:precise. If set to 0, actions will be directed to the absolute left-most point of a tile. If set to precise, you must directly pass a valid precise point goal pair (point x100 for precision) to up-target-point. Note: when set to 6 (precise), all up-target-point actions will assume the point has precise coordinates when sending the units to that point, i.e. it will assume the coordinates are multiplied by 100. So, ensure that you set this strategic number back to a value from 0 to 5 before using a point with normal coordinates in a up-target-point command. Otherwise, using up-target-point with this strategic number will send units to the left corner of the map. For example, if the point has the normal coordinates (48, 187), up-target-point would send the units to point (0.48, 1.87) when this strategic number is set to 6.

Default: `0`

Required range: `0 to 6`

Range: `Min to Max`

[AIRef](https://airef.github.io/strategic-numbers/sn-details.html#sn-target-point-adjustment)

