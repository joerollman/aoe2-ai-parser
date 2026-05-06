# `up-lerp-tiles`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-lerp-tiles"></a>

## `up-lerp-tiles`

- Kind: `command`
- Detail: Action - Points

Syntax: `(up-lerp-tiles <Point> <Point> <typeOp> <Value>)`

Interpolate a point by tiles between two point goal pairs and store the new point in Point1. The Value parameter specifies how many tiles the new point will move toward or away from Point1 to Point2. If Value is positive, the new point will move closer to Point2. If Value is negative, the new point will move further away from Point2. Set Point2 to 0 to use the point that is stored by up-set-target-point. Note: It is possible for the new point to be outside the bounds of the map which can cause several issues. Therefore, it is wise to use up-bound-point afterward to ensure that you always have a valid point location.

[AIRef](https://airef.github.io/commands/commands-details.html#up-lerp-tiles)

Completion insert text:

```text
(up-lerp-tiles ${1:Point} ${2:Point} ${3:typeOp} ${4:Value})
```

