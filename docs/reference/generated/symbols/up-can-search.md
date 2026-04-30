# `up-can-search`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-can-search"></a>

## `up-can-search`

- Kind: `command`
- Detail: Fact - Can Do, DUC

Syntax: `(up-can-search <SearchSource>)`

Check the status for either the local or remote search. If the result list is full or the index offset is at the end of the player object list, this will return false.

[AIRef](https://airef.github.io/commands/commands-details.html#up-can-search)

Completion insert text:

```text
(up-can-search ${1:SearchSource})
```

