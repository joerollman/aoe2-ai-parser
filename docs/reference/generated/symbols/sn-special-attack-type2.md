# `sn-special-attack-type2`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-sn-special-attack-type2"></a>

## `sn-special-attack-type2`

- Kind: `strategic-number`
- Detail: SN 107 - Attack

Set to any unit, building, or group id to direct attacks. Unit lines do not work. This SN only affects soldiers attacking with attack groups or attack-now. scripter64 created a test scenario and was able to switch between targeting a mill and a lumber camp on demand using the following steps: Set special-attack-type2 to millDisband groups (I set group-form-distance:0, minimum/maximum-attack-group-size:0, number-attack-groups:0)Wait a turn or two (more turns gives more time for groups to disband)Assign multi-unit attack groups as usual (single-unit groups do not use attack-intelligence)Units depart for the enemy mill as expectedSet special-attack-type2 to lumber-campDisband groups againWait a turn or twoAssign multi-unit attack groups as usualUnits retarget toward the enemy lumber campLoop to 01 You must defconst this SN before using it, like (defconst sn-special-attack-type2 107)

Default: `-1`

Required range: `-1 to Max`

Range: `Min to Max`

[AIRef](https://airef.github.io/strategic-numbers/sn-details.html#sn-special-attack-type2)

