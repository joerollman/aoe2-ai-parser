# `up-get-treaty-data`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-get-treaty-data"></a>

## `up-get-treaty-data`

- Kind: `command`
- Detail: Action - Diplomacy, Game Info

Syntax: `(up-get-treaty-data <OutputGoalId>)`

DE only. Stores the remaining treaty time in seconds into a goal. Treaty time is the amount of time left in treaty games where players cannot attack each other.

[AIRef](https://airef.github.io/commands/commands-details.html#up-get-treaty-data)

Completion insert text:

```text
(up-get-treaty-data ${1:OutputGoalId})
```

