# `enemy-captured-relics`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-enemy-captured-relics"></a>

## `enemy-captured-relics`

- Kind: `command`
- Detail: Fact - Game Info

Syntax: `(enemy-captured-relics)`

Checks if the enemy team has captured all relics. When this happens, tactical AI automatically starts targeting monasteries and monks. Use this fact to intensify attacks and combine it with the attack-now action to force attacks. You can also add snSpecialAttackType1 to 1, snSpecialAttackInfluence1 > 0, and up-set-offense-priority for monasteries to a high number to increase the likelyhood to target monasteries.

[AIRef](https://airef.github.io/commands/commands-details.html#enemy-captured-relics)

Completion insert text:

```text
(enemy-captured-relics)
```

