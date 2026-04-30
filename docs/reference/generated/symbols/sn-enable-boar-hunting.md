# `sn-enable-boar-hunting`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-sn-enable-boar-hunting"></a>

## `sn-enable-boar-hunting`

- Kind: `strategic-number`
- Detail: SN 244 - Economy

Set to 1 to target deer and boar; if it's set to 2, deer will be ignored. Keep sn-enable-boar-hunting at the default setting of 0 to target deer and ignore boar. To ignore both deer and boar, set sn-minimum-number-hunters to 0, and set sn-maximum-hunt-drop-distance to -2. This SN's default value is 0, which is usually not the value you want. Make sure to change the setting of this SN if you want your AI to hunt boar. The recommended setting is 1 when you are just starting to script so that your AI doesn't ignore free and valuable food resources. Hunting is one of the fastest sources of food. See this page for examples on how different SN hunting values affects your hunting.

Default: `0`

Required range: `0 to 2`

Range: `Min to Max`

[AIRef](https://airef.github.io/strategic-numbers/sn-details.html#sn-enable-boar-hunting)

