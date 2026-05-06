# `set-escrow-percentage`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-set-escrow-percentage"></a>

## `set-escrow-percentage`

- Kind: `command`
- Detail: Action - Economy

Syntax: `(set-escrow-percentage <Resource> <Value>)`

Sets the computer player's escrow percentage for a given resource type. Given values have to be in the range 0-100. AIs can store each of their four resource stockpiles in one of two stockpile types: normal and escrow. Resources in the normal stockpiles are free for the AI to use, while resources in the escrow stockpiles can only be used with up-build, up-train, or up-research if the EscrowGoalId parameter in these commands is a goal set to the value "with-escrow". The user interface shows the sum of both the normal and escrow stockpile resources added together for each resource. By default, all resources are stored in the normal stockpiles. However, set-escrow-percentage and up-modify-escrow can be used to store some or all of the AI's resources in the escrow stockpiles instead. set-escrow-percentage sets the percentage of the resources a villager or fishing ship is carrying that will be stored in the escrow stockpile instead of the normal stockpile every time the villager or fishing ship drops off the resources they are carrying. For example, if a villager is dropping off 10 wood at the lumber camp and the wood escrow percentage is set to 30, then 3 of the 10 wood that is dropped off is stored in the wood escrow stockpile, while the remaining 7 wood is stored in the normal wood stockpile. set-escrow-percentage only applies to resources as they are dropped off. It does not immediately force a certain percentage of the total stockpile to be stored in escrow. For example, if the AI has 1000 gold, setting the gold escrow percentage to 20 does not mean that the AI will reallocate its gold stockpiles so that 200 gold will be in the gold escrow stockpile and 800 gold will be in the normal gold stockpile. If you want this behavior, you can use up-modify-escrow instead (see the examples section on the up-modify-escrow page on how to do this). Resources in the escrow stockpiles can transferred back into the normal stockpiles by using release-escrow, up-release-escrow, or up-modify-escrow. Resources are usually placed in escrow stockpiles in order to save up for expensive technologies or important buildings or units, so that it isn't spent on lower priority things. There is no command that can check the current escrow percentage, so if you want to check the current escrow percentage, you'll need to store this percentage in a goal or an unused strategic number when you use set-escrow-percentage.

[AIRef](https://airef.github.io/commands/commands-details.html#set-escrow-percentage)

Completion insert text:

```text
(set-escrow-percentage ${1:Resource} ${2:Value})
```

