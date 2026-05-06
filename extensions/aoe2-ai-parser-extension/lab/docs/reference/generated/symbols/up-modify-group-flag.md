# `up-modify-group-flag`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-modify-group-flag"></a>

## `up-modify-group-flag`

- Kind: `command`
- Detail: Action - DUC, DUC Groups

Syntax: `(up-modify-group-flag <Option> <typeOp> <GroupId>)`

Modify the control group flag for units in a search group. You must manage the group flag carefully in order to avoid unexpected situations. Please remove the group flag before modifying a flagged search group. You can find units from a flagged search group using object-data-group-flag, which is set to the group id. Because this command modifies the object-data-group-flag of the units themselves, AI scripters must ensure that objects owned by other players are not stored in the AI's search group before using this command. This can occur if a unit in search group is converted and now belongs to another player, and the AI scripter doesn't include code to remove converted units from the AI's search groups during each script pass. Changing the control group flag of other players' units, even accidentally, is considered cheating in AI tournaments.

[AIRef](https://airef.github.io/commands/commands-details.html#up-modify-group-flag)

Completion insert text:

```text
(up-modify-group-flag ${1:Option} ${2:typeOp} ${3:GroupId})
```

