# `up-compare-flag`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-compare-flag"></a>

## `up-compare-flag`

- Kind: `command`
- Detail: Fact - Goals

Syntax: `(up-compare-flag <GoalId> <compareOp> <Flag>)`

Perform a bitwise flag test with a goal variable. Flags allow multiple states to be stored in a single value by using powers of 2 (1, 2, 4, 8, 16, etc.). You can use [cgs]:== to see if a flag is stored or [cgs]:!= to see if it isn't stored.

[AIRef](https://airef.github.io/commands/commands-details.html#up-compare-flag)

Completion insert text:

```text
(up-compare-flag ${1:GoalId} ${2:compareOp} ${3:Flag})
```

