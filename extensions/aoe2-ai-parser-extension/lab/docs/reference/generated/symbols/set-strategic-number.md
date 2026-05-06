# `set-strategic-number`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-set-strategic-number"></a>

## `set-strategic-number`

- Kind: `command`
- Detail: Action - SNs

Syntax: `(set-strategic-number <SnId> <Value>)`

Sets a given strategic number to a given value. See the Strategic Numbers section for more info on each strategic number. Each strategic number has a different default value, which you can also check on the SN Index page. Each SN is given an ID between 0 and 511. Currently, the SNs in the 313-511 range don't appear in the SN index and don't modify the behavior of your AI, but they are available for your AI to use. So, you can modify these SNs however you like, similar to goals, without changing the behavior of your AI. However, if you want to use a strategic number in this way like an extra custom goal, always check the SN index to make sure that the SN ID you are using is actually currently unused. A good practice is to start with using SN 510 (SN 511 might have some bugs in DE) and work your way backwards toward SNs in the 300 range.

[AIRef](https://airef.github.io/commands/commands-details.html#set-strategic-number)

Completion insert text:

```text
(set-strategic-number ${1:SnId} ${2:Value})
```

