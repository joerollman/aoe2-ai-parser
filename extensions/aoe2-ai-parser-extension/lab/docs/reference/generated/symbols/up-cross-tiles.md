# `up-cross-tiles`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-cross-tiles"></a>

## `up-cross-tiles`

- Kind: `command`
- Detail: Action - Points

Syntax: `(up-cross-tiles <Point> <Point> <typeOp> <Value>)`

Get a point perpendicular to two point goal pairs. The Value parameter specifies how many tiles away the new point will be from Point1, perpendicularly away in reference to Point2. A negative Value will result in the new point being located perpendicularly away in opposite direction. Set Point2 to 0 to use the point that is stored by up-set-target-point. The new point will be stored in Point1.

[AIRef](https://airef.github.io/commands/commands-details.html#up-cross-tiles)

Completion insert text:

```text
(up-cross-tiles ${1:Point} ${2:Point} ${3:typeOp} ${4:Value})
```

