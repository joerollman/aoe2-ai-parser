# `up-store-object-name`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-store-object-name"></a>

## `up-store-object-name`

- Kind: `command`
- Detail: Action - Buildings, Text Data, Units

Syntax: `(up-store-object-name)`

Store the target object's type name in the internal buffer. The buffer can be referenced by the chat-data commands using %s instead of %d with c: 7031232 (7031232 cannot be stored in a defconst). This buffer is shared by all AIs, so please store data before using it in a rule pass.

[AIRef](https://airef.github.io/commands/commands-details.html#up-store-object-name)

Completion insert text:

```text
(up-store-object-name)
```

