# `sn-enable-offensive-priority`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-sn-enable-offensive-priority"></a>

## `sn-enable-offensive-priority`

- Kind: `strategic-number`
- Detail: SN 254 - Attack

Set to 1 to enable attack-now and attack groups to target using the priorities set by up-set-offense-priority. This SN is turned off by default, so the SN should be changed to 1. Using up-set-offense-priority allows you to control which buildings and units have lower and higher priority when the AI is selecting an attack target. If you don't set sn-enable-offensive-priority to 1, up-set-offense-priority will have no effect. up-set-defense-priority does not have a corresponding strategic number that you need to set to 1 for the command to work, just up-set-offense-priority.

Default: `0`

Required range: `0 to 1`

Range: `Min to Max`

[AIRef](https://airef.github.io/strategic-numbers/sn-details.html#sn-enable-offensive-priority)

