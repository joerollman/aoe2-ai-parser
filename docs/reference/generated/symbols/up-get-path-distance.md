# `up-get-path-distance`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-get-path-distance"></a>

## `up-get-path-distance`

- Kind: `command`
- Detail: Action - DUC, Points

Syntax: `(up-get-path-distance <Point> <Option> <OutputGoalId>)`

Get the distance from the target object to a specified point goal pair. This will return 65535 if the point is unreachable. Set the Option parameter to 1 to require an open destination tile to find the path distance toward or 0 to allow for a few tiles of separation to find a reachable open tile.

[AIRef](https://airef.github.io/commands/commands-details.html#up-get-path-distance)

Completion insert text:

```text
(up-get-path-distance ${1:Point} ${2:Option} ${3:OutputGoalId})
```

