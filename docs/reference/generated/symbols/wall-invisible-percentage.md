# `wall-invisible-percentage`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-wall-invisible-percentage"></a>

## `wall-invisible-percentage`

- Kind: `command`
- Detail: Fact - Buildings, Walls & Gates

Syntax: `(wall-invisible-percentage <Perimeter> <compareOp> <Value>)`

Checks what percentage of the potential wall placement is covered with fog. If the invisible percentage is not equal to 0 we do not know if there is a hole or not. This is because the hidden tile(s) might have a tree(s). The given perimeter must have been enabled with enable-wall-placement, and you should not check the invisible percentage until the pass after the given wall perimeter has been enabled. Allowed perimeter values are 1 and 2, with 1 being closer to the Town Center than 2. Perimeter 1 is usually between 10 and 20 tiles from the starting Town Center. Perimeter 2 is usually between 18 and 30 tiles from the starting Town Center.

[AIRef](https://airef.github.io/commands/commands-details.html#wall-invisible-percentage)

Completion insert text:

```text
(wall-invisible-percentage ${1:Perimeter} ${2:compareOp} ${3:Value})
```

