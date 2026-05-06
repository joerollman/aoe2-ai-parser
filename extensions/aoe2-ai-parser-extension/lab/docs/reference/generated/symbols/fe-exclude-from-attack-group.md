# `fe-exclude-from-attack-group`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-fe-exclude-from-attack-group"></a>

## `fe-exclude-from-attack-group`

- Kind: `command`
- Detail: Action - Attack

Syntax: `(fe-exclude-from-attack-group <typeOp> <UnitId>)`

DE only. Removes the given unit type from attack-now and attack-groups attacks. To reset the list of units excluded from attack-now and attack-group attacks, use fe-reset-attack-group-exclusion-list.

[AIRef](https://airef.github.io/commands/commands-details.html#fe-exclude-from-attack-group)

Completion insert text:

```text
(fe-exclude-from-attack-group ${1:typeOp} ${2:UnitId})
```

