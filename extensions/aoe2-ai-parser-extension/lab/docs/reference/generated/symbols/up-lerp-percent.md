# `up-lerp-percent`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-lerp-percent"></a>

## `up-lerp-percent`

- Kind: `command`
- Detail: Action - Points

Syntax: `(up-lerp-percent <Point> <Point> <typeOp> <Percent>)`

Interpolate a point by percentage between two point goal pairs and store the new point in Point1. The Percent parameter specifies the percentage of the distance between the two points that the new point will move toward or away from Point1 to Point2. If Value is positive, the new point will move closer to Point2. If Value is negative, the new point will move further away from Point2. Set Point2 to 0 to use the point that is stored by up-set-target-point.

[AIRef](https://airef.github.io/commands/commands-details.html#up-lerp-percent)

Completion insert text:

```text
(up-lerp-percent ${1:Point} ${2:Point} ${3:typeOp} ${4:Percent})
```

