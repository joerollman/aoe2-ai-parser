# `sn-disable-tower-priority`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-sn-disable-tower-priority"></a>

## `sn-disable-tower-priority`

- Kind: `strategic-number`
- Detail: SN 267 - Attack

Set to 1 to prevent the local targeting system from giving special priority to towers and other fortifications, including town centers and castles. If set to 0, these buildings will receive the usual special priority. In combination with sn-ignore-attack-group-under-attack:1, you can better avoid being lured by town centers during early attacks, though using retreat or DUC commands to avoid town centers will be more effective overall. Note: this sn requires a packet to be sent for each change in a multiplayer game, so please consider this when using it.

Default: `0`

Required range: `0 to 1`

Range: `Min to Max`

[AIRef](https://airef.github.io/strategic-numbers/sn-details.html#sn-disable-tower-priority)

