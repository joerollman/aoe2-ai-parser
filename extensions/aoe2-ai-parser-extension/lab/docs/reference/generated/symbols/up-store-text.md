# `up-store-text`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-store-text"></a>

## `up-store-text`

- Kind: `command`
- Detail: Action - Text Data

Syntax: `(up-store-text <typeOp> <LanguageId>)`

Store a language string in the internal buffer. The buffer can be referenced by the chat-data commands using %s instead of %d with c: 7031232 (7031232 cannot be stored in a defconst). This buffer is shared by all AIs, so please store data before using it in a rule pass.

[AIRef](https://airef.github.io/commands/commands-details.html#up-store-text)

Completion insert text:

```text
(up-store-text ${1:typeOp} ${2:LanguageId})
```

