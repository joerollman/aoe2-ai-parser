# `up-clean-search`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-clean-search"></a>

## `up-clean-search`

- Kind: `command`
- Detail: Action - DUC

Syntax: `(up-clean-search <SearchSource> <ObjectData> <SearchOrder>)`

Removes duplicate ids or sorts the search results. If ObjectData is set to -1, this will attempt to remove duplicates, lowering the result total. When removing duplicates, using search-order-none to preserve the existing order may perform slower than with asc/desc. If you wish to sort by ObjectData, it's best to remove duplicates first. Depending on the number of objects in the list, this command may be expensive, so please take care.

[AIRef](https://airef.github.io/commands/commands-details.html#up-clean-search)

Completion insert text:

```text
(up-clean-search ${1:SearchSource} ${2:ObjectData} ${3:SearchOrder})
```

