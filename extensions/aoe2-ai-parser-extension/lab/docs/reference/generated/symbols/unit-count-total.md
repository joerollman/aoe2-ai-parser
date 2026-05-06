# `unit-count-total`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-unit-count-total"></a>

## `unit-count-total`

- Kind: `command`
- Detail: Fact - Counting, Units

Syntax: `(unit-count-total <compareOp> <Value>)`

Checks the computer player's total unit count. The total includes trained and queued units. To check for the unit-count of other players (not including queued units), use players-unit-type-count.

[AIRef](https://airef.github.io/commands/commands-details.html#unit-count-total)

Completion insert text:

```text
(unit-count-total ${1:compareOp} ${2:Value})
```

