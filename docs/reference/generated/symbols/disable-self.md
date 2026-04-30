# `disable-self`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-disable-self"></a>

## `disable-self`

- Kind: `command`
- Detail: Action - Other

Syntax: `(disable-self)`

Disables the rule that it is part of so that the rule is never run again. Since disabling takes effect in the next execution pass, other actions in the same rule are still executed once. Use this whenever you only want the rule to run once and never again. Rules disabled with a disable-self command are never read again, but they are still counted as rules by commands that jump over rules like up-jump-rule or up-jump-dynamic.

[AIRef](https://airef.github.io/commands/commands-details.html#disable-self)

Completion insert text:

```text
(disable-self)
```

