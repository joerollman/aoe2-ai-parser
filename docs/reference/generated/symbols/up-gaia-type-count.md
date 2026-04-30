# `up-gaia-type-count`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-gaia-type-count"></a>

## `up-gaia-type-count`

- Kind: `command`
- Detail: Fact - Counting, Economy

Syntax: `(up-gaia-type-count <typeOp> <Resource> <compareOp> <Value>)`

Check the current sighted resource count from gaia. This command may be relatively slow, since it must check the status of all discovered resources within the requested subset (food, wood, stone, or gold). This command does not work with relics.

[AIRef](https://airef.github.io/commands/commands-details.html#up-gaia-type-count)

Completion insert text:

```text
(up-gaia-type-count ${1:typeOp} ${2:Resource} ${3:compareOp} ${4:Value})
```

