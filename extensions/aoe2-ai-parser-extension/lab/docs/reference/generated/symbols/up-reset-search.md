# `up-reset-search`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-reset-search"></a>

## `up-reset-search`

- Kind: `command`
- Detail: Action - DUC

Syntax: `(up-reset-search <LocalIndex> <LocalList> <RemoteIndex> <RemoteList>)`

Reset the search state for the direct unit targeting system. Each of the four parameters can be 0 or 1:If the first parameter is 1, the search memory from previous local searches is reset. This allows all local objects to be available for the next local search. If the first parameter is 0, objects from previous local searches since the last local list reset will not be available in the next search.If the second parameter is 1, the local list search results will be emptied. If the second parameter is 0, objects in the local list will remain in the local list.If the third parameter is 1, the search memory from previous remote searches is reset. This allows all remote objects to be available for the next remote search. If the third parameter is 0, objects from previous remote searches since the last remote list reset will not be available in the next search.If the fourth parameter is 1, the remote list search results will be emptied. If the fourth parameter is 0, objects in the remote list will remain in the remote list.

[AIRef](https://airef.github.io/commands/commands-details.html#up-reset-search)

Completion insert text:

```text
(up-reset-search ${1:LocalIndex} ${2:LocalList} ${3:RemoteIndex} ${4:RemoteList})
```

