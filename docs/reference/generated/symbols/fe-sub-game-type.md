# `fe-sub-game-type`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-fe-sub-game-type"></a>

## `fe-sub-game-type`

- Kind: `command`
- Detail: Fact - Game Info

Syntax: `(fe-sub-game-type <compareOp> <SubGameType>)`

DE only. Checks if game matches the specified sub-game type. There are four sub-game types: sub-game-type-empire-wars, sub-game-type-sudden-death, sub-game-type-regicide, and sub-game-type-king-of-the-hill. Sub-games are loaded whenever the checkbox for these sub-game modes are checked in the lobby screen, rather than being selected from the game type dropdown. Multiple sub-games modes can be true at once in a game.

[AIRef](https://airef.github.io/commands/commands-details.html#fe-sub-game-type)

Completion insert text:

```text
(fe-sub-game-type ${1:compareOp} ${2:SubGameType})
```

