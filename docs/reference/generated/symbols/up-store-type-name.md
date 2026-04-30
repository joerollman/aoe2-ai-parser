# `up-store-type-name`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-store-type-name"></a>

## `up-store-type-name`

- Kind: `command`
- Detail: Action - Buildings, Text Data, Units

Syntax: `(up-store-type-name <typeOp> <TypeId>)`

Store an object type name in the internal buffer. The buffer can be referenced by the chat-data commands using %s instead of %d with c: 7031232 (7031232 cannot be stored in a defconst). This buffer is shared by all AIs, so please store data before using it in a rule pass.

[AIRef](https://airef.github.io/commands/commands-details.html#up-store-type-name)

Completion insert text:

```text
(up-store-type-name ${1:typeOp} ${2:TypeId})
```

