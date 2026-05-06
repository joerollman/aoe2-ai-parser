# `up-remaining-boar-amount`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-remaining-boar-amount"></a>

## `up-remaining-boar-amount`

- Kind: `command`
- Detail: Fact - Economy

Syntax: `(up-remaining-boar-amount <compareOp> <Value>)`

Check the amount of food remaining on the current boar. This data is only valid if the boar is lured with strategic numbers (not Direct Unit Control), while another boar is targetable and available to hunt. If this is not the case, it remains invalid (65535) to signify that this is the final boar.

[AIRef](https://airef.github.io/commands/commands-details.html#up-remaining-boar-amount)

Completion insert text:

```text
(up-remaining-boar-amount ${1:compareOp} ${2:Value})
```

