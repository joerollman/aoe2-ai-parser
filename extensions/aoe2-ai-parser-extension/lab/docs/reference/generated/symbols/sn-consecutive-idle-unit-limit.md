# `sn-consecutive-idle-unit-limit`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-sn-consecutive-idle-unit-limit"></a>

## `sn-consecutive-idle-unit-limit`

- Kind: `strategic-number`
- Detail: SN 76 - Attack

Sets the number of consecutive seconds that pass before a group is set to idle if all of its units are idle. The original documentation says this is only used during attack and retreat phases, but it applies to scouting units as well. This SN should be changed from its default value, which is 15. If you leave the SN unchanged and an exploring unit is given a non-exploring task, such as claiming sheep with DUC, it will wait 15 seconds before going back to exploring once it finished its non-exploring task. To remove this delay, you'll want this SN to be 0. There is likely no downside to setting this to 0.

Default: `15`

Required range: `0 to Max`

Range: `Min to Max`

[AIRef](https://airef.github.io/strategic-numbers/sn-details.html#sn-consecutive-idle-unit-limit)

