# `fe-cc-effect-amount`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-fe-cc-effect-amount"></a>

## `fe-cc-effect-amount`

- Kind: `command`
- Detail: Action - Cheat, Scenarios

Syntax: `(fe-cc-effect-amount <EffectId> <ItemId> <AttrId> <Value>)`

DE only. Apply a research-style effect with an integer value for the AI player. This is considered a cheat command, but cheats do not have to be enabled. When modifying objects, you may need to target ALL hidden variations, one-by-one, as well. Please consider in-game object upgrades, so that an upgrade will not push a unit's max hitpoints over 32768 or the object will be destroyed. If you disable an object with this command, in-game techs/ages (unless disabled) may re-enable them. The civ tech tree may also override changes. This command can only use integer values. If you need to make an effect with a decimal value, use fe-cc-effect-percent.

[AIRef](https://airef.github.io/commands/commands-details.html#fe-cc-effect-amount)

Completion insert text:

```text
(fe-cc-effect-amount ${1:EffectId} ${2:ItemId} ${3:AttrId} ${4:Value})
```

