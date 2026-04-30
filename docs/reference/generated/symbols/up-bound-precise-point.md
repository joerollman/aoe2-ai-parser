# `up-bound-precise-point`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-bound-precise-point"></a>

## `up-bound-precise-point`

- Kind: `command`
- Detail: Action - Points

Syntax: `(up-bound-precise-point <Point> <Option> <typeOp> <Value>)`

Bound a point goal pair, either a normal point or a precise point, inside the map according to the number of tiles specified by the Value parameter, effectively acting as if the map has been shrunk on all sides by the number of tiles specified by the Value parameter. For example, the point (0,3) will be bounded to the point (5,5) if the Value parameter is 5. Please ensure that Value is a valid value and will not cause an overflow for the map size. If Option is set to 1, the command will treat the point goal pair as precise point and multiply the map size by 100 before bounding to account for the precise point coordinates, so the Value parameter should be adjusted accordingly by multiplying by 100. The bounded point will be stored back into the original point goal pair.

[AIRef](https://airef.github.io/commands/commands-details.html#up-bound-precise-point)

Completion insert text:

```text
(up-bound-precise-point ${1:Point} ${2:Option} ${3:typeOp} ${4:Value})
```

