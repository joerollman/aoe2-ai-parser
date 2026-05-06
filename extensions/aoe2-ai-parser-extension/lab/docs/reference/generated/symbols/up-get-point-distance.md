# `up-get-point-distance`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-get-point-distance"></a>

## `up-get-point-distance`

- Kind: `command`
- Detail: Action - Points

Syntax: `(up-get-point-distance <Point> <Point> <OutputGoalId>)`

Get the distance between two point goal pairs. Set Point2 to 0 to use the point that is stored by up-set-target-point. This command does not bound the points to the map, meaning you can use it for more general calculations. It simply calculates the distance formula. When calculating the distance between two precise points, it will calculate a precise distance, where the distance is 100 times larger than the actual distance.

[AIRef](https://airef.github.io/commands/commands-details.html#up-get-point-distance)

Completion insert text:

```text
(up-get-point-distance ${1:Point} ${2:Point} ${3:OutputGoalId})
```

