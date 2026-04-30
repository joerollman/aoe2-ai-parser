# `sn-cap-civilian-gatherers`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-sn-cap-civilian-gatherers"></a>

## `sn-cap-civilian-gatherers`

- Kind: `strategic-number`
- Detail: SN 5 - Economy

Caps the number of gatherers allocated. Factored in after the percentage is calculated. Ignored when set to -1, meaning there is no cap on the number of gatherers. Unless this SN caps gatherers, all villagers who aren't exploring or building will start gathering resources so that they aren't idle. In virtually all cases this is what you want, so there usually isn't any reason to change this SN from the default -1 setting. sn-percent-civilian-gatherers does not affect the number of gatherers, so you can rely on this SN alone to determine the number of gatherers that your AI has.

Default: `-1`

Required range: `-1 to Max`

Range: `Min to Max`

[AIRef](https://airef.github.io/strategic-numbers/sn-details.html#sn-cap-civilian-gatherers)

