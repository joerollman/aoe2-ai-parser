# `up-compare-const`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-compare-const"></a>

## `up-compare-const`

- Kind: `command`
- Detail: Fact - Other

Syntax: `(up-compare-const <Defconst> <compareOp> <Value>)`

Perform a comparison with a constant value. A defconst that defines a string (quoted text) stores a string table index where the string is stored. Therefore, up-compare-const will compare against the string index of such a defconst, rather than the text itself.

[AIRef](https://airef.github.io/commands/commands-details.html#up-compare-const)

Completion insert text:

```text
(up-compare-const ${1:Defconst} ${2:compareOp} ${3:Value})
```

