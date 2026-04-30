# `fe-filter-garrisoned`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-fe-filter-garrisoned"></a>

## `fe-filter-garrisoned`

- Kind: `command`
- Detail: Action - DUC

Syntax: `(fe-filter-garrisoned <typeOp> <Option>)`

DE only. Filters whether garrisoned and/or ungarrisoned units are found in DUC searches. Set to 0 before a DUC search to exclude objects that are garrisoned in a building, ram, or transport ship from future DUC searches, but allow units that aren't garrisoned to be found (the default setting). Set to 1 before a DUC search to allow both garrisoned and ungarrisoned units to be found. Set to 2 before a DUC search to exclude ungarrisoned units. Using up-full-reset-search or up-reset-filters will reset the filter back to its default setting (0).

[AIRef](https://airef.github.io/commands/commands-details.html#fe-filter-garrisoned)

Completion insert text:

```text
(fe-filter-garrisoned ${1:typeOp} ${2:Option})
```

