# `set-difficulty-parameter`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-set-difficulty-parameter"></a>

## `set-difficulty-parameter`

- Kind: `command`
- Detail: Action - SNs

Syntax: `(set-difficulty-parameter <DiffParameterId> <Value>)`

Sets a given difficulty parameter to a given value. Difficulty parameters are similar to strategic numbers. There are two difficulty parameters that can be set: ability-to-maintain-distance or ability-to-dodge-missiles. Both have a range from 0 to 100, and the values have the opposite effect from what you'd expect! Setting a difficulty parameter to 0 completely enables the difficulty parameter behavior, and setting a difficulty parameter to 100 disables it. It isn't possible to check the current value of each difficulty parameter. Descriptions of each difficulty parameter:ability-to-maintain-distance: Chance that a computer player's ranged unit will maintain the distance. Range is 0-100, and the values are opposite from what you'd expect! When set to 0, ranged units will frequently move back to maintain distance. When set to 100, ranged units will not move back. However, this behavior only works on units are not following a move, patrol, or attack move command and are simply using their automatic attacking behavior. Setting snEnablePatrolAttack may also disable this behavior.ability-to-dodge-missiles: Chance of a computer player's unit dodging a missile. Range is 0-100, and the values are opposite from what you'd expect! When set to 0, units will try to dodge immediately upon seeing a projectile in the air. When set to 100, they have to hit first to react. Projectiles from siege-weapon-class and unpacked-trebuchet-class (913 and 954, not including scorpions) are always dodged, no matter what this parameter is set to. Note that while setting this to 0 might seem obvious, it may prove better to experiment especially depending on what enemy units you are facing and what units you are producing. For example, navy units have turn rates and so can suffer.

[AIRef](https://airef.github.io/commands/commands-details.html#set-difficulty-parameter)

Completion insert text:

```text
(set-difficulty-parameter ${1:DiffParameterId} ${2:Value})
```

