# `up-find-status-remote`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-find-status-remote"></a>

## `up-find-status-remote`

- Kind: `command`
- Detail: Fact/Action - DUC

Syntax: `(up-find-status-remote <typeOp> <UnitId> <typeOp> <Value>)`

Find objects owned by the focus player for direct targeting. Set sn-focus-player-number before using this command. This is identical to up-find-remote, except it will consider the status value set by up-filter-status. If the focus or UnitId changes, the search index offset will be reset. Otherwise, it will continue from where it left off. This command can be used as either a Fact or an Action.

[AIRef](https://airef.github.io/commands/commands-details.html#up-find-status-remote)

Completion insert text:

```text
(up-find-status-remote ${1:typeOp} ${2:UnitId} ${3:typeOp} ${4:Value})
```

