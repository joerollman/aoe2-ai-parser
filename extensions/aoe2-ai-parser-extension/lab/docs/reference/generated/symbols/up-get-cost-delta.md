# `up-get-cost-delta`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-get-cost-delta"></a>

## `up-get-cost-delta`

- Kind: `command`
- Detail: Action - Cost Data

Syntax: `(up-get-cost-delta <OutputGoalId>)`

Get the difference between player resources and the current cost data, and store this difference in four consecutive goals in the order of food, wood, stone, and gold. The calculation is the current stockpile minus the current amount stored in the four cost goals from the most recent up-setup-cost-data command.

[AIRef](https://airef.github.io/commands/commands-details.html#up-get-cost-delta)

Completion insert text:

```text
(up-get-cost-delta ${1:OutputGoalId})
```

