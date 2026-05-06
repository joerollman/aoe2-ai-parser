# `doctrine`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-doctrine"></a>

## `doctrine`

- Kind: `command`
- Detail: Fact - Goals

Syntax: `(doctrine <Value>)`

Checks what the current doctrine is, similar to checking the value of a goal. The doctrine is always an integer value which is set with the set-doctrine command, and the doctrine command simply checks if the doctrine is currently equal to the given value. Unlike goals, there is only one doctrine that you can set, and you can only use the doctrine command to check if the doctrine is currently equal to the given value, not less than, or greater than, or any other type of comparison. In all cases, using goals instead of the doctrine will give you more flexibility, but if you run out of available goals then you can use the doctrine like an extra goal if you need it. The doctrine starts with the value of -1 at the beginning of the game, and it only changes if you use the set-doctrine command.

[AIRef](https://airef.github.io/commands/commands-details.html#doctrine)

Completion insert text:

```text
(doctrine ${1:Value})
```

