# `sn-enable-training-queue`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-sn-enable-training-queue"></a>

## `sn-enable-training-queue`

- Kind: `strategic-number`
- Detail: SN 264 - Economy

Set to values > 0 to allow an additional unit(s) to be queued at each building. For example, if set to 3, then 3 units can be queued to be trained after the currently training unit. If set to 0, buildings will train one unit at a time. By default, technologies can't be queued. To enable queued technologies in DE, set sn-enable-research-queue to 1, and technologies will use sn-enable-training-queue as well.

Default: `0`

Required range: `0 to 15`

Range: `Min to Max`

[AIRef](https://airef.github.io/strategic-numbers/sn-details.html#sn-enable-training-queue)

