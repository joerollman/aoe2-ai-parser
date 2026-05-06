# `sn-percent-attack-soldiers`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-sn-percent-attack-soldiers"></a>

## `sn-percent-attack-soldiers`

- Kind: `strategic-number`
- Detail: SN 227 - Attack

Sets the percentage of defense soldiers that will be sent into battle (modified for difficulty level) the next time attack-now is issued. All newly created soldiers are defense soldiers by default, and will remain defense soldiers until attack-now is issued. For example, if 10 soldiers were defending a town, and sn-percent-attack-soldiers was set to 50, then 5 soldiers will form an attack group and attack. This SN only needs to be set once, but it can be changed as needed. sn-percent-attack-soldiers works best when not using archived-non-de-strategic-number.

Default: `75`

Required range: `0 to 100`

Range: `Min to Max`

[AIRef](https://airef.github.io/strategic-numbers/sn-details.html#sn-percent-attack-soldiers)

