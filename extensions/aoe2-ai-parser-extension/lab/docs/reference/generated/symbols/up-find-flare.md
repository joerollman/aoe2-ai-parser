# `up-find-flare`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-find-flare"></a>

## `up-find-flare`

- Kind: `command`
- Detail: Action - Other Player Info, Points

Syntax: `(up-find-flare <Point>)`

Read the (x,y) position of an allied flare into an extended goal pair. This command writes to 2 consecutive goals and requires an extended goal pair between 41 and 15998. If it fails to get a valid position, it will return (-1,-1). This command is equivalent to up-find-player-flare with any-ally.

[AIRef](https://airef.github.io/commands/commands-details.html#up-find-flare)

Completion insert text:

```text
(up-find-flare ${1:Point})
```

