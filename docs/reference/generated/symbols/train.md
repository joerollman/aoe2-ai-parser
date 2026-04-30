# `train`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-train"></a>

## `train`

- Kind: `command`
- Detail: Action - Units

Syntax: `(train <UnitId>)`

Trains the given unit if the unit is available to the player and the unit can be trained without escrowed resources. In order to use escrow resources, they must be released with release-escrow, up-release-escrow, or up-modify-escrow. To prevent cheating, this action uses the same criteria as the can-train fact to make sure the unit can be trained. It also checks When possible, use unit lines with this command. my-unique-unit, my-elite-unique-unit, and my-unique-unit-line can also be used, which will automatically get the UnitId of the unique unit, elite unique unit, or unique unit line that the AI's civ can train from the castle. You can also train by the unit ID rather than the unit name. You can see all units and their unit IDs in the Objects table. You cannot use unit classes or unit sets, like huskarl-set. To train units which can be trained at multiple buildings, like huskarls, tarkans, konniks, and serjeants, you must use a separate unit type or unit line to train them from their non-castle building. Look up these units in the Objects Table for more information. To train mercenary kipchaks (elite kipchaks that allies can train after Cuman Mercenaries is researched), use "mercenary-kipchak" rather than kipchak-line. In WK, there are two units that use a separate placeholder unit ID for training purposes, and you must use it for all train, can-train-with-escrow, train, up-can-train, and up-train commands. These units are the condottiero and genitour. Use ID 184 for condottiero-placeholder and use ID 732 for genitour-placeholder.The AI engine will automatically pick the building with the least number of queued units and techs to train the unit, and if there are multiple equally available buildings, the AI will pick one of those buildings at random. To pick a particular building or buildings on the map to train the unit, use a DUC search to put those buildings in the local list and use the up-target-point command with the action-train action to order the buildings to train the unit. See the up-target-point page for an example. Interestingly, you can safely use the base unit of a unit line with this command instead of the unit line version, and it will work regardless of any upgrades that have been researched. For example, you can safely use (train archer) even if Crossbowman has been researched. This capability is important if you are scripting for WololoKingdoms (WK) or any other mod where some unit lines aren't defined in the AI engine. The setting of snDockTrainingFilter affects the ability for docks to train warships with this command. The fact allows the use of unit line wildcard parameters for pUnitId.

[AIRef](https://airef.github.io/commands/commands-details.html#train)

Completion insert text:

```text
(train ${1:UnitId})
```

