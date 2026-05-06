# `sn-preferred-storage-pit-placement`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-sn-preferred-storage-pit-placement"></a>

## `sn-preferred-storage-pit-placement`

- Kind: `strategic-number`
- Detail: SN 311 - Buildings

Controls the preferred resource the AI will place its storage pits nearby. Return of Rome DLC only. Currently this SN seems bugged, but the following values are what is supposed to work. Setting the SN to -1 seems to currently work for placing storage pits near wood.(defconst storage-pit-default -1)(defconst storage-pit-forage 0)(defconst storage-pit-hunting 1)(defconst storage-pit-fishing 2)(defconst storage-pit-wood 3)(defconst storage-pit-gold 4)(defconst storage-pit-stone 5)

Default: `-1`

Required range: `-1 to 5`

Range: `Min to Max`

[AIRef](https://airef.github.io/strategic-numbers/sn-details.html#sn-preferred-storage-pit-placement)

