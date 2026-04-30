# `up-update-targets`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-update-targets"></a>

## `up-update-targets`

- Kind: `command`
- Detail: Action - Attack, Defense

Syntax: `(up-update-targets)`

Perform an immediate update for objects in town size. This command is important when using TSA. If you expand town size, new targets inside sn-maximum-town-size are quickly added into the target list (the list of enemy objects within sn-maximum-town-size). However, if you reduce sn-maximum-town-size, you have to wait until the target refresh for these objects to be removed from the target list, which happens every 15 seconds. This can cause issues with retreating, for example. Using up-update-targets will immediately update the target list, resolving the issue.

[AIRef](https://airef.github.io/commands/commands-details.html#up-update-targets)

Completion insert text:

```text
(up-update-targets)
```

