# `fe-cc-effect-percent`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-fe-cc-effect-percent"></a>

## `fe-cc-effect-percent`

- Kind: `command`
- Detail: Action - Cheat, Scenarios

Syntax: `(fe-cc-effect-percent <EffectId> <ItemId> <AttrId> <Percent>)`

DE only. Apply a research-style effect as a percentage for the AI player. This command is identical to fe-cc-effect-amount, except the value is divided by 100 to provide decimal precision. This is considered a cheat command, but cheats do not have to be enabled. When modifying objects, you may need to target ALL hidden variations, one-by-one, as well. Please consider in-game object upgrades, so that an upgrade will not push a unit's max hitpoints over 32768 or the object will be destroyed. If you disable an object with this command, in-game techs/ages (unless disabled) may re-enable them. The civ tech tree may also override changes. This command can only use integer values.

[AIRef](https://airef.github.io/commands/commands-details.html#fe-cc-effect-percent)

Completion insert text:

```text
(fe-cc-effect-percent ${1:EffectId} ${2:ItemId} ${3:AttrId} ${4:Percent})
```

