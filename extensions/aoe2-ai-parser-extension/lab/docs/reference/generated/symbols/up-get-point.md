# `up-get-point`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-get-point"></a>

## `up-get-point`

- Kind: `command`
- Detail: Action - Points

Syntax: `(up-get-point <PositionType> <Point>)`

Read a specific (x,y) position into an extended goal pair. This command writes to 2 consecutive goals and requires an extended goal pair between 41 and 15998. If it fails to get a valid position, it will return (-1,-1).

[AIRef](https://airef.github.io/commands/commands-details.html#up-get-point)

Completion insert text:

```text
(up-get-point ${1:PositionType} ${2:Point})
```

