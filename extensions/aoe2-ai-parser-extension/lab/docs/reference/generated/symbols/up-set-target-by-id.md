# `up-set-target-by-id`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-set-target-by-id"></a>

## `up-set-target-by-id`

- Kind: `command`
- Detail: Fact/Action - DUC

Syntax: `(up-set-target-by-id <typeOp> <Id>)`

Set the target object for other commands by id. Reference it with up-get-point and position-object. If the Id is invalid, the current target object will remain unchanged. This command can be used as either a Fact or an Action.

[AIRef](https://airef.github.io/commands/commands-details.html#up-set-target-by-id)

Completion insert text:

```text
(up-set-target-by-id ${1:typeOp} ${2:Id})
```

