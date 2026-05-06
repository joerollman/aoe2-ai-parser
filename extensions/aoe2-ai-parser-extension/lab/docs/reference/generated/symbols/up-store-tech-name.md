# `up-store-tech-name`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-store-tech-name"></a>

## `up-store-tech-name`

- Kind: `command`
- Detail: Action - Techs, Text Data

Syntax: `(up-store-tech-name <typeOp> <TechId>)`

Store a research tech name in the internal buffer. The buffer can be referenced by the chat-data commands using %s instead of %d with c: 7031232 (7031232 cannot be stored in a defconst). This buffer is shared by all AIs, so please store data before using it in a rule pass. You can also use my-unique-research, which will usually get the imperial age unique tech for the civilization, and you can also use my-second-unique-research, which will usually get the castle age unique tech for the civilization. The excepts are the Britons, Franks, Goths, and Saracens, whose my-unique-research and my-second-unique-research are switched.

[AIRef](https://airef.github.io/commands/commands-details.html#up-store-tech-name)

Completion insert text:

```text
(up-store-tech-name ${1:typeOp} ${2:TechId})
```

