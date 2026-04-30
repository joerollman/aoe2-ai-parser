# `fe-idle-pasture-count`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-fe-idle-pasture-count"></a>

## `fe-idle-pasture-count`

- Kind: `command`
- Detail: Fact - Counting, Economy

Syntax: `(fe-idle-pasture-count <compareOp> <Value>)`

DE only. Checks the number of pastures with zero herders gathering from it. It can be used before a new pasture is built to make sure it is needed. To check the number of idle farms, use idle-farm-count.

[AIRef](https://airef.github.io/commands/commands-details.html#fe-idle-pasture-count)

Completion insert text:

```text
(fe-idle-pasture-count ${1:compareOp} ${2:Value})
```

