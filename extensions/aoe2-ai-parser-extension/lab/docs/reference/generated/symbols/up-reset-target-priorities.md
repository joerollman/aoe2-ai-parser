# `up-reset-target-priorities`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-reset-target-priorities"></a>

## `up-reset-target-priorities`

- Kind: `command`
- Detail: Action - Attack, Defense

Syntax: `(up-reset-target-priorities <PriorityType> <Option>)`

Reset or clear offensive or defensive targeting priorities. Restore default priorities with 0. For defensive priorities, setting the Option parameter to 1 will reset all to -1. For offensive priorities, unit types will be reset to 0, while classes will be -1. Target units on -1 offensive priority will not hold the attention of attackers if a higher priority unit appears, and you may notice attack behavior that is a bit similar to how patrol selects its targets. If the target unit is not -1 priority, the attacker may retarget, but primarily to other units with the same offensive priority. Battering rams and cannon galleons prefer to attack non-moving targets, while all other units prefer moving targets.

[AIRef](https://airef.github.io/commands/commands-details.html#up-reset-target-priorities)

Completion insert text:

```text
(up-reset-target-priorities ${1:PriorityType} ${2:Option})
```

