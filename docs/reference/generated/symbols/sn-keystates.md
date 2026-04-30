# `sn-keystates`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-sn-keystates"></a>

## `sn-keystates`

- Kind: `strategic-number`
- Detail: SN 312 - Other

This allows the AI to input ctrl and shift inputs when issuing commands. Setting to 1 corresponds to shift, setting to 2 corresponds to ctrl and setting to 3 corresponds to both. sn-keystates affects the behavior of up-target-objects and up-target-point, and it affects them at the moment those commands are used, so set this strategic number before using them. sn-keystates can safely be set back to another value immediately after those commands are used. Using the Shift option allows AI scripters to set movement waypoints or queue commands for units, like using Shift in a normal game. Using the Ctrl option allows AI scripters to force units to target an object more directly than normal, making the units less likely to retarget to another object.

Default: `0`

Required range: `0 to 3`

Range: `Min to Max`

[AIRef](https://airef.github.io/strategic-numbers/sn-details.html#sn-keystates)

