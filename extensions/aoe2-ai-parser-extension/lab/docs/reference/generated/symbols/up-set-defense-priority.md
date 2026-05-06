# `up-set-defense-priority`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-set-defense-priority"></a>

## `up-set-defense-priority`

- Kind: `command`
- Detail: Action - Attack, Defense

Syntax: `(up-set-defense-priority <typeOp> <BuildingId> <typeOp> <Value>)`

Set the defensive (TSA) targeting priority for a building. This has no effect against units. Also, unit lines do not work here, so just set the base unit type id (spearman for the entire spearman-line, etc.). Classes may be used, as well. For walls, use class 927; for gates, use class 939.

[AIRef](https://airef.github.io/commands/commands-details.html#up-set-defense-priority)

Completion insert text:

```text
(up-set-defense-priority ${1:typeOp} ${2:BuildingId} ${3:typeOp} ${4:Value})
```

