# `up-find-resource`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-find-resource"></a>

## `up-find-resource`

- Kind: `command`
- Detail: Fact/Action - DUC

Syntax: `(up-find-resource <typeOp> <Resource> <typeOp> <Value>)`

Find gatherable resource objects for direct targeting. This command stores data in the remote list and it will consider the status value set by up-filter-status. To find stone, gold, fallen trees, and other directly gatherable resources, status-resource is required. For standing trees and living objects, status-ready is required. Please ensure the proper status is set before searching. The remote index will reset automatically when switching between this command and other remote search commands like up-find-remote. If Resource changes, the search index offset will be reset. Otherwise, it will continue from where it left off. This command can be used as either a Fact or an Action. When searching with boar-class (class 910), this command will not include wolves in the search.

[AIRef](https://airef.github.io/commands/commands-details.html#up-find-resource)

Completion insert text:

```text
(up-find-resource ${1:typeOp} ${2:Resource} ${3:typeOp} ${4:Value})
```

