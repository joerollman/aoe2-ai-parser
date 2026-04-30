# `sn-disable-defend-groups`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-sn-disable-defend-groups"></a>

## `sn-disable-defend-groups`

- Kind: `strategic-number`
- Detail: SN 277 - Defense

Append flags to disable various defense systems: 1 to disable the defensive (TSA) targeting system, 2 to disable assistance inside sn-safe-town-size, 4 to disable assistance between sn-safe-town-size and sn-maximum-town-size, 8 to disable assistance outside sn-maximum-town-size. When assistance is disabled, please be aware that your units will only respond to attackers within their individual line of sight. If set to 0, units will respond to threats in town as usual.

Default: `0`

Required range: `0 to 15`

Range: `Min to Max`

[AIRef](https://airef.github.io/strategic-numbers/sn-details.html#sn-disable-defend-groups)

