# `up-modify-flag`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-modify-flag"></a>

## `up-modify-flag`

- Kind: `command`
- Detail: Action - Goals

Syntax: `(up-modify-flag <GoalId> <mathOp> <Flag>)`

Modify a bitwise flag on the value stored in a goal variable. Flags allow multiple states to be stored in a single value by using powers of 2 (1, 2, 4, 8, 16, etc.). The only ops allowed are [cgs]:+ to append a flag and [cgs]:- to remove a flag.

[AIRef](https://airef.github.io/commands/commands-details.html#up-modify-flag)

Completion insert text:

```text
(up-modify-flag ${1:GoalId} ${2:mathOp} ${3:Flag})
```

