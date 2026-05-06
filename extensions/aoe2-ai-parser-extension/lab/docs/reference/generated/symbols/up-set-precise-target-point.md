# `up-set-precise-target-point`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-set-precise-target-point"></a>

## `up-set-precise-target-point`

- Kind: `command`
- Detail: Action - DUC

Syntax: `(up-set-precise-target-point <Point>)`

Set the target point with an unchecked extended goal pair. This command is identical to up-set-target-point, except it will not bound the point inside the map. Please ensure the point is valid with up-bound-precise-point. A precise point is expected to be a normal point x100 for 2 places of decimal precision.

[AIRef](https://airef.github.io/commands/commands-details.html#up-set-precise-target-point)

Completion insert text:

```text
(up-set-precise-target-point ${1:Point})
```

