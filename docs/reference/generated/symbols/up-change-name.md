# `up-change-name`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-change-name"></a>

## `up-change-name`

- Kind: `command`
- Detail: Action - Other

Syntax: `(up-change-name <String>)`

Change the name of the AI during gameplay. When you use (up-change-name -1), the AI's name will be set to one of that civilization's first 8 built-in historical names in an semi-random manner, same as the names used in the default AI. The name is guaranteed to be unique among other AIs that use this command, but not necessarily with Petersen's selection.

[AIRef](https://airef.github.io/commands/commands-details.html#up-change-name)

Completion insert text:

```text
(up-change-name ${1:String})
```

