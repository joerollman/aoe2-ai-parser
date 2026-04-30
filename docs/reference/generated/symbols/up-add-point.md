# `up-add-point`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-add-point"></a>

## `up-add-point`

- Kind: `command`
- Detail: Action - Points

Syntax: `(up-add-point <Point> <Point> <typeOp> <Value>)`

Add or subtract two point goal pairs together and store the result in Point1. The Value parameter indicates how many instances of Point2 to add to Point1. A negative Value will result in subtracting this number of instances of Point2 from Point1. Set Point2 to 0 to use the point that is stored by up-set-target-point.

[AIRef](https://airef.github.io/commands/commands-details.html#up-add-point)

Completion insert text:

```text
(up-add-point ${1:Point} ${2:Point} ${3:typeOp} ${4:Value})
```

