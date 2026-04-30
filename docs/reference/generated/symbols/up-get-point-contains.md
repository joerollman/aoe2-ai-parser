# `up-get-point-contains`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-get-point-contains"></a>

## `up-get-point-contains`

- Kind: `command`
- Detail: Fact/Action - Points

Syntax: `(up-get-point-contains <Point> <OutputGoalId> <typeOp> <ObjectId>)`

Get the id if an object exists at a point goal pair position. Set Point to 0 to use the point that is stored by up-set-target-point. Please note that when used with all-units-class (-1), this may capture unexpected objects like birds flying over a tile, terrain plants, etc. This command can be used as either a Fact or an Action. Also, this action will work whether the point has been explored or not. Therefore, in AI tournaments up-point-explored must be used as a condition in every rule where this command is used.

[AIRef](https://airef.github.io/commands/commands-details.html#up-get-point-contains)

Completion insert text:

```text
(up-get-point-contains ${1:Point} ${2:OutputGoalId} ${3:typeOp} ${4:ObjectId})
```

