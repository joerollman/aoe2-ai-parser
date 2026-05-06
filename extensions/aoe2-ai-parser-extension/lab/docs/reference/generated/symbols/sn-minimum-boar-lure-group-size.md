# `sn-minimum-boar-lure-group-size`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-sn-minimum-boar-lure-group-size"></a>

## `sn-minimum-boar-lure-group-size`

- Kind: `strategic-number`
- Detail: SN 252 - Economy

Set to the number of villagers that will be sent in the initial boar luring group. The initial luring group size is determined exclusively by sn-minimum-boar-lure-group-size. If this is set excessively high, luring a new boar will be blocked, which is useful to ensure that all new hunters will help with an existing lure only. If sn-minimum-boar-lure-group-size is set to 0, a new boar lure is guaranteed to start if sn-minimum-number-hunters requests at least 1 hunter and sn-enable-boar-hunting is set appropriately. The sn-minimum-boar-hunt-group-size value is used only to determine how many hunters should be active during a lure. Each time a lurer is hit, it will try to request up to sn-minimum-boar-hunt-group-size hunters in total to help with the hunt. If it's set to 7, for example, it will request support hunters until there are 7 total hunters. After it is down, each boar will accept a maximum of 8 gatherers. The 9th will have to seek a new boar, if sn-minimum-boar-lure-group-size permits it.

Default: `0`

Required range: `0 to 8`

Range: `Min to Max`

[AIRef](https://airef.github.io/strategic-numbers/sn-details.html#sn-minimum-boar-lure-group-size)

