# `up-path-distance`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-path-distance"></a>

## `up-path-distance`

- Kind: `command`
- Detail: Fact - DUC, Points

Syntax: `(up-path-distance <Point> <Option> <compareOp> <Value>)`

Check the distance from the target object to a specified point goal pair. The distance will be 65535 if the point is unreachable. Set the Option parameter to 1 to require an open destination tile to find the path distance toward or 0 to allow for a few tiles of separation to find a reachable open tile.

[AIRef](https://airef.github.io/commands/commands-details.html#up-path-distance)

Completion insert text:

```text
(up-path-distance ${1:Point} ${2:Option} ${3:compareOp} ${4:Value})
```

