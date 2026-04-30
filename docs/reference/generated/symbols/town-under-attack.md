# `town-under-attack`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-town-under-attack"></a>

## `town-under-attack`

- Kind: `command`
- Detail: Fact - Defense

Syntax: `(town-under-attack)`

town-under-attack is triggered (i.e. returns true) if any unit/building belonging to the computer player that is inside snMaximumTownSize gets attacked. It lasts 1 to 10 in-game seconds after the attack. It is not triggered by attacks to buildings or villagers that are outside sn-maximum-town-size. This command detects ally attackers. Because town-under-attack detects any attack events within sn-maximum-town-size, it can sometimes trigger town-under-attack in conditions when a human player wouldn't consider the town under attack, such as if a wolf attacks a villager or an enemy scout attacks a villager while exploring. Most importantly, town-under-attack can trigger when the AI is using TSA to attack the enemy, since sn-maximum-town-size is large enough to detect attack events that occur in the enemy's town, so use town-under-attack with care.

[AIRef](https://airef.github.io/commands/commands-details.html#town-under-attack)

Completion insert text:

```text
(town-under-attack)
```

