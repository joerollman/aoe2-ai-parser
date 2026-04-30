# `up-set-target-object`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-set-target-object"></a>

## `up-set-target-object`

- Kind: `command`
- Detail: Fact/Action - DUC

Syntax: `(up-set-target-object <SearchSource> <typeOp> <Index>)`

Set the target object for other commands from your search. Reference it with up-get-point and position-object. If the Index is invalid, the current target object will remain unchanged. This command can be used as either a Fact or an Action.

[AIRef](https://airef.github.io/commands/commands-details.html#up-set-target-object)

Completion insert text:

```text
(up-set-target-object ${1:SearchSource} ${2:typeOp} ${3:Index})
```

