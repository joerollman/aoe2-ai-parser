# `do-nothing`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-do-nothing"></a>

## `do-nothing`

- Kind: `command`
- Detail: Action - Other

Syntax: `(do-nothing)`

Does nothing. Used as a placeholder action if you don't want a rule to have any actions. Every rule must have at least one fact and one action. In rare cases where you don't want to include any actions in your rule, use do-nothing as a placeholder to fulfill the one action requirement. One of these rare cases is when you want to temporarily comment out all the actions in your rule for testing purposes but you want to keep the facts section of your rule. Unlike disable-self do-nothing will not stop the rule from being checked each pass.

[AIRef](https://airef.github.io/commands/commands-details.html#do-nothing)

Completion insert text:

```text
(do-nothing)
```

