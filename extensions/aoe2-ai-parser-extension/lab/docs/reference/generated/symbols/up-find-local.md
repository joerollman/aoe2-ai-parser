# `up-find-local`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-find-local"></a>

## `up-find-local`

- Kind: `command`
- Detail: Fact/Action - DUC

Syntax: `(up-find-local <typeOp> <UnitId> <typeOp> <Value>)`

Find objects owned by the local player for direct targeting. If UnitId changes, the search index offset will be reset. Otherwise, it will continue from where it left off. This command can be used as either a Fact or an Action.

[AIRef](https://airef.github.io/commands/commands-details.html#up-find-local)

Completion insert text:

```text
(up-find-local ${1:typeOp} ${2:UnitId} ${3:typeOp} ${4:Value})
```

