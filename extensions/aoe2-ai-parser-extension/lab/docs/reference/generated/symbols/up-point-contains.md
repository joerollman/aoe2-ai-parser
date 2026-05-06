# `up-point-contains`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-point-contains"></a>

## `up-point-contains`

- Kind: `command`
- Detail: Fact - Buildings, Points, Units

Syntax: `(up-point-contains <Point> <typeOp> <ObjectId>)`

Check if an object exists at a point goal pair position. Set Point to 0 to use the point that is stored by up-set-target-point. Please note that when used with all-units-class (-1), this may capture unexpected objects like birds flying over a tile, terrain plants, etc. Also, this action will work whether the point has been explored or not. Therefore, in AI tournaments up-point-explored must be used as a condition in every rule where this command is used.

[AIRef](https://airef.github.io/commands/commands-details.html#up-point-contains)

Completion insert text:

```text
(up-point-contains ${1:Point} ${2:typeOp} ${3:ObjectId})
```

