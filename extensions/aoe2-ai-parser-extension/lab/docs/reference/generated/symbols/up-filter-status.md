# `up-filter-status`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-filter-status"></a>

## `up-filter-status`

- Kind: `command`
- Detail: Action - DUC

Syntax: `(up-filter-status <typeOp> <ObjectStatus> <typeOp> <ObjectList>)`

Set the object status value for use with up-find-status. The default (after up-reset-filters) is 2, which should match most active objects. Buildings that are incomplete have a status of 0, while certain resources have a status of 3. For remote search, up-find-remote can find objects with object status values 0 to 3 (status-pending, status-ready, and status-resource) if you search by object type id instead of class id.

[AIRef](https://airef.github.io/commands/commands-details.html#up-filter-status)

Completion insert text:

```text
(up-filter-status ${1:typeOp} ${2:ObjectStatus} ${3:typeOp} ${4:ObjectList})
```

