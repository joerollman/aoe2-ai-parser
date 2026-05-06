# `up-retreat-now`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-retreat-now"></a>

## `up-retreat-now`

- Kind: `command`
- Detail: Action - Attack

Syntax: `(up-retreat-now)`

Retreat all military units to the home town center. Military units within 6 range of the home town center will not be told to retreat. Active explorers will not retreat. If explorers need to retreat, use up-reset-scouts before using this command. It should work with groups and idle units. There's a chance that you may need to disband attack groups before using it, though, by setting the attack group sns to 0 (sn-number-attack-groups, min, and max). It will also work with TSA units, unless an enemy building exists in max-town-size. In that case, TSA overrides the retreat, I think, and resends them to the target. It should also work with attack-now if you use up-reset-attack-now before using up-retreat-now.

[AIRef](https://airef.github.io/commands/commands-details.html#up-retreat-now)

Completion insert text:

```text
(up-retreat-now)
```

