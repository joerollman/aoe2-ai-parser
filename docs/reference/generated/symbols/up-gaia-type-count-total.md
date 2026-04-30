# `up-gaia-type-count-total`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-gaia-type-count-total"></a>

## `up-gaia-type-count-total`

- Kind: `command`
- Detail: Fact - Counting, Economy

Syntax: `(up-gaia-type-count-total <typeOp> <Resource> <compareOp> <Value>)`

Check the total sighted resource count from gaia. When checking food, wood, stone, or gold, this command operates very quickly. However, the required data does not exist for specific food types, including deer and sheep. As a fallback, it will redirect to the slower up-gaia-type-count, and the result will only reflect resources that still exist. This command does not work with relics.

[AIRef](https://airef.github.io/commands/commands-details.html#up-gaia-type-count-total)

Completion insert text:

```text
(up-gaia-type-count-total ${1:typeOp} ${2:Resource} ${3:compareOp} ${4:Value})
```

