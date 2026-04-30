# `up-find-remote`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-find-remote"></a>

## `up-find-remote`

- Kind: `command`
- Detail: Fact/Action - DUC

Syntax: `(up-find-remote <typeOp> <UnitId> <typeOp> <Value>)`

Find objects owned by the focus player for direct targeting. Set sn-focus-player-number before using this command. If the focus or UnitId changes, the search index offset will be reset. Otherwise, it will continue from where it left off. This command can be used as either a Fact or an Action. Normally, up-find-remote will only find status-ready objects, but up-find-remote can also find objects with object status values 0 to 3 (status-pending, status-ready, and status-resource) if you search by object type id instead of class id. For self/ally objects, it can find them directly at all times. For non-ally objects, if the object has been sighted and is either a building or has been seen/reseen within the past 5 seconds, it can be found. This should allow the AI to target units that are clearly visible without cheating, and target sighted enemy buildings in the fog. One other note: although the new targeting and find commands aren't as heavy as attack-now, like any command that directly manipulates units like retreat-now, guard-unit, etc., please try not to flood them.

[AIRef](https://airef.github.io/commands/commands-details.html#up-find-remote)

Completion insert text:

```text
(up-find-remote ${1:typeOp} ${2:UnitId} ${3:typeOp} ${4:Value})
```

