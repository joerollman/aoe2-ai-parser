# `up-get-search-state`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-get-search-state"></a>

## `up-get-search-state`

- Kind: `command`
- Detail: Action - DUC

Syntax: `(up-get-search-state <OutputGoalId>)`

Get the search state into 4 consecutive extended goals. The goals will be filled with data in the following order: current local search total, last local search count, current remote search total, last remote search count.

[AIRef](https://airef.github.io/commands/commands-details.html#up-get-search-state)

Completion insert text:

```text
(up-get-search-state ${1:OutputGoalId})
```

