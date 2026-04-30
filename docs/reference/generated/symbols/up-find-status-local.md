# `up-find-status-local`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-find-status-local"></a>

## `up-find-status-local`

- Kind: `command`
- Detail: Fact/Action - DUC

Syntax: `(up-find-status-local <typeOp> <UnitId> <typeOp> <Value>)`

Find objects owned by the local player filtered by status. This is identical to up-find-local, except it will consider the status value set by up-filter-status. If UnitId changes, the search index offset will be reset. Otherwise, it will continue from where it left off. This command can be used as either a Fact or an Action.

[AIRef](https://airef.github.io/commands/commands-details.html#up-find-status-local)

Completion insert text:

```text
(up-find-status-local ${1:typeOp} ${2:UnitId} ${3:typeOp} ${4:Value})
```

