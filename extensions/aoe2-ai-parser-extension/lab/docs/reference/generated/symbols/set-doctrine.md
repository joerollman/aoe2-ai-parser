# `set-doctrine`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-set-doctrine"></a>

## `set-doctrine`

- Kind: `command`
- Detail: Action - Goals

Syntax: `(set-doctrine <Value>)`

Sets the doctrine to the given value, similar to setting the value of a goal. The doctrine is always an integer value and you can check if the doctrine is set to a given value with the doctrine" command. Unlike goals, there is only one doctrine that you can set, and you can only use the set-doctrine command to set the doctrine to a specific value. You can't dynamically set the doctrine to equal the value of a goal or strategic number, like you can with goals. In all cases, using goals instead of the doctrine will give you more flexibility, but if you run out of available goals then you can use the doctrine like an extra goal if you need it. The doctrine starts with the value of -1 at the beginning of the game, and it only changes if you use the set-doctrine command." cSetDoctrine.commandParameters = [ { nameLink: pValue.getLink(), name: "Value", type: "Const", dir: "in", range: "-2,147,483,648 to 2,147,483,647.", note: "The value to set the doctrine to." } ]

[AIRef](https://airef.github.io/commands/commands-details.html#set-doctrine)

Completion insert text:

```text
(set-doctrine ${1:Value})
```

