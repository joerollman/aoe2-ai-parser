# `up-modify-goal`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-modify-goal"></a>

## `up-modify-goal`

- Kind: `command`
- Detail: Fact/Action - Goals

Syntax: `(up-modify-goal <GoalId> <mathOp> <Value>)`

Perform math operations on the value stored in a goal variable. This command can be used as either a Fact or an Action, meaning the command can appear before the "=>" in the rule or after it. The behavior of the command is identical, regardless of whether it is used as a Fact or as an Action. This command is a much more flexible version of the set-goal command, which only allows you to set a goal to a specific value. up-modify-goal allows you to add, subtract, multiply, divide, find remainders, find percentages, find min and max values, and do other mathematical operations, either with specific numbers or with the values currently stored in a goal or strategic number. See the pMathOp page for a full list of all the operations available, along with in-depth examples of each operation.

[AIRef](https://airef.github.io/commands/commands-details.html#up-modify-goal)

Completion insert text:

```text
(up-modify-goal ${1:GoalId} ${2:mathOp} ${3:Value})
```

