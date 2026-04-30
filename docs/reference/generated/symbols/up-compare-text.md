# `up-compare-text`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-compare-text"></a>

## `up-compare-text`

- Kind: `command`
- Detail: Fact - Text Data

Syntax: `(up-compare-text <typeOp> <Defconst> <compareOp> <Value>)`

Perform a string comparison with the stored text. You must store text before using this command and the provided Defconst must be a text defconst. If the provided string cannot be found anywhere in the stored text, the value will be -1. Otherwise, the value will be the index of the match.

[AIRef](https://airef.github.io/commands/commands-details.html#up-compare-text)

Completion insert text:

```text
(up-compare-text ${1:typeOp} ${2:Defconst} ${3:compareOp} ${4:Value})
```

