# `sn-dock-training-filter`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-sn-dock-training-filter"></a>

## `sn-dock-training-filter`

- Kind: `strategic-number`
- Detail: SN 281 - Water

Set to 1 or 2 to enable the intelligent dock training filter. This will prevent docks from training ships that would likely be useless in their body of water. If set to 1, docks will continue to train in seas that no longer contain recently sighted targets, while 2 will block training. If set to 0, docks will train units without additional consideration. When sn-dock-training-filter is not 0, fishing ships will only be trained from docks that are able to reach, and are closest to, deep sea fish. This means that if you have 4 docks in an ocean with deep sea fish, side by side, the two outside docks are likely to be set aside to train fishing ships, while the center docks will be free to create warships without interruption. If you aren't training fishing ships, the two outside docks will also be able to train warships, of course. Additionally, when sn-dock-training-filter is not 0, trade cogs may be rejected by the dock if it hasn't found an allied dock in the same sea that could be reached from it. On the other hand, a military ship uses enemy ships/docks to determine if it is acceptable when that sn is in use. Here is some sample code from scripter64 to set sn-dock-training-filter to the best possible state: (defrule (true) => (set-strategic-number sn-dock-training-filter 0) (set-goal gl-dock-attack-training 0) ) (defrule (up-train-site-ready c: galley) => (chat-to-all "A dock is available to train warships.") (set-strategic-number sn-dock-training-filter 2) (set-goal gl-dock-attack-training 1) ) (defrule (goal gl-dock-attack-training 1) (not(up-train-site-ready c: galley)) => (chat-to-all "A dock is not available to train warships with recent sighting data.") (set-strategic-number sn-dock-training-filter 1) ) (defrule (goal gl-dock-attack-training 1) (not(up-train-site-ready c: galley)) => (chat-to-all "A dock is not available to train warships with any sighting data.") (set-strategic-number sn-dock-training-filter 0) ) ;sn-dock-training-filter is now set to the best possible state

Default: `0`

Required range: `0 to 2`

Range: `Min to Max`

[AIRef](https://airef.github.io/strategic-numbers/sn-details.html#sn-dock-training-filter)

