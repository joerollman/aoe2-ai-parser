# `up-remove-objects`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-remove-objects"></a>

## `up-remove-objects`

- Kind: `command`
- Detail: Action - DUC

Syntax: `(up-remove-objects <SearchSource> <ObjectData> <compareOp> <Value>)`

Removes objects from the search results based on specific data. If ObjectData is set to -1, the object index in the search results will be used for data comparison when performing removal.

[AIRef](https://airef.github.io/commands/commands-details.html#up-remove-objects)

Completion insert text:

```text
(up-remove-objects ${1:SearchSource} ${2:ObjectData} ${3:compareOp} ${4:Value})
```

