# `up-set-offense-priority`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-set-offense-priority"></a>

## `up-set-offense-priority`

- Kind: `command`
- Detail: Action - Attack

Syntax: `(up-set-offense-priority <typeOp> <ObjectId> <typeOp> <Value>)`

Set the offensive targeting priority for an object. This is used when attacking with snNumberAttackGroups or attack-now. snEnableOffensivePriority must be set to 1 for these priorities to take effect. Note: offensive priorities have a very small range. You can turn the priorities up to 11 (highest), but no more. Also, unit lines do not work here, so just set the base unit type id (spearman for the entire spearman-line, etc.). Classes may be used, as well. If a unit has its type priority set, that will override its class priority. Target units on -1 offensive priority will not hold the attention of attackers if a higher priority unit appears. If the target unit is not -1 priority, the attacker may retarget to other units nearby, but primarily to other units with the same offensive priority. Battering rams and cannon galleons prefer to attack non-moving targets, while all other units prefer moving targets. If you clear offensive priorities with up-reset-target-priorities, you may notice attack behavior that is a bit similar to patrol.

[AIRef](https://airef.github.io/commands/commands-details.html#up-set-offense-priority)

Completion insert text:

```text
(up-set-offense-priority ${1:typeOp} ${2:ObjectId} ${3:typeOp} ${4:Value})
```

